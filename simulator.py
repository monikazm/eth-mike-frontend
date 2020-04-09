import time
from enum import Enum
from typing import Optional

import XInput as xinput
from keyboard import is_pressed

from assessment import Assessment
from assessment_modes.force import ForceAssessment
from assessment_modes.motor import MotorAssessment
from assessment_modes.pos_match import PositionMatchingAssessment
from assessment_modes.rom import RangeOfMotionAssessment
from assessment_modes.sensorimotor import SensoriMotorAssessment
from datamodels import PatientResponse, MotorState, ControlResponse, AssessmentType
from util import PrintUtil


# Simulator states, transitions occur based on control signals
class SimulatorState(Enum):
    DISABLED = 0
    WAITING_FOR_PATIENT = 1
    READY = 2
    RUNNING = 3


# Dict for looking up class corresponding to assessment type
assessments_class_for_type = {
    AssessmentType.Force: ForceAssessment,
    AssessmentType.PositionMatching: PositionMatchingAssessment,
    AssessmentType.RangeOfMotion: RangeOfMotionAssessment,
    AssessmentType.Motor: MotorAssessment,
    AssessmentType.SensoriMotor: SensoriMotorAssessment,
}


class BackendSimulator:
    def __init__(self):
        self.current_patient: PatientResponse = PatientResponse()
        self.current_state = SimulatorState.DISABLED
        self.current_assessment: Optional[Assessment] = None
        self._reset()

        self.last_update = -1
        self.use_gamepad = any(xinput.get_connected())
        Assessment.HAS_ANALOG_INPUT = self.use_gamepad

    def update_patient_data(self, data: PatientResponse):
        PrintUtil.print_normally(f'Received {data}')
        self.current_patient = data
        self.current_motor_state.LeftHand = data.LeftHand
        self.current_assessment = assessments_class_for_type[data.AssessmentMode]()

    def update_control_data(self, data: ControlResponse):
        PrintUtil.print_normally(f'Received {data}')
        if data.EmergencyStop:
            self.current_state = SimulatorState.DISABLED
            self._reset()
        elif data.Restart:
            self.current_state = SimulatorState.WAITING_FOR_PATIENT
            self._reset()
        elif data.Start:
            self.current_state = SimulatorState.RUNNING
            self.current_assessment.on_start(self.current_motor_state)
            self.last_update = time.time_ns()
        elif data.FrontendStarted:
            PrintUtil.print_normally('Frontend started')
            pass
        if data.Close:
            self.current_state = SimulatorState.DISABLED
            self._reset()

    def get_motor_state(self) -> MotorState:
        self._update_motor_state()
        #print(f'Sending {self.current_motor_state}')
        return self.current_motor_state

    def _reset(self):
        self.current_motor_state = MotorState()
        self.start_time = time.time_ns()

    def _update_motor_state(self):
        current_time = time.time_ns()
        delta_time = (current_time - self.last_update) / 1_000_000_000
        self.last_update = current_time

        self.current_motor_state.Time = ((time.time_ns() - self.start_time) // 1_000_000) / 1000
        if self.current_assessment is not None:
            tv = 0.0
            if self.use_gamepad:
                state = xinput.get_state(0)
                tv = xinput.get_thumb_values(state)[0][0]
            tv += float(is_pressed('right') - is_pressed('left'))

            self.current_assessment.on_update(self.current_motor_state, tv, delta_time)
            if self.current_assessment.is_finished():
                self.current_assessment = None
                self.current_motor_state = MotorState(LeftHand=self.current_patient.LeftHand, Finished=True)
