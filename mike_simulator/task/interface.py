from abc import ABCMeta, abstractmethod

from mike_simulator.datamodels import MotorState, ControlResponse
from mike_simulator.input import InputHandler


class Task(metaclass=ABCMeta):
    """Abstract interface for a task"""

    # Abstract Interface

    def __init__(self, state):
        self.state = state

    @abstractmethod
    def on_start(self, motor_state: MotorState, control_response: ControlResponse, input_handler: InputHandler, starting_position: float, target_position: float):
        """Should be called whenever the frontend issued a start command."""
        pass

    @abstractmethod
    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        """Should be called regularly to update the motor state."""
        pass

    def on_skip(self, motor_state: MotorState):
        """Called when the backend receives a skip signal"""
        pass

    # Helper Functionality

    def is_finished(self) -> bool:
        """Returns true if task is finished."""
        return self.state == -1

    def in_state(self, state) -> bool:
        """Return true if the task is in the given state."""
        return self.state == state

    def goto_state(self, state):
        """Perform an task state transition."""
        self.state = state

    @abstractmethod
    def _prepare_next_trial_or_finish(self, motor_state: MotorState, control_response: ControlResponse):
        """This should be called internally at the beginning and whenever a trial is finished"""
        pass
