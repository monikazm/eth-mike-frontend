import random
import select
import socket
import sys

from mike_simulator.config import load_configuration, cfg
from mike_simulator.datamodels import PatientResponse, ControlResponse
from mike_simulator.simulator import BackendSimulator
from mike_simulator.util.lab_view_serialization import unflatten_from_string, flatten_to_string


def main():
    seed = random.randrange(sys.maxsize)
    #seed = value
    motor_data_loss_rng = random.Random(seed+2)
    print(f'Packet loss rng seed: {seed}')

    # Load configuration file
    load_configuration()

    data_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_dest = (cfg.Network.frontend_ip, cfg.Network.motor_data_port)

    # Create sockets
    patient_server = socket.create_server((cfg.Network.server_bind_ip, cfg.Network.patient_port), backlog=1)
    control_server = socket.create_server((cfg.Network.server_bind_ip, cfg.Network.control_port), backlog=1)

    while True:
        print('Servers and client started, waiting for frontend to connect...')

        # Wait until frontend connects
        patient_connection, _ = patient_server.accept()
        control_connection, _ = control_server.accept()
        print('Frontend connected')

        simulator = BackendSimulator()

        server_sockets = [patient_connection, control_connection]
        client_sockets = [data_client]
        try:
            while True:
                # Wait until at least one of the sockets is ready for receiving/sending
                receive_socks, send_socks, _ = select.select(server_sockets, client_sockets, [])
                for sock in receive_socks:
                    if sock == patient_connection:
                        # Receive patient data from frontend and update simulator accordingly
                        data = unflatten_from_string(patient_connection, PatientResponse, True)
                        simulator.update_patient_data(data)
                    elif sock == control_connection:
                        # Receive control signal from frontend and update simulator accordingly
                        data = unflatten_from_string(control_connection, ControlResponse, False)
                        simulator.update_control_data(data)
                for sock in send_socks:
                    assert sock == data_client
                    # Get updated motor state from simulator
                    ms = simulator.get_motor_state()

                    # Send new motor state to frontend
                    if motor_data_loss_rng.random() >= cfg.Network.motor_data_packet_loss_rate:
                        data = flatten_to_string(ms)
                        data_client.sendto(data, data_dest)
        except Exception:
            print('Connection terminated')
            pass


if __name__ == '__main__':
    main()
