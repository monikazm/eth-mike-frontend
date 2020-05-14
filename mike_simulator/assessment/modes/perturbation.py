import random
from enum import IntEnum
from typing import Optional

from mike_simulator.assessment import Assessment
from mike_simulator.auto_movement.factory import AutoMover, AutoMoverFactory
from mike_simulator.config import cfg
from mike_simulator.datamodels import MotorState, PerturbationPhase, PatientResponse
from mike_simulator.input import InputHandler
from mike_simulator.util import PrintUtil, Timer
from mike_simulator.util.helpers import clamp
from mike_simulator.util.perturbation import SpringPerturbation, RampPerturbation, StepPerturbation


class S(IntEnum):
    STANDBY = 0
    MOVING_TO_START = 1
    MOVING_TO_TARGET = 2
    STAYING_AT_TARGET = 3
    RANDOM_DELAY = 4
    PERTURBATION = 5
    RELEASING = 6

    FINISHED = -1


class PerturbationAssessment(Assessment):
    def __init__(self, motor_state: MotorState, patient: PatientResponse) -> None:
        super().__init__(S.STANDBY)
        self.direction = 1.0 if patient.LeftHand else -1.0

        # Used to simulate delays
        self.timer = Timer()

        # 20 trials of 4 different perturbation types in random order
        self.all_perturbs = cfg.Assessments.num_perturbation_trials_per_type * \
                               [RampPerturbation(-15.0 * self.direction, 1.0),
                                RampPerturbation(-30.0 * self.direction, 1.0),
                                StepPerturbation(-9.0 * self.direction),
                                StepPerturbation(-18.0 * self.direction)]
        random.shuffle(self.all_perturbs)

        self.perturb = None

        # Create spring perturbation
        spring_v_max = -15.0 * self.direction
        self.spring_perturb = SpringPerturbation(spring_v_max, 30.0 * self.direction, 60.0 * self.direction)

        # Used for automatic movement to starting position
        self.auto_mover: Optional[AutoMover] = None

        # Set starting/target position and initialize trial
        motor_state.StartingPosition = 30.0 * self.direction
        motor_state.TargetPosition = 60.0 * self.direction
        self._prepare_next_trial_or_finish(motor_state)

    def _prepare_next_trial_or_finish(self, motor_state: MotorState):
        if motor_state.TrialNr == cfg.Assessments.num_perturbation_trials_per_type * 4:
            self.goto_state(S.FINISHED)
        else:
            motor_state.TrialNr += 1
            self.goto_state(S.STANDBY)

    def release_perturbation(self, motor_state):
        if self.spring_perturb is not None:
            self.spring_perturb.release_perturbation(2.0)
        if self.perturb is not None:
            self.perturb.release_perturbation(2.0)
        self.timer.restart(2.0)
        motor_state.PerturbationPhase = PerturbationPhase.ReleasePhase
        self.goto_state(S.RELEASING)

    def on_start(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.STANDBY):
            self.auto_mover = AutoMoverFactory.make_linear_mover(motor_state.Position, motor_state.StartingPosition, 3.0)
            self.goto_state(S.MOVING_TO_START)

    def on_update(self, motor_state: MotorState, input_handler: InputHandler):
        if self.in_state(S.MOVING_TO_START):
            if motor_state.move_using(self.auto_mover).has_finished():
                # Display target
                motor_state.TargetState = True

                # Add spring force in opposite direction of movement
                input_handler.unlock_movement()
                input_handler.add_perturbation(self.spring_perturb)

                # Give user 10 seconds to move to target position (against the force)
                self.timer.start(10.0)
                self.goto_state(S.MOVING_TO_TARGET)

        elif self.in_state(S.MOVING_TO_TARGET):
            if self.timer.has_finished():
                # Abort since target was not reached within 10 seconds
                self.release_perturbation(motor_state)

            if motor_state.is_at_position(motor_state.TargetPosition, 1.0):
                # Once target was reached wait for 5 seconds
                self.timer.restart(5.0)
                motor_state.PerturbationPhase = PerturbationPhase.HoldingPhase
                self.goto_state(S.STAYING_AT_TARGET)

        elif self.in_state(S.STAYING_AT_TARGET):
            if self.timer.has_finished():
                # Wait for random delay between 1 and 3 seconds
                random_delay = random.uniform(1.0, 3.0)
                PrintUtil.print_normally(f"Random delay {random_delay:.2f} s")
                self.timer.start(random_delay)
                motor_state.PerturbationPhase = PerturbationPhase.PerPerturbPhase
                self.goto_state(S.RANDOM_DELAY)
            elif not (motor_state.StartingPosition * self.direction <= motor_state.Position * self.direction <= 85.0):
                # Safety
                self.release_perturbation(motor_state)

        elif self.in_state(S.RANDOM_DELAY):
            if self.timer.has_finished():
                # After random delay has elapsed, start perturbation for 10 seconds
                self.perturb = self.all_perturbs[motor_state.TrialNr]
                input_handler.add_perturbation(self.perturb)
                self.timer.start(10.0)
                motor_state.PerturbationPhase = PerturbationPhase.PerturbApplied
                self.goto_state(S.PERTURBATION)
            elif not (motor_state.StartingPosition * self.direction <= motor_state.Position * self.direction <= 85.0):
                # Safety
                self.release_perturbation(motor_state)

        elif self.in_state(S.PERTURBATION):
            if self.timer.has_finished() or not (0.0 <= motor_state.Position * self.direction <= 85.0):
                # Release perturbations when time is up or if safety is triggered
                self.release_perturbation(motor_state)
            else:
                # Soft safety (linear force decrease below 30 deg)
                perturb_multiplier = clamp(0.0, 1.0, (motor_state.Position * self.direction) / 30.0)
                self.perturb.set_multiplier(perturb_multiplier)

        elif self.in_state(S.RELEASING):
            if self.timer.has_finished():
                # Finish trial when force release is finished
                motor_state.TargetState = False
                input_handler.lock_movement()

                motor_state.PerturbationPhase = PerturbationPhase.InitialPhase
                self._prepare_next_trial_or_finish(motor_state)
            else:
                # Soft safety (linear force decrease below 30 deg)
                perturb_multiplier = clamp(0.0, 1.0, (motor_state.Position * self.direction) / 30.0)
                if self.perturb is not None:
                    self.perturb.set_multiplier(perturb_multiplier)
