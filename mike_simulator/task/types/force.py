from enum import IntEnum

from mike_simulator.task import Task
from mike_simulator.datamodels import MotorState, PatientResponse
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil, Timer


class S(IntEnum):
    STANDBY = 0
    COUNTDOWN = 1
    USER_INPUT = 2

    FINISHED = -1


class ForceAssessment(Task):
    def __init__(self, motor_state: MotorState, patient: PatientResponse) -> None:
        super().__init__(S.STANDBY)

        # Used to simulate delays
        self.timer = Timer()

        self.phase_trial_count = patient.PhaseTrialCount

        # Set starting position and initialize trial
        motor_state.StartingPosition = 0.0
        self._prepare_next_trial_or_finish(motor_state)

    def _prepare_next_trial_or_finish(self, motor_state: MotorState):
        if motor_state.TrialNr == 2 * self.phase_trial_count:
            self.goto_state(S.FINISHED)
        else:
            if motor_state.TrialNr == self.phase_trial_count:
                motor_state.Flexion = False
            motor_state.TrialNr += 1
            self.goto_state(S.STANDBY)

    def on_start(self, motor_state: MotorState, input_handler: InputHandler, target_position: float):
        if self.in_state(S.STANDBY):
            # Start a trial
            self.timer.start(3.0)
            self.goto_state(S.COUNTDOWN)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.COUNTDOWN):
            # We are waiting for 3 sec until the user is asked to apply force
            if self.timer.has_finished():
                motor_state.TargetState = True
                input_handler.reset_input()
                self.timer.start(3.0)
                self.goto_state(S.USER_INPUT)
        elif self.in_state(S.USER_INPUT):
            if self.timer.is_active():
                PrintUtil.print_inplace(f'Current force: {motor_state.Force:.3f} N')
            else:
                # After 3 seconds, the trial ends
                motor_state.TargetState = False
                input_handler.reset_input()
                self._prepare_next_trial_or_finish(motor_state)
