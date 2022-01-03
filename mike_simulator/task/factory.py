from mike_simulator.task import Task
from mike_simulator.task.types import *
from mike_simulator.datamodels import TaskType

# Dict for looking up class corresponding to task type
from mike_simulator.task.types.trajectory_perception import TrajectoryPerceptionAssessment

_tasks_class_by_type = {
    TaskType.Force: ForceAssessment,
    TaskType.PositionMatching: PositionMatchingAssessment,
    TaskType.RangeOfMotion: RangeOfMotionAssessment,
    TaskType.Motor: MotorAssessment,
    TaskType.SensoriMotor: SensoriMotorAssessment,
    TaskType.PreciseReaching: PreciseReachAssessment,
    TaskType.PassiveMatching: PassiveMatchingAssessment,
    TaskType.ActiveMatching: ActiveMatchingAssessment,
    TaskType.TeachAndReproduce: TeachAndReproduceAssessment,
    TaskType.HapticBump: HapticBumpAssessment,
    TaskType.TrajectoryPerception: TrajectoryPerceptionAssessment,
}


class TaskFactory:
    @staticmethod
    def create(task: TaskType, motor_state, patient_data) -> Task:
        if (_tasks_class_by_type.get(task) is None):
            raise ValueError('TaskType unknown')
        return _tasks_class_by_type[task](motor_state, patient_data)
