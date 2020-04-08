import math
from dataclasses import dataclass
from enum import IntEnum

from dataclasses_json import dataclass_json


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

    def reached_position(self, position) -> bool:
        return math.fabs(self.Position - position) < 0.5


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
