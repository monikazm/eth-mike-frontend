import XInput as xinput

from mike_simulator.assessment.modes import *
from mike_simulator.datamodels import MotorState, Constants
from mike_simulator.input import InputState
from mike_simulator.input.input_base import InputHandlerBase


class GamepadInputHandler(InputHandlerBase):
    def __init__(self):
        super().__init__()
        if not any(xinput.get_connected()):
            raise RuntimeError('No gamepad connected')

    @staticmethod
    def get_directional_input():
        state = xinput.get_state(0)
        return xinput.get_thumb_values(state)[0][0]

    def get_current_force(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        return self.analog_velocity(self.get_directional_input(), Constants.MAX_FORCE)

    def get_current_velocity(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        if isinstance(self.assessment, MotorAssessment):
            raw_input = self.get_directional_input()
            return self.accelerate_or_decelerate(prev_input.velocity, raw_input,
                                                 Constants.USER_BURST_ACCEL_RATE,
                                                 6.0 * Constants.USER_BURST_ACCEL_RATE,
                                                 delta_time)
        elif isinstance(self.assessment, (RangeOfMotionAssessment, SensoriMotorAssessment, PreciseReachAssessment, ActiveMatchingAssessment)):
            return self.analog_velocity(self.get_directional_input(), Constants.USER_NORMAL_MAX_SPEED)
        else:
            return 0.0
