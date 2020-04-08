import math
import random
import time
from enum import IntEnum

from assessment import Assessment
from datamodels import MotorState


class MState(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    COUNTDOWN = 2
    USER_INPUT = 3
    FINISHED = 4


class MotorAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__()

        # Current state
        self.state = MState.STANDBY

        # Compute randomized list of 20 flexion/extension phases (10 each)
        self.phases = [True]*10 + [False]*10
        random.shuffle(self.phases)

        # Maximum velocity reached within phase
        self.v_current = 0
        self.v_max = 0

        # Used for delays
        self._start_time = None

    def is_finished(self, motor_state: MotorState) -> bool:
        return self.state == MState.FINISHED

    def on_start(self, motor_state: MotorState):
        if self.state == MState.STANDBY:
            # Select random phase
            motor_state.Flexion = self.phases[motor_state.TrialNr]
            motor_state.TrialNr += 1

            # Set start and end position accordingly
            if motor_state.Flexion:
                (motor_state.StartingPosition, motor_state.TargetPosition) = (20, 60)
            else:
                (motor_state.StartingPosition, motor_state.TargetPosition) = (60, 20)
            if not motor_state.LeftHand:
                motor_state.StartingPosition *= -1
                motor_state.TargetPosition *= -1
            self.state = MState.MOVING_TO_START

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.state == MState.MOVING_TO_START:
            # Automatic movement towards starting position
            if motor_state.reached_position(motor_state.StartingPosition):
                self._start_time = time.time_ns()
                self.state = MState.COUNTDOWN
            else:
                self.automatic_move_towards(motor_state, motor_state.StartingPosition, delta_time)
        elif self.state == MState.COUNTDOWN:
            # Waiting 1 sec until displaying destination
            if self.time_in_sec_since(self._start_time) >= 1.0:
                motor_state.TargetState = True
                self._start_time = time.time_ns()
                self.state = MState.USER_INPUT
        elif self.state == MState.USER_INPUT:
            # User gets 4 seconds to move towards target
            if self.time_in_sec_since(self._start_time) < 4.0:
                # If input has analog controls, directly map to velocity
                # Otherwise, the speed accelerates/decelerates over time as long as the corresponding key is pressed
                if Assessment.HAS_ANALOG_INPUT:
                    self.v_current = directional_input * Assessment.USER_MAX_MOVEMENT_SPEED
                else:
                    self.v_current += directional_input * Assessment.USER_ACCELERATION_RATE * delta_time

                # Move according to velocity (but clamped to limits)
                new_pos = motor_state.Position + self.get_movement_delta(self.v_current, delta_time, 1.0)
                motor_state.Position = min(max(-90.0, new_pos), 90.0)

                # If user reaches the boundaries, velocity drops to 0
                if 90 - math.fabs(motor_state.Position) < 0.1:
                    self.v_current = 0

                # Compute new v_max and print current data
                self.v_max = max(math.fabs(self.v_current), self.v_max)
                self.print_inplace(
                    f'Current pos: {motor_state.Position:.3f}°, speed: {math.fabs(self.v_current):.3f} [max: {self.v_max:.3f}] °/s')
            else:
                # Time is up, finish probe
                motor_state.TargetState = False
                self.v_max = 0
                if motor_state.TrialNr == len(self.phases):
                    self.state = MState.FINISHED
                else:
                    self.state = MState.STANDBY
