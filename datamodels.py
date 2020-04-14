import math
from dataclasses import dataclass
from enum import IntEnum

from dataclasses_json import dataclass_json

from auto_movement import AutomaticMovement
from util import PrintUtil


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


@dataclass_json
@dataclass
class MotorState:
    LeftHand: bool = False
    Position: float = 0.0
    StartingPosition: float = 0.0
    TargetPosition: float = 0.0
    Time: float = 0.0
    TrialNr: int = 0
    TargetState: bool = False
    Finished: bool = False
    Flexion: bool = True
    RomState: RomState = RomState.ActiveMotion
    Force: float = 0.0

    @staticmethod
    def new(patient: 'PatientResponse', **kwargs) -> 'MotorState':
        assert 'StartingPosition' not in kwargs
        left = patient.LeftHand
        return MotorState(LeftHand=left, StartingPosition=(30.0 if left else -30.0), **kwargs)

    def move_using(self, auto_mover: AutomaticMovement) -> AutomaticMovement.MovementState:
        self.Position, state = auto_mover.get_current_position_and_state()
        PrintUtil.print_inplace(f'Current robot position: {self.Position:.3f}°')
        return state

    def move_target_using(self, auto_mover: AutomaticMovement) -> AutomaticMovement.MovementState:
        self.TargetPosition, state = auto_mover.get_current_position_and_state()
        PrintUtil.print_inplace(f'Current robot position: {self.Position:.3f}°, target position: {self.TargetPosition:.3f}°')
        return state

    def is_at_position(self, position: float) -> bool:
        return math.fabs(position - self.Position) < 0.0001


@dataclass_json
@dataclass
class ControlResponse:
    EmergencyStop: bool = False
    Start: bool = False
    Restart: bool = False
    FrontendStarted: bool = False
    Close: bool = False


@dataclass_json
@dataclass
class PatientResponse:
    SubjectNr: str = ''
    LeftHand: bool = False
    AssessmentMode: AssessmentType = AssessmentType.Disabled
    DateTime: str = ''
