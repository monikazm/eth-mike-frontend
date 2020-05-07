from keyboard import is_pressed

from mike_simulator.assessment.modes import *
from mike_simulator.datamodels import MotorState, Constants
from mike_simulator.input import InputState
from mike_simulator.input.input_base import InputHandlerBase


class KeyboardInputHandler(InputHandlerBase):

    @staticmethod
    def get_directional_input():
        return float(is_pressed('right') - is_pressed('left'))

    def get_current_force(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        raw_input = self.get_directional_input()
        return self.accelerate(prev_input.force, raw_input, Constants.USER_FORCE_ACCEL_RATE, delta_time)

    def get_current_velocity(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        if isinstance(self.assessment, MotorAssessment):
            raw_input = self.get_directional_input()
            return self.accelerate_or_decelerate(prev_input.velocity, raw_input,
                                                 Constants.USER_BURST_ACCEL_RATE,
                                                 6.0 * Constants.USER_BURST_ACCEL_RATE,
                                                 delta_time)
        elif isinstance(self.assessment, (RangeOfMotionAssessment, SensoriMotorAssessment, PerturbationAssessment)):
            return self.analog_velocity(self.get_directional_input(), Constants.USER_NORMAL_MAX_SPEED)
        else:
            return 0.0
