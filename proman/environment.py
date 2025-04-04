import os
import subprocess


def is_valid_python_interpreter(path):
    if not os.path.isfile(path) or not os.access(path, os.X_OK):
        return False
    try:
        output = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT)
        return output.decode().strip().startswith("Python")
    except Exception:
        return False
