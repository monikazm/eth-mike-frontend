import random
import sys
from time import sleep

from keyboard import is_pressed

from mike_simulator.config import load_configuration
from mike_simulator.server import MikeServer


def main():
    seed = random.randrange(sys.maxsize)
    #seed = value
    motor_data_loss_rng = random.Random(seed+2)
    print(f'Packet loss rng seed: {seed}')

    # Load configuration file
    load_configuration()

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


if __name__ == '__main__':
    main()
