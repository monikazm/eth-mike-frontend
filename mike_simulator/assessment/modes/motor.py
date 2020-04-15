import math
import random
from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.datamodels import MotorState
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil, Timer


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    COUNTDOWN = 2
    USER_INPUT = 3

    FINISHED = -1


class MotorAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__(S.STANDBY)

        # Compute randomized list of 20 flexion/extension phases (10 each)
        self.phases = [True]*10 + [False]*10
        random.shuffle(self.phases)

        # Maximum velocity reached within phase
        self.v_max = 0

        # Used to simulate delays
        self.timer = Timer()

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutoMover] = None

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.STANDBY):
            # Select random phase (either flexion or extension)
            motor_state.Flexion = self.phases[motor_state.TrialNr]
            motor_state.TrialNr += 1

            # Set start and end position accordingly
            if motor_state.Flexion:
                (motor_state.StartingPosition, motor_state.TargetPosition) = (20.0, 60.0)
            else:
                (motor_state.StartingPosition, motor_state.TargetPosition) = (60.0, 20.0)
            if not motor_state.LeftHand:
                motor_state.StartingPosition *= -1.0
                motor_state.TargetPosition *= -1.0

            # Direct robot to move to starting position within 3 seconds
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            # Automatic movement towards starting position
            if motor_state.move_using(self.auto_mover).has_finished():
                self.timer.start(1.0)
                self.goto_state(S.COUNTDOWN)
        elif self.in_state(S.COUNTDOWN):
            # Display destination after 1 second
            if self.timer.has_finished():
                # Allow user movement for 4 seconds
                motor_state.TargetState = True
                input_handler.unlock_movement()
                self.timer.start(4.0)
                self.goto_state(S.USER_INPUT)
        elif self.in_state(S.USER_INPUT):
            if self.timer.is_active():
                # Compute new v_max and print current data
                v_current = input_handler.current_input_state.velocity
                self.v_max = max(math.fabs(v_current), self.v_max)
                PrintUtil.print_inplace(f'Current pos: {motor_state.Position:.3f}°, '
                                        f'speed: {math.fabs(v_current):.3f} [max: {self.v_max:.3f}] °/s')
            else:
                # Time is up, lock movement and wait for next probe to start (if any)
                motor_state.TargetState = False
                input_handler.lock_movement()
                self.v_max = 0.0
                if motor_state.TrialNr == len(self.phases):
                    self.goto_state(S.FINISHED)
                else:
                    self.goto_state(S.STANDBY)
