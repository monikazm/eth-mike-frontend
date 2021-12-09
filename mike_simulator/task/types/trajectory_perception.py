import random
import time
from enum import IntEnum
from typing import Optional

from mike_simulator.task import Task
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.datamodels import MotorState, PatientResponse
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    MOVING_TO_TARGET = 2
    WAIT_AT_TARGET = 3
    MOVING_BACK_TO_START = 4
    USER_INPUT = 5

    FINISHED = -1


class TrajectoryPerceptionAssessment(Task):
    def __init__(self, motor_state: MotorState, patient: PatientResponse) -> None:
        super().__init__(S.STANDBY)
        self.direction = 1 if patient.LeftHand else -1

        self.trial_count = patient.PhaseTrialCount

        # Used for automatic movement to starting position and target position
        self.auto_mover: Optional[AutoMover] = None

        # Set starting position and initialize trial
        self._prepare_next_trial_or_finish(motor_state)

        # Get Target Position in the beginning
        self.target_position = 0

        self.waiting_since = time.time()

    def _prepare_next_trial_or_finish(self, motor_state: MotorState):
        if motor_state.TrialNr == self.trial_count:
            self.goto_state(S.FINISHED)
        else:
            motor_state.TrialNr += 1
            self.goto_state(S.STANDBY)

    def on_start(self, motor_state: MotorState, input_handler: InputHandler, starting_position: float, target_position: float):
        motor_state.StartingPosition = starting_position;
        if self.in_state(S.USER_INPUT):
            # User confirmed selected position -> start next trial (if any)
            motor_state.TargetState = False
            self._prepare_next_trial_or_finish(motor_state)

        if self.in_state(S.STANDBY):
            # Start new trial, instruct robot to move to starting position within 2 seconds
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 2.0)
            self.goto_state(S.MOVING_TO_START)
            self.target_position = target_position

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            # Automatic movement towards starting position
            if motor_state.move_using(self.auto_mover).has_finished():
                # Robot is at starting position, compute random destination
                PrintUtil.print_normally('Reached start')
                motor_state.TargetPosition = self.target_position

                # Instruct robot to move to random destination within 2 seconds
                self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.TargetPosition, 2.0)
                self.goto_state(S.MOVING_TO_TARGET)

        elif self.in_state(S.MOVING_TO_TARGET):
            # Automatic movement towards random destination
            if motor_state.move_using(self.auto_mover).has_finished():
                # Once target is reached, wait for user to enter a position in the frontend
                #motor_state.TargetState = True
                #self.goto_state(S.USER_INPUT)
                PrintUtil.print_normally('Reached target')
                self.waiting_since = time.time()
                self.goto_state(S.WAIT_AT_TARGET)

        elif self.in_state(S.WAIT_AT_TARGET):
            time_elapsed = time.time() - self.waiting_since
            if time_elapsed > 1.0:  # wait for one second
                # Instruct robot to move to back to start position within 3 seconds
                self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
                self.goto_state(S.MOVING_BACK_TO_START)

        elif self.in_state(S.MOVING_BACK_TO_START):
            # Automatic movement back to start destination
            if motor_state.move_using(self.auto_mover).has_finished():
                PrintUtil.print_normally('Back at start')
                # Once target is reached, wait for user to move back to the target and confirm input
                motor_state.TargetState = True
                #input_handler.unlock_movement()
                self.goto_state(S.USER_INPUT)

        elif self.in_state(S.USER_INPUT):
            # Print current position
           PrintUtil.print_inplace(f'Current pos: {motor_state.Position:.3f}°')