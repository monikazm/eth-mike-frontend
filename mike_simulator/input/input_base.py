import math
from abc import abstractmethod, ABCMeta

from mike_simulator.datamodels import MotorState, Constants
from mike_simulator.input import InputHandler, InputState


class InputHandlerBase(InputHandler, metaclass=ABCMeta):
    def __init__(self):
        self.assessment = None
        self.movement_locked = True
        self._current_input_state = InputState()

    def begin_assessment(self, assessment_mode):
        self.assessment = assessment_mode
        self._current_input_state = InputState()
        self.movement_locked = True

    def finish_assessment(self):
        self.begin_assessment(None)

    def update_input_state(self, motor_state: MotorState, delta_time: float):
        state = self.current_input_state
        if self.movement_locked:
            state.force = self.get_current_force(state, motor_state, delta_time)
        else:
            prev_velocity = state.velocity
            state.velocity = self.get_current_velocity(state, motor_state, delta_time)
            # Compute some dummy value for the force (F = m * a)
            state.force = (state.velocity - prev_velocity) * (Constants.MASS_CONSTANT / delta_time)

        # Cap values to reasonable range and make sure that velocity drops to 0 when boundary is reached
        state.force = min(max(-Constants.MAX_FORCE, state.force), Constants.MAX_FORCE)
        if self.cannot_move(motor_state.Position, state.velocity):
            state.velocity = 0.0
        else:
            state.velocity = min(max(-Constants.MAX_SPEED, state.velocity), Constants.MAX_SPEED)

    @property
    def current_input_state(self) -> InputState:
        return self._current_input_state

    def reset_input(self):
        self._current_input_state = InputState()

    def lock_movement(self):
        self.movement_locked = True
        self.reset_input()

    def unlock_movement(self):
        self.movement_locked = False
        self.reset_input()

    @abstractmethod
    def get_current_force(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        pass

    @abstractmethod
    def get_current_velocity(self, prev_input: InputState, motor_state: MotorState, delta_time: float) -> float:
        pass

    # Helper functions

    def cannot_move(self, position: float, velocity: float) -> bool:
        """Return true if user movement is disabled or if the robot hit a boundary."""
        if self.movement_locked:
            return True
        if position >= Constants.MAX_POSITION and velocity > 0.0:
            return True
        if position <= Constants.MIN_POSITION and velocity < 0.0:
            return True
        return False

    @staticmethod
    def accelerate(v_start: float, normalized_input: float, acceleration: float, delta_time: float) -> float:
        """Accelerate velocity with rate normalized_input * acceleration"""
        return v_start + normalized_input * acceleration * delta_time

    @staticmethod
    def accelerate_or_decelerate(v_start: float, normalized_input: float, acceleration: float, deceleration: float, delta_time: float) -> float:
        """Accelerate velocity as long as input is above threshold and decelerate otherwise."""
        if math.fabs(normalized_input) > 0.3:
            return InputHandlerBase.accelerate(v_start, normalized_input, acceleration, delta_time)
        else:
            if v_start < 0:
                return min(0.0, InputHandlerBase.accelerate(v_start, 1.0, deceleration, delta_time))
            else:
                return max(0.0, InputHandlerBase.accelerate(v_start, -1.0, deceleration, delta_time))

    @staticmethod
    def analog_velocity(normalized_input: float, max_velocity: float) -> float:
        return normalized_input * max_velocity
