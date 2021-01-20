from mike_simulator.assessment import Assessment
from mike_simulator.assessment.modes import *
from mike_simulator.datamodels import AssessmentType

# Dict for looking up class corresponding to assessment type
_assessments_class_for_type = {
    AssessmentType.Force: ForceAssessment,
    AssessmentType.PositionMatching: PositionMatchingAssessment,
    AssessmentType.RangeOfMotion: RangeOfMotionAssessment,
    AssessmentType.Motor: MotorAssessment,
    AssessmentType.SensoriMotor: SensoriMotorAssessment,
    AssessmentType.PreciseReaching: PreciseReachAssessment,
    AssessmentType.PassiveMatching: PassiveMatchingAssessment,
    AssessmentType.ActiveMatching: ActiveMatchingAssessment,
}


class AssessmentFactory:
    @staticmethod
    def create(assessment: AssessmentType, motor_state, patient_data) -> Assessment:
        if (_assessments_class_for_type.get(assessment) is None):
            raise ValueError('AssessmentType unknown')
        return _assessments_class_for_type[assessment](motor_state, patient_data)
