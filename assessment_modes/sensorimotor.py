from assessment import Assessment
from datamodels import MotorState


class SensoriMotorAssessment(Assessment):
    def is_finished(self, motor_state: MotorState) -> bool:
        pass

    def on_start(self, motor_state: MotorState):
        pass

    def on_update(self, motor_state: MotorState, directional_input: float, delta_time: float):
        pass
