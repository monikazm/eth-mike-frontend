import random
from enum import IntEnum
from typing import Optional

from assessment import Assessment, AutomaticMovement
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

        # Used for automatic movement to starting position and target position
        self._automove: Optional[AutomaticMovement] = None

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
        motor_state.StartingPosition = 30.0 if motor_state.LeftHand else -30.0

        self._automove = AutomaticMovement(motor_state.Position, motor_state.StartingPosition, 3.0)
        self.state = POMState.MOVING_TO_START

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.state == POMState.MOVING_TO_START:
            if motor_state.Position == motor_state.StartingPosition:
                # Robot is at starting position, compute random destination
                self.print_normally('Reached start')
                motor_state.TargetPosition = float(random.randint(40, 60))
                if not motor_state.LeftHand:
                    motor_state.TargetPosition *= -1.0
                self._automove = AutomaticMovement(motor_state.Position, motor_state.TargetPosition, 3.0)
                self.state = POMState.MOVING_TO_HIDDEN_DEST
            else:
                # Automatic movement towards starting position
                motor_state.Position = self._automove.current_location
        elif self.state == POMState.MOVING_TO_HIDDEN_DEST:
            if motor_state.Position == motor_state.TargetPosition:
                motor_state.TargetState = True
                self.state = POMState.USER_INPUT
            else:
                motor_state.Position = self._automove.current_location
