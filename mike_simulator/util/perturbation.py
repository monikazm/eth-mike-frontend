from abc import ABCMeta, abstractmethod

from mike_simulator.datamodels import MotorState
from mike_simulator.util import get_current_time
from mike_simulator.util.helpers import lerp, clamp


class Perturbation(metaclass=ABCMeta):
    def __init__(self):
        self.release_start_time = None
        self.release_duration = None
        self.multiplier = 1.0

    def set_multiplier(self, val: float):
        self.multiplier = val

    def get_current_perturbation_velocity(self, motor_data: MotorState) -> float:
        v = self._get_raw_perturbation_velocity(motor_data) * self.multiplier
        if self.release_start_time is None:
            return v
        else:
            t = clamp(0.0, 1.0, (get_current_time() - self.release_start_time) / self.release_duration)
            return lerp(v, 0.0, t)

    @abstractmethod
    def _get_raw_perturbation_velocity(self, motor_data: MotorState) -> float:
        pass

    def release_perturbation(self, release_duration: float):
        self.release_start_time = get_current_time()
        self.release_duration = release_duration

    def is_finished(self) -> bool:
        return self.release_start_time is not None and get_current_time() - self.release_start_time > self.release_duration


class SpringPerturbation(Perturbation):
    def __init__(self, v_max: float, start_pos: float, end_pos: float):
        super().__init__()
        self.v_max = v_max
        distance = end_pos - start_pos
        if start_pos < end_pos:
            self.to_t = lambda pos: clamp(0.0, 1.0, (clamp(start_pos, end_pos, pos) - start_pos) / distance)
        else:
            self.to_t = lambda pos: clamp(0.0, 1.0, (clamp(end_pos, start_pos, pos) - start_pos) / distance)

    def _get_raw_perturbation_velocity(self, motor_data: MotorState) -> float:
        return lerp(0.0, self.v_max, self.to_t(motor_data.Position))


class RampPerturbation(Perturbation):
    def __init__(self, v_max: float, ramp_duration: float):
        super().__init__()
        self.start_time = get_current_time()
        self.v_max = v_max
        self.duration = ramp_duration

    def _get_raw_perturbation_velocity(self, _) -> float:
        elapsed = get_current_time() - self.start_time
        normalized_t = clamp(0.0, 1.0, elapsed / self.duration)
        return lerp(0.0, self.v_max, normalized_t)


class StepPerturbation(Perturbation):
    def __init__(self, v: float):
        super().__init__()
        self.v = v

    def _get_raw_perturbation_velocity(self, _) -> float:
        return self.v
