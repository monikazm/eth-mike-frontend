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
    AssessmentType.Perturbation: PerturbationAssessment
}


class AssessmentFactory:
    @staticmethod
    def create(assessment: AssessmentType, patient_data) -> Assessment:
        return _assessments_class_for_type[assessment](patient_data)
