from mike_simulator.input import InputHandler, InputMethod
from mike_simulator.input.backends import *

# Dict for looking up class corresponding to InputMethod
_input_class_for_type = {
    InputMethod.Gamepad: GamepadInputHandler,
    InputMethod.Keyboard: KeyboardInputHandler,
}


class InputHandlerFactory:
    @staticmethod
    def create(method: InputMethod) -> InputHandler:
        """Create an input handler instance for the specified InputMethod."""
        return _input_class_for_type[method]()
