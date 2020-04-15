from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.datamodels import MotorState
from mike_simulator.input import InputHandler


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    USER_FOLLOW = 2

    FINISHED = -1


class SensoriMotorAssessment(Assessment):
    def __init__(self):
        super().__init__(S.STANDBY)

        # Whether we are in the slow or fast phase
        self.fast_phase = False

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutoMover] = None

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.STANDBY):
            motor_state.TrialNr += 1

            # Move to starting position in 3 seconds (if not already there)
            motor_state.StartingPosition = 45.0 if motor_state.LeftHand else -45.0
            motor_state.TargetPosition = motor_state.StartingPosition
            move_time = 0.0 if motor_state.is_at_position(motor_state.StartingPosition) else 3.0
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, move_time)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            if motor_state.move_using(self.auto_mover).has_finished():
                # Instruct robot to move along mixture of sines for 30 seconds
                factor = 3.0 if self.fast_phase else 1.0
                amplitude = 15.0 if motor_state.LeftHand else -15.0
                sine_params = [
                    (amplitude, 1.0 * factor),
                    (amplitude, 2.0 * factor),
                    (amplitude, 4.0 * factor)
                ]
                self.auto_mover = AutoMoverFactory.make_sine_mover(motor_state.StartingPosition, 30.0, *sine_params)

                # Allow user movement
                motor_state.TargetState = True
                input_handler.unlock_movement()

                self.goto_state(S.USER_FOLLOW)
        elif self.in_state(S.USER_FOLLOW):
            if motor_state.move_target_using(self.auto_mover).has_finished():
                # Disable user movement after 30 seconds
                input_handler.lock_movement()
                motor_state.TargetState = False

                # Wait for next probe to start (if any)
                if motor_state.TrialNr == 3:
                    self.fast_phase = True
                elif motor_state.TrialNr == 6:
                    self.goto_state(S.FINISHED)
                    return
                self.goto_state(S.STANDBY)
