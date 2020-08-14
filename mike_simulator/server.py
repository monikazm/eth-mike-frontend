import select
import socket
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

import netstruct
from keyboard import is_pressed

from mike_simulator.config import cfg
from mike_simulator.datamodels import PatientResponse, ControlResponse
from mike_simulator.simulator import BackendSimulator
from mike_simulator.util.lab_view_serialization import unflatten_from_string, flatten_to_string


class MsgType(IntEnum):
    Invalid = 0
    PatientSelect = 1
    Control = 2


@dataclass
class MsgHeader:
    type: MsgType = MsgType.Invalid
    msg_len: int = 0
header_format = b'BH'
header_size = netstruct.minimum_size(header_format)


class MikeServer:
    def __init__(self, packet_loss_rng) -> None:
        # UDP socket for sending data to frontend
        self.data_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Frontend endpoint
        self.data_dest_endpoint = ('0.0.0.0', cfg.Network.motor_data_port)

        # Socket used to accept tcp connections
        self.server_socket: Optional[socket.socket] = None

        # TCP connection to frontend
        self.connection: Optional[socket.socket] = None

        self.packet_loss_rng = packet_loss_rng

        self.simulator = None

    def start(self):
        self.simulator = BackendSimulator()
        self.server_socket = socket.create_server((cfg.Network.server_bind_ip, cfg.Network.patient_port), backlog=1)

    def stop(self):
        self.server_socket.close()

    def wait_for_connection(self):
        print('Servers and client started, waiting for frontend to connect...')
        # Wait until frontend connects
        self.connection, (host_addr, port) = self.server_socket.accept()
        self.data_dest_endpoint = (host_addr, cfg.Network.motor_data_port)
        print('Frontend connected')

    def main_loop(self):
        while True:
            try:
                # Wait until at least one of the sockets is ready for receiving/sending
                receive_socks, send_socks, _ = select.select([self.connection], [self.data_client_socket], [])
                for _ in receive_socks:
                    header = self._recv_header()
                    if header.type == MsgType.Invalid:
                        # received invalid message (probably connection closed -> restart server)
                        return

                    data = self.connection.recv(header.msg_len)
                    #print(f"Received: 0x{data.hex()}")
                    if header.type == MsgType.PatientSelect:
                        # Receive patient data from frontend and update simulator accordingly
                        data = unflatten_from_string(data, PatientResponse)
                        self.connection.send('X'.encode('utf-8'))
                        self.simulator.update_patient_data(data)
                    elif header.type == MsgType.Control:
                        # Receive control signal from frontend and update simulator accordingly
                        data = unflatten_from_string(data, ControlResponse)
                        self.connection.send('X'.encode('utf-8'))
                        self.simulator.update_control_data(data)
                    else:
                        raise NotImplementedError(f'Message type {header.type} is currently not handled.')

                for sock in send_socks:
                    assert sock == self.data_client_socket
                    # Get updated motor state from simulator
                    ms = self.simulator.get_motor_state()

                    if is_pressed('f10'):
                        return

                    # Send new motor state to frontend
                    if self.packet_loss_rng.random() >= cfg.Network.motor_data_packet_loss_rate:
                        data = flatten_to_string(ms)
                        self.data_client_socket.sendto(data, self.data_dest_endpoint)
            except ConnectionError:
                return

    def _recv_header(self) -> MsgHeader:
        data = self.connection.recv(header_size)
        if data:
            data = netstruct.unpack(header_format, data)
            return MsgHeader(*data)
        else:
            return MsgHeader()

    def close_connection(self):
        self.connection.close()
        self.connection = None
