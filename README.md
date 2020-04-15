## Build Instructions (Windows)

#### Prerequisites
Install the latest Python 3 release from https://www.python.org/downloads/
During installation, ensure that the box "Add Python to PATH" is ticked.

#### Building standalone exe
Simply double click build.bat, which will create a standalone executable file of the simulator.
The resulting executable should then be portable, i.e. it should be able to run on any Windows system (even without a Python installation).

## Usage
Simply start the simulator before starting the frontend and close it after the frontend has terminated.

If you are using the frontend version from [here](https://gitlab.ethz.ch/RELab/eth-mike/eth-mike-front-end/tree/debug-needle),
you can rename the simulator executable to `UDPService.exe` and drop it into the Unity project folder (when running from Editor) or next to the ETH Mike.exe (when running standalone build).
Starting and closing of the simulator should then happen automatically.
