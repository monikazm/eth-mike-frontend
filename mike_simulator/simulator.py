import time
from enum import Enum
from typing import Optional

import XInput as xinput

from mike_simulator.assessment.factory import Assessment, AssessmentFactory
from mike_simulator.datamodels import ControlResponse, PatientResponse, MotorState, Constants
from mike_simulator.input.factory import InputMethod, InputHandlerFactory
from mike_simulator.util import PrintUtil


# Simulator states, transitions occur based on control signals
class SimulatorState(Enum):
    DISABLED = 0
    WAITING_FOR_PATIENT = 1
    READY = 2
    RUNNING = 3


class BackendSimulator:
    def __init__(self):
        self.current_patient: PatientResponse = PatientResponse()
        self.current_state = SimulatorState.DISABLED
        self.current_assessment: Optional[Assessment] = None

        self.last_update = -1
        if any(xinput.get_connected()):
            self.input_handler = InputHandlerFactory.create(InputMethod.Gamepad)
        else:
            self.input_handler = InputHandlerFactory.create(InputMethod.Keyboard)

        self._reset()

    def update_patient_data(self, data: PatientResponse):
        PrintUtil.print_normally(f'Received {data}')
        self.current_patient = data
        self._reset()
        self.current_assessment = AssessmentFactory.create(data.AssessmentMode)
        self.input_handler.begin_assessment(self.current_assessment)

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
            self.current_assessment.on_start(self.current_motor_state, self.input_handler)
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
        self.current_motor_state = MotorState.new(self.current_patient)
        self.current_assessment = None
        self.start_time = time.time_ns()
        self.input_handler.finish_assessment()

    def _update_motor_state(self):
        # Compute delta time
        current_time = time.time_ns()
        delta_time = (current_time - self.last_update) / 1_000_000_000
        self.last_update = current_time

        # Update user input state
        self.input_handler.update_input_state(self.current_motor_state, delta_time)

        # Update motor state based on user input
        input_state = self.input_handler.current_input_state
        pos = self.current_motor_state.Position
        self.current_motor_state.Force = input_state.force
        self.current_motor_state.Position = self.clamp_position(pos + input_state.velocity * delta_time)

        # Update assessment state (if any)
        if self.current_assessment is not None:
            self.current_assessment.on_update(self.current_motor_state, self.input_handler)

            # Check if assessment is finished
            if self.current_assessment.is_finished():
                self.input_handler.finish_assessment()
                self.current_assessment = None
                self.current_motor_state = MotorState.new(self.current_patient, Finished=True)

        # Update the time value from motor state
        self.current_motor_state.Time = ((time.time_ns() - self.start_time) // 1_000_000) / 1000.0

        # TODO log input and motor state

        # Wait 1ms to simulate 1kHz update frequency, accuracy of this depends on OS
        time.sleep(Constants.ROBOT_CYCLE_TIME)

    @staticmethod
    def clamp_position(pos: float):
        return min(max(Constants.MIN_POSITION, pos), Constants.MAX_POSITION)
