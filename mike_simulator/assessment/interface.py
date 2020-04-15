from abc import ABCMeta, abstractmethod

from mike_simulator.datamodels import MotorState
from mike_simulator.input import InputHandler


class Assessment(metaclass=ABCMeta):
    """Abstract interface for an assessment"""

    # Abstract Interface

    def __init__(self, state):
        self.state = state

    @abstractmethod
    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        """Should be called whenever the frontend issued a start command."""
        pass

    @abstractmethod
    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        """Should be called regularly to update the motor state."""
        pass

    # Helper Functionality

    def is_finished(self) -> bool:
        """Returns true if assessment is finished."""
        return self.state == -1

    def in_state(self, state) -> bool:
        """Return true if the Assessment is in the given state."""
        return self.state == state

    def goto_state(self, state):
        """Perform an assessment state transition."""
        self.state = state
