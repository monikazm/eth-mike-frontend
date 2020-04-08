import select
import socket
import time

from datamodels import PatientResponse, ControlResponse
from simulator import BackendSimulator

# Everything is on localhost
UDP_IP = '127.0.0.1'

# Address at which the frontend is listening for the updated motor state
UDP_DATA_PORT = 6661
DATA_DEST = (UDP_IP, UDP_DATA_PORT)

# Addresses at which the simulator should listen for commands and patient data
UDP_PATIENT_PORT = 6662
UDP_CONTROL_PORT = 6664


def main():
    # Create sockets
    patient_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    patient_server.bind((UDP_IP, UDP_PATIENT_PORT))

    control_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_server.bind((UDP_IP, UDP_CONTROL_PORT))

    data_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
                data = PatientResponse.from_json(data.decode('utf-8'))
                simulator.update_patient_data(data)
            elif sock == control_server:
                # Receive control signal from frontend and update simulator accordingly
                data, _ = control_server.recvfrom(1024)
                data = ControlResponse.from_json(data.decode('utf-8'))
                simulator.update_control_data(data)
        for sock in send_socks:
            assert sock == data_client
            # Get updated motor state from simulator
            state = simulator.get_motor_state().to_json()

            # Send new motor state to frontend
            data_client.sendto(state.encode('utf-8'), DATA_DEST)

            # Wait 30ms (TODO adjust this to actual robot update interval)
            time.sleep(0.03)


if __name__ == '__main__':
    main()
