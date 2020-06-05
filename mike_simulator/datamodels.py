import math
from dataclasses import dataclass
from enum import IntEnum

from mike_simulator.auto_movement import AutoMover
from mike_simulator.util import PrintUtil


class UInt8(int):
    def __new__(cls, *args, **kwargs):
        return super(UInt8, cls).__new__(cls, *args)


class UInt32(int):
    def __new__(cls, *args, **kwargs):
        return super(UInt32, cls).__new__(cls, *args)


class Int32(int):
    def __new__(cls, *args, **kwargs):
        return super(Int32, cls).__new__(cls, *args)


class Constants:
    # Log to csv every n_th cycle
    LOG_CYCLES = 3

    # Robot cycle time [s]
    ROBOT_CYCLE_TIME = 0.001

    # Robot movement bounds [deg]
    MIN_POSITION = -90.0
    MAX_POSITION = 90.0

    # Constant to derive force from acceleration [kg]
    MASS_CONSTANT = 0.3

    # Maximum measurable force [N]
    MAX_FORCE = 50.0

    # Maximum measurable speed [deg / s]
    MAX_SPEED = 800.0

    # Maximum speed for non-burst movement [deg / s]
    USER_NORMAL_MAX_SPEED = 80.0

    # Rates at how digital input changes applied force [N / s]
    USER_FORCE_ACCEL_RATE = 30.0

    # Rates at how velocity accelerates when simulating burst movement [deg / s^2]
    USER_BURST_ACCEL_RATE = 2200.0


class RomState(IntEnum):
    ActiveMotion = 0
    PassiveMotion = 1
    AutomaticPassiveMovement = 2


class AssessmentType(IntEnum):
    Disabled = -1
    Force = 1
    RangeOfMotion = 0
    PositionMatching = 4
    Motor = 2
    SensoriMotor = 3


@dataclass
class ControlResponse:
    EmergencyStop: bool = False
    Start: bool = False
    Restart: bool = False
    FrontendStarted: bool = False
    Close: bool = False


@dataclass
class PatientResponse:
    LeftHand: bool = False
    AssessmentMode: AssessmentType = AssessmentType.Disabled
    SubjectNr: str = ''
    DateTime: str = ''
    PhaseTrialCount: Int32 = 0


@dataclass
class MotorState:
    Counter: UInt32 = 0
    Time: float = 0.0
    Position: float = 0.0
    StartingPosition: float = 0.0
    TargetPosition: float = 0.0
    Force: float = 0.0
    Velocity: float = 0.0
    TrialNr: UInt8 = 0
    RomState: RomState = RomState.ActiveMotion
    LeftHand: bool = False
    TargetState: bool = False
    Finished: bool = False
    Flexion: bool = True

    @staticmethod
    def new(patient: PatientResponse, **kwargs) -> 'MotorState':
        """
        Initialize a new MotorState for the given patient information.

        :param patient: patient information to use for the new motor state
        :param kwargs: used to specify values of additional MotorState fields
        :return: new motor state instance
        """
        assert 'StartingPosition' not in kwargs
        left = patient.LeftHand
        return MotorState(LeftHand=left, **kwargs)

    def move_using(self, auto_mover: AutoMover) -> AutoMover.MovementState:
        """
        Move the robot position using the given mover.

        :param auto_mover: mover object which should update the current position
        :return: MovementState which stores whether the movement described by auto_mover has finished
        """
        self.Position, state = auto_mover.get_current_position_and_state()
        PrintUtil.print_inplace(f'Current robot position: {self.Position:.3f}°')
        return state

    def move_target_using(self, auto_mover: AutoMover) -> AutoMover.MovementState:
        """Move the robot's *target* position using the given mover."""
        self.TargetPosition, state = auto_mover.get_current_position_and_state()
        PrintUtil.print_inplace(f'Current robot position: {self.Position:.3f}°, target position: {self.TargetPosition:.3f}°')
        return state

    def is_at_position(self, position: float) -> bool:
        """Check whether the robot is currently at the specified position (in [deg])."""
        return math.fabs(position - self.Position) < 0.0001
