from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.config import cfg
from mike_simulator.datamodels import MotorState, RomState, PatientResponse
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    USER_INPUT = 2
    AUTO_MOVE = 3

    FINISHED = -1


class RangeOfMotionAssessment(Assessment):
    def __init__(self, patient: PatientResponse) -> None:
        super().__init__(S.STANDBY)

        self.direction = 1.0 if patient.LeftHand else -1.0

        # Extreme positions recorded during passive movement phase
        self.p_min_motion = 30.0 * self.direction
        self.p_max_motion = self.p_min_motion

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutoMover] = None

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.USER_INPUT):
            # Finish currently active probe (disable user movement) if not in automatic passive movement phase
            motor_state.TargetState = False
            input_handler.lock_movement()
            if motor_state.TrialNr == cfg.Assessments.num_rom_repetitions:
                # Goto next phase
                motor_state.RomState = RomState(motor_state.RomState + 1)
                motor_state.TrialNr = 0
                self.goto_state(S.STANDBY)
                return
            else:
                self.goto_state(S.STANDBY)

        if self.in_state(S.STANDBY):
            self._start_probe(motor_state)

    def _start_probe(self, motor_state):
        # Instruct robot to move to starting position in 3 seconds (if not already there)
        motor_state.TrialNr += 1
        if motor_state.RomState == RomState.AutomaticPassiveMovement:
            motor_state.StartingPosition = (self.p_max_motion + self.p_min_motion) / 2.0
        else:
            motor_state.StartingPosition = 30.0 * self.direction
        move_time = 0.0 if motor_state.is_at_position(motor_state.StartingPosition) else 3.0
        self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, move_time)
        self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            # Automatic movement towards starting position
            if motor_state.move_using(self.auto_mover).has_finished():
                if motor_state.RomState == RomState.AutomaticPassiveMovement:
                    # In automatic passive movement phase, instruct robot to move along sine
                    # with parameters based on passive movement phase for 2 seconds
                    amplitude = (self.p_max_motion - self.p_min_motion) / 2.0
                    if not motor_state.LeftHand:
                        amplitude = -amplitude
                    freq = 1.0
                    self.auto_mover = AutoMoverFactory.make_sine_mover(motor_state.Position, 2.0, (amplitude, freq))
                    self.goto_state(S.AUTO_MOVE)
                else:
                    # In other phases, allow user movement
                    motor_state.TargetState = True
                    input_handler.unlock_movement()
                    self.goto_state(S.USER_INPUT)
        elif self.in_state(S.USER_INPUT):
            if motor_state.RomState == RomState.PassiveMotion:
                # Record extreme values for Passive motion
                self.p_min_motion = min(motor_state.Position, self.p_min_motion)
                self.p_max_motion = max(motor_state.Position, self.p_max_motion)
                PrintUtil.print_inplace(f'Current position: {motor_state.Position:.3f}°')
        elif self.in_state(S.AUTO_MOVE):
            # In automatic passive movement phase, automatically start next probe when movement is finished (if any)
            if motor_state.move_using(self.auto_mover).has_finished():
                if motor_state.TrialNr == cfg.Assessments.num_rom_repetitions:
                    self.goto_state(S.FINISHED)
                else:
                    self._start_probe(motor_state)
