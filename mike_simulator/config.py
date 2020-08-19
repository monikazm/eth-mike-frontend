import ast
import os
import socket
from configparser import ConfigParser
from dataclasses import dataclass, asdict, fields

from mike_simulator.input import InputMethod


@dataclass
class IniSection:
    """
    Base class for ini section data classes.

    Ensures that all attributes which are passed to the constructor are converted to the declared types.
    Also calls the validation function which can be used to implement sanity checks for the configuration values.
    """
    def __post_init__(self):
        # Automatic type conversion
        for field in fields(self):
            val = getattr(self, field.name)
            if field.type != str and isinstance(val, str):
                try:
                    setattr(self, field.name, field.type(ast.literal_eval(val)))
                except Exception:
                    raise ValueError(f'{val} could not be parsed or converted to correct type for field {field.name}')
        self.validate()

    def validate(self):
        """
        Validate the fields defined in this ini section

        :raise ValueError: if an invalid configuration value was provided
        """
        raise NotImplementedError()


@dataclass
class Config:
    """
    Data class corresponding to the ini file structure

    Contains one IniSection subclass and a corresponding instance variable for every ini section.
    The name of each of those instance variable defines the ini section name.

    The members of each section class directly correspond to the supported configuration entries,
    i.e. to add a new config option, it is enough to simply add a correspond attribute to one of the section
    classes (or to create a new section class and add it in there).
    """

    @dataclass
    class InputSection(IniSection):
        method: str = 'Keyboard'

        def validate(self):
            supported_input_methods = [v.name for v in InputMethod]
            if self.method not in supported_input_methods:
                raise ValueError(f'Input method must be one of {supported_input_methods}')
    Input: InputSection = InputSection()

    @dataclass
    class LoggingSection(IniSection):
        enabled: bool = True
        log_dir: str = './logs'
        data_root_dir: str = os.path.join('media', 'sda1')

        def validate(self):
            pass
    Logging: LoggingSection = LoggingSection()

    @dataclass
    class NetworkSection(IniSection):
        server_bind_ip: str = '127.0.0.1'

        # Address at which the frontend is listening for the updated motor state
        motor_data_port: int = 6661

        # Addresses at which the simulator should listen for commands and patient data
        control_port: int = 6664
        patient_port: int = 6662

        motor_data_packet_loss_rate: float = 0.0

        simulate_ftp_server: bool = False

        def validate(self):
            try:
                socket.inet_aton(self.server_bind_ip)
            except socket.error:
                raise ValueError('Not a valid ip address')

            for name, value in vars(self).items():
                if 'port' in name and not (0 <= value < (1 << 16)):
                    raise ValueError(f'Network.{name} must be unsigned 16-bit integer')
                if 'loss_rate' in name and not (0.0 <= value <= 1.0):
                    raise ValueError(f'Network.{name} must be between 0 and 1')
    Network: NetworkSection = NetworkSection()

    @dataclass
    class AssessmentsSection(IniSection):
        sensorimotor_movement_duration: float = 30.0

        def validate(self):
            pass
    Assessments: AssessmentsSection = AssessmentsSection()


def load_configuration(filename: str = './simulator_config.ini'):
    """
    Load configuration from specified ini file into the global configuration object 'cfg'.
    If the configuration file does not exist, it is created and populated with the default values as specified
    by the Config dataclass.

    :param filename: path to the configuration ini file
    """
    global cfg
    filename = os.path.realpath(filename)
    config = ConfigParser()
    if os.path.exists(filename):
        # Read configuration file and set cfg entries based on its contents
        config.read(filename)
        for section in config.sections():
            if hasattr(Config, section):
                section_class = type(getattr(Config, section))
                cfg_values = {k: v for k, v in config[section].items() if hasattr(section_class, k)}
                setattr(cfg, section, section_class(**cfg_values))
    else:
        # If no configuration file exists, create one with the default settings as specified by the Config dataclass
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        config.read_dict(asdict(cfg))
        with open(filename, 'w') as cfg_file:
            config.write(cfg_file)


# Global configuration object
cfg: Config = Config()
