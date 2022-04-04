## Windows Instructions

### Build 

#### Prerequisites
Install the latest Python 3 release from https://www.python.org/downloads/
During installation, ensure that the box "Add Python to PATH" is ticked.

#### Building standalone exe
Simply double click build.bat, which will create a standalone executable file of the simulator.
The resulting executable should then be portable, i.e. it should be able to run on any Windows system (even without a Python installation).

### Usage
Simply start the simulator before starting the frontend and close it after the frontend has terminated.

If you are using the frontend version from [here](https://gitlab.ethz.ch/RELab/eth-mike/eth-mike-front-end/tree/debug-needle),
you can rename the simulator executable to `UDPService.exe` and drop it into the Unity project folder (when running from Editor) or next to the ETH Mike.exe (when running standalone build).
Starting and closing of the simulator should then happen automatically.

If you want to run the simulator from a plain terminal, use
```
python -m mike_simulator.main
```

## Ubuntu Instructions (20.04+)

### Setup Enviroment
It is adviced to install all dependencies in a separated virtual enviroment in order to not override the system dependencies. This can be done using for example venv. 

Install venv using:
```
sudo pip3 install virtualenv
```

Create a virtual enviroment in the project root folder and install dependencies:

```
python3 -m venv .venv
```

Activate the enviroment using: 
```
source .venv/bin/activate
```

Install the dependencies with the activated enviroment:
```
pip install -r requirements.txt 
```

### Usage
If you want to run the simulator simply use: 
```
python -m mike_simulator.main.py
```

## Development
[Pycharm Community](https://www.jetbrains.com/de-de/pycharm/download/#section=windows) is a good, free IDE for python developement.
