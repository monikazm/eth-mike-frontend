import sys
import time
from abc import ABCMeta, abstractmethod

from datamodels import MotorState


class Assessment(metaclass=ABCMeta):
    """Abstract interface for an assessment"""

    # Maximum measurable force [N]
    MAX_FORCE = 50

    # Speeds are in [degree / s]
    AUTOMATIC_MOVEMENT_MAX_SPEED = 30.0
    USER_MAX_MOVEMENT_SPEED = 50.0

    # Rates at how digital input changes applied force [N / s]
    USER_FORCE_CHANGE_SPEED = 30.0

    # Rates at how velocity accelerates with digital input [degree / s^2]
    USER_ACCELERATION_RATE = 20.0

    # This is set by simulator depending on whether a gamepad is plugged in
    HAS_ANALOG_INPUT = False

    _inplace = False

    # Abstract Interface

    @abstractmethod
    def is_finished(self, ms: MotorState) -> bool:
        """Returns true if assessment is finished."""
        pass

    @abstractmethod
    def on_start(self, motor_state: MotorState):
        """Should be called whenever the frontend issued a start command."""
        pass

    @abstractmethod
    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        """Should be called regularly to update the motor state."""
        pass

    # Helper Functionality

    @staticmethod
    def print_inplace(*text, **kwargs):
        """Print text by overwriting current line in terminal"""
        Assessment._inplace = True
        print('\r', *text, end='', **kwargs)
        sys.stdout.flush()

    @staticmethod
    def print_normally(*text, **kwargs):
        """Print text on a new line"""
        if Assessment._inplace:
            print()
            Assessment._inplace = False
        print(*text, **kwargs)

    @staticmethod
    def time_in_sec_since(start_time) -> float:
        """Compute elapsed time since start_time. (in fractional seconds)"""
        return (time.time_ns() - start_time) / 1_000_000_000

    @staticmethod
    def automatic_move_towards(motor_state, position, delta_time):
        """Perform automatic robot movement towards position."""
        direction = 1.0 if position > motor_state.Position else -1.0
        motor_state.Position += Assessment.get_movement_delta(direction, delta_time,
                                                              Assessment.AUTOMATIC_MOVEMENT_MAX_SPEED)
        Assessment.print_inplace(f'Current robot position: {motor_state.Position:.3f}°')

    @staticmethod
    def get_movement_delta(normalized_velocity, delta_time, speed):
        """Compute the angular offset for this update when moving in normalized_velocity direction with speed."""
        return speed * normalized_velocity * delta_time
