from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement import AutomaticMovement, MoverFactory
from mike_simulator.datamodels import MotorState


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
        self.auto_mover: Optional[AutomaticMovement] = None

    def on_start(self, motor_state: MotorState):
        if self.in_state(S.STANDBY):
            motor_state.TrialNr += 1
            motor_state.StartingPosition = 45.0 if motor_state.LeftHand else -45.0
            motor_state.TargetPosition = motor_state.StartingPosition
            move_time = 0.0 if motor_state.is_at_position(motor_state.StartingPosition) else 3.0
            self.auto_mover = MoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, move_time)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.in_state(S.MOVING_TO_START):
            if motor_state.move_using(self.auto_mover).has_finished():
                motor_state.TargetState = True
                factor = 3.0 if self.fast_phase else 1.0
                amplitude = 15.0 if motor_state.LeftHand else -15.0
                sine_params = [
                    (amplitude, 1.0 * factor),
                    (amplitude, 2.0 * factor),
                    (amplitude, 4.0 * factor)
                ]
                self.auto_mover = MoverFactory.make_sine_mover(motor_state.StartingPosition, 30.0, *sine_params)
                self.goto_state(S.USER_FOLLOW)
        elif self.in_state(S.USER_FOLLOW):
            # In active and passive phases, the movement is controlled via keyboard/gamepad
            motor_state.Position += self.get_movement_delta(directional_input, delta_time,
                                                            Assessment.USER_MAX_MOVEMENT_SPEED)
            # Clamp position to legal range
            motor_state.Position = min(max(-90.0, motor_state.Position), 90.0)

            if motor_state.move_target_using(self.auto_mover).has_finished():
                motor_state.TargetState = False
                if motor_state.TrialNr == 3:
                    self.fast_phase = True
                elif motor_state.TrialNr == 6:
                    self.goto_state(S.FINISHED)
                    return
                self.goto_state(S.STANDBY)
