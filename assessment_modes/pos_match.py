import random
from enum import IntEnum
from typing import Optional

from assessment import Assessment
from auto_movement import AutomaticMovement, MoverFactory
from datamodels import MotorState
from util import PrintUtil


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    MOVING_TO_HIDDEN_DEST = 2
    USER_INPUT = 3

    FINISHED = -1


class PositionMatchingAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__(S.STANDBY)

        # Used for automatic movement to starting position and target position
        self.auto_mover: Optional[AutomaticMovement] = None

    def on_start(self, motor_state: MotorState):
        if self.in_state(S.USER_INPUT):
            # Finish probe
            motor_state.TargetState = False
            if motor_state.TrialNr == 21:
                self.goto_state(S.FINISHED)
            else:
                self.goto_state(S.STANDBY)

        if self.in_state(S.STANDBY):
            # Start new probe
            motor_state.TrialNr += 1
            motor_state.StartingPosition = 30.0 if motor_state.LeftHand else -30.0
            self.auto_mover = MoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.in_state(S.MOVING_TO_START):
            # Automatic movement towards starting position
            if motor_state.move_using(self.auto_mover).has_finished():
                # Robot is at starting position, compute random destination
                PrintUtil.print_normally('Reached start')
                motor_state.TargetPosition = float(random.randint(40, 60))
                if not motor_state.LeftHand:
                    motor_state.TargetPosition *= -1.0
                self.auto_mover = MoverFactory.make_linear_mover(motor_state.Position, motor_state.TargetPosition, 3.0)
                self.goto_state(S.MOVING_TO_HIDDEN_DEST)
        elif self.in_state(S.MOVING_TO_HIDDEN_DEST):
            # Automatic movement towards hidden target position
            if motor_state.move_using(self.auto_mover).has_finished():
                motor_state.TargetState = True
                self.goto_state(S.USER_INPUT)
