import random
from enum import IntEnum

from assessment import Assessment
from datamodels import MotorState


class POMState(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    MOVING_TO_HIDDEN_DEST = 2
    USER_INPUT = 3
    FINISHED = 4


class PositionMatchingAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__()

        # Current state
        self.state = POMState.STANDBY

    def is_finished(self, motor_state: MotorState) -> bool:
        return self.state == POMState.FINISHED

    def on_start(self, motor_state: MotorState):
        if self.state != POMState.STANDBY:
            # Finish probe
            motor_state.TargetState = False
            self.state = POMState.STANDBY
            if motor_state.TrialNr == 21:
                self.state = POMState.FINISHED
                return

        # Start new probe
        motor_state.TrialNr += 1
        motor_state.StartingPosition = 30 if motor_state.LeftHand else -30
        self.state = POMState.MOVING_TO_START

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.state == POMState.MOVING_TO_START:
            if motor_state.reached_position(motor_state.StartingPosition):
                # Robot is at starting position, compute random destination
                self.print_normally('Reached start')
                motor_state.TargetPosition = random.uniform(40.0, 60.0)
                if not motor_state.LeftHand:
                    motor_state.TargetPosition *= -1
                self.state = POMState.MOVING_TO_HIDDEN_DEST
            else:
                # Automatic movement towards starting position
                self.automatic_move_towards(motor_state, motor_state.StartingPosition, delta_time)
        elif self.state == POMState.MOVING_TO_HIDDEN_DEST:
            if motor_state.reached_position(motor_state.TargetPosition):
                motor_state.TargetState = True
                self.state = POMState.USER_INPUT
            else:
                self.automatic_move_towards(motor_state, motor_state.TargetPosition, delta_time)
