import random
from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.config import cfg
from mike_simulator.datamodels import MotorState, PatientResponse
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    MOVING_TO_HIDDEN_DEST = 2
    USER_INPUT = 3

    FINISHED = -1


class PositionMatchingAssessment(Assessment):
    def __init__(self, patient: PatientResponse) -> None:
        super().__init__(S.STANDBY)
        self.direction = 1.0 if patient.LeftHand else -1.0

        # Used for automatic movement to starting position and target position
        self.auto_mover: Optional[AutoMover] = None

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.USER_INPUT):
            # User confirmed selected position -> start next probe (if any)
            motor_state.TargetState = False
            if motor_state.TrialNr == cfg.Assessments.num_pos_match_trials:
                self.goto_state(S.FINISHED)
            else:
                self.goto_state(S.STANDBY)

        if self.in_state(S.STANDBY):
            # Start new probe, instruct robot to move to starting position within 3 seconds
            motor_state.TrialNr += 1
            motor_state.StartingPosition = 30.0 * self.direction
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            # Automatic movement towards starting position
            if motor_state.move_using(self.auto_mover).has_finished():
                # Robot is at starting position, compute random destination
                PrintUtil.print_normally('Reached start')
                motor_state.TargetPosition = float(random.randint(40, 60)) * self.direction

                # Instruct robot to move to random destination within 3 seconds
                self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.TargetPosition, 3.0)
                self.goto_state(S.MOVING_TO_HIDDEN_DEST)
        elif self.in_state(S.MOVING_TO_HIDDEN_DEST):
            # Automatic movement towards random destination
            if motor_state.move_using(self.auto_mover).has_finished():
                # Once target is reached, wait for user to enter a position in the frontend
                motor_state.TargetState = True
                self.goto_state(S.USER_INPUT)
