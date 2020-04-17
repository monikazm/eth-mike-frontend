from enum import Enum

from .interface import InputHandler, InputState


class InputMethod(Enum):
    Gamepad = 0
    Keyboard = 1
    #Prerecorded
    #Random
