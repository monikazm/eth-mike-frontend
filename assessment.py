from abc import ABCMeta, abstractmethod

from datamodels import MotorState


class Assessment(metaclass=ABCMeta):
    """Abstract interface for an assessment"""

    # Maximum measurable force [N]
    MAX_FORCE = 50

    # Speeds are in [degree / s]
    USER_MAX_MOVEMENT_SPEED = 50.0

    # Rates at how digital input changes applied force [N / s]
    USER_FORCE_CHANGE_SPEED = 30.0

    # Rates at how velocity accelerates with digital input [degree / s^2]
    USER_ACCELERATION_RATE = 2200.0

    # This is set by simulator depending on whether a gamepad is plugged in
    HAS_ANALOG_INPUT = False

    _inplace = False

    # Abstract Interface

    def __init__(self, state):
        self.state = state

    @abstractmethod
    def on_start(self, motor_state: MotorState):
        """Should be called whenever the frontend issued a start command."""
        pass

    @abstractmethod
    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        """Should be called regularly to update the motor state."""
        pass

    # Helper Functionality

    def is_finished(self) -> bool:
        """Returns true if assessment is finished."""
        return self.state == -1

    def in_state(self, state) -> bool:
        return self.state == state

    def goto_state(self, state):
        self.state = state

    @staticmethod
    def get_movement_delta(normalized_velocity, delta_time, speed):
        """Compute the angular offset for this update when moving in normalized_velocity direction with speed."""
        return speed * normalized_velocity * delta_time
