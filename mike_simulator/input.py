from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum

from mike_simulator.assessment import Assessment


class InputMethod(Enum):
    pass
    #Gamepad
    #Keyboard
    #Prerecorded
    #Random


@dataclass
class InputState:
    force: float = 0.0
    velocity: float = 0.0


class InputHandler(metaclass=ABCMeta):
    @staticmethod
    def create(method: InputMethod):
        pass

    def get_current_input(self, assessment_mode: Assessment, delta_time: float) -> InputState:
        pass
