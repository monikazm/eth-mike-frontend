import json
import random
import select
import socket
import sys
from dataclasses import asdict

from mike_simulator.config import load_configuration, cfg
from mike_simulator.datamodels import PatientResponse, ControlResponse
from mike_simulator.simulator import BackendSimulator
from mike_simulator.util import PrintUtil


def main():
    seed = random.randrange(sys.maxsize)
    #seed = value
    control_loss_rng = random.Random(seed)
    patient_loss_rng = random.Random(seed+1)
    motor_data_loss_rng = random.Random(seed+2)
    print(f'Packet loss rng seed: {seed}')

    # Load configuration file
    load_configuration()

    # Create sockets
    patient_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    patient_server.bind((cfg.Network.server_bind_ip, cfg.Network.patient_port))

    control_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_server.bind((cfg.Network.server_bind_ip, cfg.Network.control_port))

    data_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_dest = (cfg.Network.frontend_ip, cfg.Network.motor_data_port)

    print('Servers and client started')
    simulator = BackendSimulator()

    server_sockets = [patient_server, control_server]
    client_sockets = [data_client]
    while True:
        # Wait until at least one of the sockets is ready for receiving/sending
        receive_socks, send_socks, _ = select.select(server_sockets, client_sockets, [])
        for sock in receive_socks:
            if sock == patient_server:
                # Receive patient data from frontend and update simulator accordingly
                data, _ = patient_server.recvfrom(1024)
                data = PatientResponse(**json.loads(data.decode('utf-8')))
                if patient_loss_rng.random() >= cfg.Network.patient_packet_loss_rate:
                    simulator.update_patient_data(data)
                else:
                    PrintUtil.print_normally(f'!!! PACKET LOSS FOR {data} !!!')
            elif sock == control_server:
                # Receive control signal from frontend and update simulator accordingly
                data, _ = control_server.recvfrom(1024)
                data = ControlResponse(**json.loads(data.decode('utf-8')))
                if control_loss_rng.random() >= cfg.Network.control_packet_loss_rate:
                    simulator.update_control_data(data)
                else:
                    PrintUtil.print_normally(f'!!! PACKET LOSS FOR {data} !!!')
        for sock in send_socks:
            assert sock == data_client
            # Get updated motor state from simulator
            ms = simulator.get_motor_state()

            # Send new motor state to frontend
            if motor_data_loss_rng.random() >= cfg.Network.motor_data_packet_loss_rate:
                data_client.sendto(json.dumps(asdict(ms)).encode('utf-8'), data_dest)


if __name__ == '__main__':
    main()
