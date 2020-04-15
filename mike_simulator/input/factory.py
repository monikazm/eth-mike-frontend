from enum import Enum

from mike_simulator.input import InputHandler
from mike_simulator.input.backends import *


class InputMethod(Enum):
    Gamepad = GamepadInputHandler
    Keyboard = KeyboardInputHandler
    #Prerecorded
    #Random


class InputHandlerFactory:
    @staticmethod
    def create(method: InputMethod) -> InputHandler:
        """Create an input handler instance for the specified InputMethod."""
        return method.value()
