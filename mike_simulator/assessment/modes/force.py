from enum import IntEnum

from mike_simulator.assessment import Assessment
from mike_simulator.datamodels import MotorState
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil, Timer


class S(IntEnum):
    STANDBY = 0
    STANDBY_IN_PHASE = 1
    COUNTDOWN = 2
    USER_INPUT = 3

    FINISHED = -1


class ForceAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__(S.STANDBY)

        # The probe number within the current phase
        self.phase_probe_num = 0

        # Used to simulate delays
        self.timer = Timer()

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.STANDBY):
            # Start a new phase
            self.phase_probe_num = 0
            self.goto_state(S.STANDBY_IN_PHASE)

        if self.in_state(S.STANDBY_IN_PHASE):
            # Start a probe
            self.phase_probe_num += 1
            motor_state.TrialNr += 1
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
                # After 3 seconds, the probe ends
                motor_state.TargetState = False
                input_handler.reset_input()

                # Wait for next probe to start
                if self.phase_probe_num == 3:
                    # Move on to extension phase or quit if this has already been the extension phase
                    if motor_state.Flexion:
                        motor_state.Flexion = False
                        self.goto_state(S.STANDBY)
                    else:
                        self.goto_state(S.FINISHED)
                else:
                    self.goto_state(S.STANDBY_IN_PHASE)
