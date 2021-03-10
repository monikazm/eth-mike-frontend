from enum import IntEnum
from typing import Optional

from mike_simulator.task import Task
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.config import cfg
from mike_simulator.datamodels import MotorState, PatientResponse
from mike_simulator.input import InputHandler


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    USER_FOLLOW = 2

    FINISHED = -1


class SensoriMotorAssessment(Task):
    def __init__(self, motor_state: MotorState, patient: PatientResponse):
        super().__init__(S.STANDBY)
        self.direction = 1.0 if patient.LeftHand else -1.0

        # Whether we are in the slow or fast phase
        self.fast_phase = False

        self.phase_trial_count = patient.PhaseTrialCount

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutoMover] = None

        # Set starting position and initialize trial
        motor_state.StartingPosition = 45.0 * self.direction
        self._prepare_next_trial_or_finish(motor_state)

    def _prepare_next_trial_or_finish(self, motor_state: MotorState):
        if motor_state.TrialNr == self.phase_trial_count * 2:
            self.goto_state(S.FINISHED)
        else:
            if motor_state.TrialNr == self.phase_trial_count:
                self.fast_phase = True
            motor_state.TrialNr += 1
            self.goto_state(S.STANDBY)

    def on_start(self, motor_state: MotorState, input_handler: InputHandler, starting_position: float, target_position: float):
        if self.in_state(S.STANDBY):
            # Move to starting position in 3 seconds
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            if motor_state.move_using(self.auto_mover).has_finished():
                # Instruct robot to move along mixture of sines for 30 seconds
                factor = 3.0 if self.fast_phase else 1.0
                amplitude = 15.0 * self.direction
                sine_params = [
                    (amplitude, 1.0 * factor),
                    (amplitude, 2.0 * factor),
                    (amplitude, 4.0 * factor)
                ]
                self.auto_mover = AutoMoverFactory.make_sine_mover(motor_state.StartingPosition,
                                                                   cfg.Tasks.sensorimotor_movement_duration,
                                                                   *sine_params)

                # Allow user movement
                motor_state.TargetState = True
                input_handler.unlock_movement()

                self.goto_state(S.USER_FOLLOW)
        elif self.in_state(S.USER_FOLLOW):
            if motor_state.move_target_using(self.auto_mover).has_finished():
                # Disable user movement after 30 seconds and wait for next trial to start (if any)
                input_handler.lock_movement()
                motor_state.TargetState = False
                self._prepare_next_trial_or_finish(motor_state)

    def on_skip(self, motor_state: MotorState):
        if self.in_state(S.STANDBY):
            firstTrialOfPhase = motor_state.TrialNr % self.phase_trial_count == 1
            afterFirstInLastPhase = motor_state.TrialNr > self.phase_trial_count + 1
            if not (firstTrialOfPhase or afterFirstInLastPhase):
                motor_state.TrialNr = self.phase_trial_count
                self._prepare_next_trial_or_finish(motor_state)
            if afterFirstInLastPhase:
                self.goto_state(S.FINISHED)
