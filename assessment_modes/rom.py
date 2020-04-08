import math
import time

from assessment import Assessment
from datamodels import MotorState, RomState


class RangeOfMotionAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__()

        # Current trial number within a phase
        self.num_trials = 0

        # Extreme positions recorded during passive movement phase
        self.p_min_motion = 0
        self.p_max_motion = 0

        # Sine parameters, computed when automatic passive movement phase is started
        self.ap_start_time = -1
        self.ap_ampl = -1
        self.ap_offset = -1

        # Whether assessment is finished
        self.finished = False

    def _sine(self, t):
        freq = 0.5
        return math.sin(2 * math.pi * freq * (t / 30)) * self.ap_ampl + self.ap_offset

    def on_start(self, motor_state: MotorState):
        if not motor_state.TargetState:
            if motor_state.RomState == RomState.AutomaticPassiveMovement:
                # Compute sine parameters
                self.ap_ampl = (self.p_max_motion - self.p_min_motion) / 2
                self.ap_offset = (self.p_max_motion + self.p_min_motion) / 2
                self.ap_start_time = time.time_ns()
                Assessment.print_normally(f'Moving between {self.p_min_motion} and {self.p_max_motion}, '
                                          f'via sine wave with ampl = {self.ap_ampl} and offset: {self.ap_offset}')

            # Start listening for user input
            motor_state.TargetState = True
            self.num_trials = 0

        if self.num_trials == 3:
            # Phase is over
            motor_state.TargetState = False
            if motor_state.RomState != RomState.AutomaticPassiveMovement:
                # Goto next phase if we are not yet in automatic passive movement
                motor_state.RomState = RomState(motor_state.RomState + 1)
            else:
                # End the assessment if all phases are finished
                self.finished = True
        else:
            # Continue with next measurement
            motor_state.TrialNr += 1
            self.num_trials += 1
            motor_state.Position = 0

    def is_finished(self, motor_state: MotorState) -> bool:
        return self.finished

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if not self.finished and motor_state.TargetState:
            state = motor_state.RomState
            if state == RomState.ActiveMotion or state == RomState.PassiveMotion:
                # In active and passive phases, the movement is controlled via keyboard/gamepad
                motor_state.Position += self.get_movement_delta(directional_input, delta_time, Assessment.USER_MAX_MOVEMENT_SPEED)
                if state == RomState.PassiveMotion:
                    self.print_inplace(f'Current position: {motor_state.Position:.3f}°')
            else:
                # In automatic passive movement phase, the movement is controlled by the sine
                motor_state.Position = self._sine(self.time_in_sec_since(self.ap_start_time))
                self.print_inplace(f'Current position: {motor_state.Position:.3f}°')

            # Clamp position to legal range
            motor_state.Position = min(max(-90.0, motor_state.Position), 90.0)

            if state == RomState.PassiveMotion:
                # Record extreme values for Passive motion
                self.p_min_motion = min(motor_state.Position, self.p_min_motion)
                self.p_max_motion = max(motor_state.Position, self.p_max_motion)
