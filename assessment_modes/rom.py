from enum import IntEnum
from typing import Optional

from assessment import Assessment
from auto_movement import AutomaticMovement, MoverFactory
from datamodels import MotorState, RomState
from util import PrintUtil


class S(IntEnum):
    STANDBY = 0
    STANDBY_IN_PHASE = 1
    MOVING_TO_START = 2
    USER_INPUT = 3
    AUTO_MOVE = 4

    FINISHED = -1


class RangeOfMotionAssessment(Assessment):
    def __init__(self) -> None:
        super().__init__(S.STANDBY)

        # Current trial number within a phase
        self.phase_probe_num = 0

        # Extreme positions recorded during passive movement phase
        self.p_min_motion = 0
        self.p_max_motion = 0

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutomaticMovement] = None

    def on_start(self, motor_state: MotorState):
        if self.in_state(S.USER_INPUT):
            if self.phase_probe_num == 3:
                # Goto next phase
                motor_state.TargetState = False
                motor_state.RomState = RomState(motor_state.RomState + 1)
                self.goto_state(S.STANDBY)
                return
            else:
                self.goto_state(S.STANDBY_IN_PHASE)

        if self.in_state(S.STANDBY):
            self.phase_probe_num = 0
            self.goto_state(S.STANDBY_IN_PHASE)

        if self.in_state(S.STANDBY_IN_PHASE):
            self._start_probe(motor_state)

    def _start_probe(self, motor_state):
        motor_state.TrialNr += 1
        self.phase_probe_num += 1
        if motor_state.RomState == RomState.AutomaticPassiveMovement:
            motor_state.StartingPosition = (self.p_max_motion + self.p_min_motion) / 2.0
        else:
            motor_state.StartingPosition = 0.0
        move_time = 0.0 if motor_state.is_at_position(motor_state.StartingPosition) else 3.0
        self.auto_mover = MoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, move_time)
        self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        if self.in_state(S.MOVING_TO_START):
            if motor_state.move_using(self.auto_mover).has_finished():
                if motor_state.RomState == RomState.AutomaticPassiveMovement:
                    amplitude = (self.p_max_motion - self.p_min_motion) / 2.0
                    freq = 0.5
                    self.auto_mover = MoverFactory.make_sine_mover(motor_state.Position, 2.0, (amplitude, freq))
                    self.goto_state(S.AUTO_MOVE)
                else:
                    motor_state.TargetState = True
                    self.goto_state(S.USER_INPUT)
        elif self.in_state(S.USER_INPUT):
            # In active and passive phases, the movement is controlled via keyboard/gamepad
            motor_state.Position += self.get_movement_delta(directional_input, delta_time,
                                                            Assessment.USER_MAX_MOVEMENT_SPEED)
            # Clamp position to legal range
            motor_state.Position = min(max(-90.0, motor_state.Position), 90.0)

            if motor_state.RomState == RomState.PassiveMotion:
                # Record extreme values for Passive motion
                self.p_min_motion = min(motor_state.Position, self.p_min_motion)
                self.p_max_motion = max(motor_state.Position, self.p_max_motion)

                PrintUtil.print_inplace(f'Current position: {motor_state.Position:.3f}°')
        elif self.in_state(S.AUTO_MOVE):
            if motor_state.move_using(self.auto_mover).has_finished():
                if self.phase_probe_num == 3:
                    self.goto_state(S.FINISHED)
                else:
                    self._start_probe(motor_state)
