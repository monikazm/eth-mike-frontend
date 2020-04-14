from enum import IntEnum

from assessment import Assessment
from datamodels import MotorState
from util import PrintUtil, Timer


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

        # Stores the currently applied force (only during 3sec force phase)
        self.current_force = 0

        # Used to simulate delays
        self.timer = Timer()

    def on_start(self, motor_state: MotorState):
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

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.in_state(S.COUNTDOWN):
            # We are waiting for 3 sec until to start applying force
            if self.timer.has_finished():
                motor_state.TargetState = True
                self.timer.start(3.0)
                self.goto_state(S.USER_INPUT)
        elif self.in_state(S.USER_INPUT):
            if self.timer.is_active():
                # If input device has analog controls, directly map analog state to force
                # otherwise (e.g. with keyboard), increase/decrease force over time as long as keys are pressed
                if Assessment.HAS_ANALOG_INPUT:
                    # Mask input depending on the measured direction and the hand which is used
                    if motor_state.Flexion != motor_state.LeftHand:
                        directional_input = -min(directional_input, 0.0)
                    else:
                        directional_input = max(0.0, directional_input)

                    self.current_force = directional_input * Assessment.MAX_FORCE
                else:
                    # Depending on flexion/extension, different directions lead to increase in force
                    if motor_state.Flexion != motor_state.LeftHand:
                        directional_input = -directional_input

                    self.current_force += self.get_movement_delta(directional_input, delta_time,
                                                                  Assessment.USER_FORCE_CHANGE_SPEED)

                self.current_force = min(max(0.0, self.current_force), Assessment.MAX_FORCE)
                PrintUtil.print_inplace(f'Current force: {self.current_force:.3f} N')
            else:
                # After 3 seconds, the probe ends
                motor_state.TargetState = False
                self.current_force = 0.0

                if self.phase_probe_num == 3:
                    # Move on to extension phase or quit if this has already been the extension phase
                    if motor_state.Flexion:
                        motor_state.Flexion = False
                        self.goto_state(S.STANDBY)
                    else:
                        self.goto_state(S.FINISHED)
                else:
                    self.goto_state(S.STANDBY_IN_PHASE)
