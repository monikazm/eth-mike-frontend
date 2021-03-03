# Simulator Documentation (Python)

Note: remember to update with when variable names are changed (after code cleanup)

This document provides an overview of how to add a new assessment / exercise task 

## Code structure - overview

`main.py` and `server.py` generate the ftp server so that the simulator can act as an input to the frontend (instead of myRIO). To run the whole program from the terminal you would need to run `main.py` (see [readme](https://gitlab.ethz.ch/RELab/eth-mike/eth-mike-simulator/-/blob/master/README.md))

`simulator.py` simulates backend states and comunication with the frontend (e.g. displays message "Received {data}" when patient response received, i.e. button pressed)

`logger.py` defines assessment task names (need to correspond to the name in FrontEnd) and what normally be logged in TDMS file on myRIO (e.g. Time [s])

`datamodels.py` defines some properties of the simulator (e.g. MAX_FORCE = 50.0, this is linked to the fact that the physical sensor we are using can only go up to 50 N, so we want to have this constraint in the simulator too). It also creates Enums like we have in LabVIEW (e.g. Enum with all differnt tasks - order needs to correspond to the one in Frontend)

Folders: input, auto_movememnt, assessment. Each of them have the same structure - it contains interface (abstract class), factory and subfolder with specific implementation. Factory chooses which of the specific implementations defined in the subfolder are used in the code (e.g. `input/factory.py` points to gamepad and kayboard inputs, which are defined inside `input/backends` subfolder). 

* input: how simulator is controlled (keyboard and gamepad)
* auto_movement: what kind of trajectories we simulate (currently: linear and sinusoidal) - in the hardware this would be implemented in a PID controller to make the robot move
* assessment: (TO BE CHAGED TO TASKS) where all tasks are defined (both assessments and exercises)

## How to add a new task to the simulator

See [here](https://gitlab.ethz.ch/RELab/eth-mike/eth-mike-simulator/-/commit/791746397fc2cc8343fca8536fd2140a70f5d535) for a commit where a new task (Teach and Reproduce exercise)was added as an example. 

1. Go to `logger.py` and add `AssessmentType.NewTask: 'NewTask',` at the end of the existing list. 
2. If your implementing an "active" task (patient needs to move, i.e. requires keyboard/gamepad input), go to `input/backends/kayboard_input.py` and `input/backends/gamepad_input.py` and add your new task to the list (see other tasks for guidance). 
3. In `datamodels.py`add your task to the class AssessmentType (NOTE: naming needs to be changed to TaskType). 
4. Add a new file to `assessment/modes` folder and give it a name corresponding to your new task name (follow the format `new_task.py`)
5. Copy and paste one of the existing tasks that is the closest to what you want to do and modify what's neccessary. Define what does the simulator do in `on_start` and `on_update` (every loop)
6. Add your new task to `assessment/modes/__init__.py`
7. Add your new task to `assessment/factory.py`
8. Run the code - either by rebuiding the simulator with the build.bat or directly from the Pycharm terminal (see [readme](https://gitlab.ethz.ch/RELab/eth-mike/eth-mike-simulator/-/blob/master/README.md) for the command to use)




