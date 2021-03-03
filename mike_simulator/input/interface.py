from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from mike_simulator.datamodels import MotorState


@dataclass
class InputState:
    force: float = 0.0
    velocity: float = 0.0


class InputHandler(metaclass=ABCMeta):
    """Abstract interface for input handler"""

    @abstractmethod
    def begin_task(self, task):
        """Make InputHandler aware than a task was started."""
        pass

    @abstractmethod
    def finish_task(self):
        """Make InputHandler aware that the current task ended."""
        pass

    @abstractmethod
    def update_input_state(self, motor_state: MotorState, delta_time: float):
        """Update the current input state."""
        pass

    @property
    @abstractmethod
    def current_input_state(self) -> InputState:
        """Return the current input state."""
        pass

    @abstractmethod
    def reset_input(self):
        """Reset input state"""
        pass

    @abstractmethod
    def lock_movement(self):
        """Prevent user from moving the robot."""
        pass

    @abstractmethod
    def unlock_movement(self):
        """Allow user to move the robot"""
        pass
