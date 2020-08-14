import csv
import os
import random
from datetime import datetime

from mike_simulator.config import cfg
from mike_simulator.datamodels import MotorState, PatientResponse, AssessmentType
from mike_simulator.input import InputState


class Logger:
    FIELDS = (
        'Time [s]', 'Position [deg]', 'Target Position [deg]', 'Frontend Started', 'Trial Nr', 'Velocity [deg/s]',
        'Current [A]', 'Starting position [deg]', 'Left Hand? ', 'Voltage force [V]', 'Force [N]', 'Force filtered [N]',
        'Velocity unfiltered', 'ROM State 0-Active 1-Passive 2-Automatic,Acceleration'
    )

    TASK_NAMES = {
        AssessmentType.Force: 'Force Task',
        AssessmentType.PositionMatching: 'Position Matching Task',
        AssessmentType.RangeOfMotion: 'Range of Motion Task',
        AssessmentType.Motor: 'Motor Task',
        AssessmentType.SensoriMotor: 'Sensorimotor Task',
        AssessmentType.PreciseReaching: 'Precise Reaching Task',
    }

    def __init__(self, patient: PatientResponse):
        # Create directories if needed
        directory = os.path.join(cfg.Logging.log_dir,
                                 cfg.Logging.data_dir,
                                 patient.SubjectNr,
                                 Logger.TASK_NAMES[patient.AssessmentMode],
                                 f'{"Left" if patient.LeftHand else "Right"} Hand')
        os.makedirs(directory, exist_ok=True)

        # Create log file
        self.file = open(os.path.join(directory, f'{patient.DateTime}.csv'), 'w', buffering=1, newline='')

        # Open csv writer for log file
        self.writer = csv.writer(self.file)
        self.writer.writerow(Logger.FIELDS)

    def __del__(self):
        self.file.close()

    def log(self, elapsed_time: float, motor_state: MotorState, frontend_started: bool, input_state: InputState):
        row = (
            elapsed_time,
            motor_state.Position,
            motor_state.TargetPosition,
            1 if frontend_started else 0,
            motor_state.TrialNr,
            input_state.velocity, # filtered velocity, for now == unfiltered
            'nan', # Current
            motor_state.StartingPosition,
            1 if motor_state.LeftHand else 0,
            input_state.force / 10 + random.gauss(0.0, 0.1), # Voltage force
            input_state.force,
            input_state.force, # filtered force, for now == unfiltered
            input_state.velocity,
            int(motor_state.RomState)
        )
        self.writer.writerow([str(elem) for elem in row])
