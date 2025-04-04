import subprocess
import sys
from typing import Literal

from proman.environment import is_valid_python_interpreter

# ------------------------------------------------------------------------------
# Base Process class with automatic subclass registration
# ------------------------------------------------------------------------------


class Process:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Automatically register subclasses using their class name.
        Process.registry[cls.__name__] = cls

    def __init__(self):
        # Empty constructor – all configuration is done in initialize().
        pass

    def _initialize(self, config):
        """
        Initialize the process with configuration data.
        Subclasses must override this method.
        """
        self.status: Literal["not started", "running", "stopped", "failed", "error"] = (
            "not started"
        )
        self.active = bool(config.get("active", True))
        self.initialize(config)

    def _start(self):
        if self.status == "running":
            print(f"Process '{self.name}' is already running.")
            return

        self.status = "running"

        try:
            self.start()
            print(f"Process '{self.name}' started with PID {self.process.pid}.")
        except Exception as e:
            print(f"nProcess '{self.name}' encountered an error: {e}")
            self.status = "failed"

    def _stop(self):
        if self.status != "running":
            print(f"Process '{self.name}' is not running, cannot stop.")

        try:
            self.stop()
            print(f"Process '{self.name}' terminated.")
        except Exception as e:
            print(f"Process '{self.name}' failed to terminate: {e}")
            self.status = "error"

    def _describe(self):
        base_info = {"name": self.name, "status": self.status}
        info = self.describe()
        base_info.update(info)
        print(f"Describing {base_info}")
        return base_info

    def initialize(self, config):
        raise NotImplementedError("Subclasses must implement initialize()")

    def start(self):
        raise NotImplementedError("Subclasses must implement start()")

    def stop(self):
        raise NotImplementedError("Subclasses must implement stop()")

    def describe(self):
        """Return info specific to the process"""
        return {}


# ------------------------------------------------------------------------------
# Standard Process subclasses
# ------------------------------------------------------------------------------


class PythonProcess(Process):
    def __init__(self):
        # Empty constructor.
        self.name = None
        self.target = None
        self.args = []
        self.kwargs = {}
        self.process = None

    def initialize(self, config):
        # Populate attributes from configuration.
        self.name = config.get("name")
        self.target = config.get("target")
        self.args = config.get("args", [])
        self.kwargs = config.get("kwargs", {})

    def _get_interpreter_path(self):
        if "interpreter_path" in self.kwargs:
            interpreter_path = self.kwargs.get("interpreter_path")
            if is_valid_python_interpreter(interpreter_path):
                return interpreter_path

        return sys.executable

    def start(self):

        executable = self._get_interpreter_path()
        cmd = [executable, self.target] + [str(arg) for arg in self.args]
        self.process = subprocess.Popen(cmd, **self.kwargs)

    def stop(self):
        self.process.terminate()
        self.process.wait(timeout=5)
        self.status = "stopped"

    def describe(self):
        info = {
            "target": self.target,
            "args": self.args,
        }
        info.update(self.kwargs)
        return info

    def __repr__(self):
        return (
            f"<PythonProcess name={self.name}, target={self.target}, "
            f"args={self.args}, kwargs={self.kwargs}, status={self.status}>"
        )


class ShellProcess(Process):
    def __init__(self):
        self.name = None
        self.command = None

    def initialize(self, config):
        super().initialize(config)
        self.name = config.get("name")
        self.command = config.get("command")

    def start(self):
        self.process = subprocess.Popen(self.command, shell=True)
        self.status = "running"

    def stop(self):
        self.process.terminate()
        self.process.wait()
        self.status = "stopped"

    def __repr__(self):
        return f"<ShellProcess name={self.name}, command={self.command}, status={self.status}>"
