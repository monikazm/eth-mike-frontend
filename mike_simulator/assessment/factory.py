from mike_simulator.assessment import Assessment
from mike_simulator.assessment.modes import *
from mike_simulator.datamodels import TaskType

# Dict for looking up class corresponding to assessment type
_assessments_class_for_type = {
    TaskType.Force: ForceAssessment,
    TaskType.PositionMatching: PositionMatchingAssessment,
    TaskType.RangeOfMotion: RangeOfMotionAssessment,
    TaskType.Motor: MotorAssessment,
    TaskType.SensoriMotor: SensoriMotorAssessment,
    TaskType.PreciseReaching: PreciseReachAssessment,
    TaskType.PassiveMatching: PassiveMatchingAssessment,
    TaskType.ActiveMatching: ActiveMatchingAssessment,
    TaskType.TeachAndReproduce: TeachAndReproduceAssessment,
}


class AssessmentFactory:
    @staticmethod
    def create(assessment: TaskType, motor_state, patient_data) -> Assessment:
        if (_assessments_class_for_type.get(assessment) is None):
            raise ValueError('TaskType unknown')
        return _assessments_class_for_type[assessment](motor_state, patient_data)
