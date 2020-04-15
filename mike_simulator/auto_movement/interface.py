from abc import ABCMeta, abstractmethod
from typing import Tuple


class AutoMover(metaclass=ABCMeta):
    class MovementState:
        def __init__(self, finished: bool):
            self.__finished = finished

        def has_finished(self) -> bool:
            return self.__finished

    @abstractmethod
    def get_current_position_and_state(self) -> Tuple[float, MovementState]:
        """
        Returns the current position on the mover's trajectory.

        The position is determined based on the time which has elapsed since the mover's construction.
        :return: Tuple consisting of the position (in [deg]) and a movement state,
                 which stores whether the movement described by this mover is finished
        """
        pass
