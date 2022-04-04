import os
import random
import sys
from multiprocessing import Process, freeze_support
from time import sleep


from keyboard import is_pressed
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from mike_simulator.config import load_configuration, cfg
from mike_simulator.server import MikeServer


def start_ftp(log_dir):
    load_configuration()
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(os.path.realpath(log_dir))
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((cfg.Network.server_bind_ip, 21), handler)
    server.serve_forever()


def main():
    from sys import platform
    if platform == "linux" or platform == "linux2":
        from elevate import elevate
        elevate(graphical=False)

    freeze_support()

    seed = random.randrange(sys.maxsize)
    #seed = value
    motor_data_loss_rng = random.Random(seed+2)
    print('Packet loss rng seed: {seed}')

    # Load configuration file
    load_configuration()

    if cfg.Network.simulate_ftp_server:
        ftp_server = Process(target=start_ftp, args=(cfg.Logging.log_dir, ))
        ftp_server.start()

    server = MikeServer(motor_data_loss_rng)
    server.start()

    while True:
        if is_pressed('f10'):
            sleep(1.0)
            continue

        server.wait_for_connection()
        try:
            server.main_loop()
        finally:
            print('Connection terminated')
            server.close_connection()

    ftp_server.join()


if __name__ == '__main__':
    main()
