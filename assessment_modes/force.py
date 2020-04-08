import time
from enum import IntEnum

from assessment import Assessment
from datamodels import MotorState


class ForceState(IntEnum):
    STANDBY = 0,
    STANDBY_IN_PHASE = 1,
    COUNTDOWN = 2,
    USER_INPUT = 3,
    FINISHED = 4,


class ForceAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__()

        # Current state
        self.state = ForceState.STANDBY

        # The probe number within the current phase
        self.phase_probe_num = 0

        # Stores the currently applied force (only during 3sec force phase)
        self.current_force = 0

        # Used for delays
        self._start_time = None

    def is_finished(self, motor_state: MotorState) -> bool:
        return self.state == ForceState.FINISHED

    def on_start(self, motor_state: MotorState):
        if self.state == ForceState.STANDBY:
            # Start a new phase
            self.state = ForceState.STANDBY_IN_PHASE
            self.phase_probe_num = 0

        if self.state == ForceState.STANDBY_IN_PHASE:
            # Start a probe
            self._start_time = time.time_ns()
            self.phase_probe_num += 1
            motor_state.TrialNr += 1
            self.state = ForceState.COUNTDOWN

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.state == ForceState.COUNTDOWN:
            # We are waiting for 3 sec until to start applying force
            if self.time_in_sec_since(self._start_time) >= 3.0:
                motor_state.TargetState = True
                self._start_time = time.time_ns()
                self.state = ForceState.USER_INPUT
        elif self.state == ForceState.USER_INPUT:
            if self.time_in_sec_since(self._start_time) < 3.0:
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
                self.print_inplace(f'Current force: {self.current_force:.3f} N')
            else:
                # After 3 seconds, the probe ends
                motor_state.TargetState = False

                if self.phase_probe_num == 3:
                    # Move on to extension phase or quit if this has already been the extension phase
                    if motor_state.Flexion:
                        motor_state.Flexion = False
                        self.state = ForceState.STANDBY
                    else:
                        self.state = ForceState.FINISHED
                else:
                    self.state = ForceState.STANDBY_IN_PHASE
