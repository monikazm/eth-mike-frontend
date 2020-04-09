import math
import sys
import time
from abc import ABCMeta, abstractmethod

from datamodels import MotorState


class AutomaticMovement:
    """Linear interpolation between two positions within a particular duration"""

    def __init__(self, start_position: float, target_position: float, duration: float):
        self.start = start_position
        self.end = target_position
        self.start_time = time.time_ns() / 1_000_000_000
        self.duration = duration
        self.end_time = self.start_time + duration

    @property
    def current_location(self) -> float:
        current_time = min(time.time_ns() / 1_000_000_000, self.end_time)
        if math.fabs(self.end_time - current_time) < 0.0001:
            current = self.end
        else:
            current = Assessment.lerp(self.start, self.end, (current_time - self.start_time) / self.duration)
        Assessment.print_inplace(f'Current robot position: {current:.3f}°')
        return current


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
    def lerp(start, end, t: float):
        """Linear interpolation between start and end with t in [0, 1]"""
        return start + (end - start) * t

    @staticmethod
    def get_movement_delta(normalized_velocity, delta_time, speed):
        """Compute the angular offset for this update when moving in normalized_velocity direction with speed."""
        return speed * normalized_velocity * delta_time
