![Proman Logo](./assets/logo.jpg)

# Proman - A developer friendly PROcess MANager

Proman is a programmer-friendly, extensible process manager written in Python. It is designed to work on any operating system and provides a unified interface for managing processes in your projects. With Proman, you can define, monitor, and control your processes using a YAML configuration file, a command-line interface (CLI), or a web-based dashboard.

## Table of Contents

- [Proman - A developer friendly PROcess MANager](#proman---a-developer-friendly-process-manager)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Using pip](#using-pip)
    - [From Source](#from-source)
  - [Getting Started](#getting-started)
    - [YAML Configuration](#yaml-configuration)
      - [Example `processes.yaml`](#example-processesyaml)
    - [Running Proman](#running-proman)
      - [Basic Usage](#basic-usage)
      - [Additional CLI Options](#additional-cli-options)
    - [Web Dashboard](#web-dashboard)
  - [Extending Proman](#extending-proman)
    - [Creating a Custom Process](#creating-a-custom-process)
  - [Project Structure](#project-structure)

## Features

- **Cross-Platform:** Runs on any OS that supports Python.
- **Extensible:** Easily extend with custom process classes and functionalities.
- **Multiple Process Types:** Supports both Python processes and shell processes out-of-the-box.
- **YAML Configuration:** Define processes using a simple YAML syntax with tags (e.g., `!PythonProcess`, `!ShellProcess`).
- **Web Interface:** Built-in web dashboard (via FastAPI) for real-time process monitoring and control.
- **CLI Support:** Simple command-line interface for starting the process manager and dynamically loading extension modules.
- **Dynamic Extension Loading:** Extend Proman by loading additional modules at runtime.

## Installation

Proman requires Python 3.6 or higher.

### Using pip

If Proman is published on PyPI, install it with:

```bash
pip install py-proman
```

### From Source

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/proman.git
cd proman
pip install .
```

## Getting Started

### YAML Configuration

Proman uses a YAML configuration file (e.g., `processes.yaml`) to define processes. The configuration leverages YAML tags to instantiate process objects based on the available process classes (see [processes.py](./proman/processes.py)).

#### Example `processes.yaml`

```yaml
# processes.yaml
process_foo: !PythonProcess
  target: "path/to/foo.py"
  args: [1, "flag-2", true]
  kwargs:
    flag3: true
    flag5: false

process_bar: !ShellProcess "command='echo Hello World'"
```

- **process_foo:** A Python process that runs a script with specified arguments and keyword arguments.
- **process_bar:** A shell process that executes a command.

The YAML multi-constructor (implemented in [config.py](./proman/config.py)) automatically instantiates and initializes the process classes based on these tags.

### Running Proman

Proman comes with a CLI for managing processes. The main command is `proman run`.

#### Basic Usage

```bash
proman run processes.yaml
```

This command will:
- Parse the `processes.yaml` file.
- Initialize all defined processes.
- Automatically start processes that are marked as active.

#### Additional CLI Options

- **Load Extensions:** Dynamically load extension modules to add or override functionalities.

  ```bash
  proman run processes.yaml --extension path/to/extension1.py path/to/extension2.py
  ```

- **Specify Host and Port:** Set the host and port for the web dashboard.

  ```bash
  proman run processes.yaml --host 0.0.0.0 --port 8080
  ```

- **Headless Mode:** Run without launching the web interface.

  ```bash
  proman run processes.yaml --headless
  ```

For more details, refer to the CLI implementation in [cli.py](./proman/cli.py).

### Web Dashboard

When not in headless mode, Proman launches a web dashboard powered by FastAPI ([server.py](./proman/server.py)).

- **Dashboard URL:** By default, the dashboard is accessible at `http://localhost:5678` (or at the host/port you specify).
- **Features:**
  - View current status of all registered processes.
  - Start or stop individual processes via the provided buttons.
  - Inspect detailed information about each process.

## Extending Proman

Proman is designed with extensibility in mind. You can create custom process classes by subclassing the base `Process` class (defined in [processes.py](./proman/processes.py)).

### Creating a Custom Process

Below is a sample custom process implementation to run Streamlit applicatons:

```python
import subprocess
import sys
from proman.processes import Process


class StreamlitProcess(Process):
    def initialize(self, config):
        self.target = config.get("target")
        self.port = config.get("port", 9501)
        self.host = config.get("host", "localhost")
        self.interpreter_path = config.get("interpreter_path", sys.executable)
        self.process = None

    def start(self):
        executable = self.interpreter_path
        cmd = [
            executable, "-m", "streamlit", "run", self.target,
            "--server.port", str(self.port),
            "--server.address", self.host,
            "--server.headless", "true"
        ]
        self.process = subprocess.Popen(cmd)

    def stop(self):
        self.process.terminate()
        self.process.wait(timeout=5)
        self.status = "stopped"

    def describe(self):
        return {
            "port": self.port,
            "host": self.host,
            "interpreter_path": self.interpreter_path,
            "link": f"<a href='http://{self.host}:{self.port}/' target='_blank'> http://{self.host}:{self.port}/ </a>",
        }

```

After saving your custom process (e.g., as `custom_process.py`), load it using the `--extension` flag:

```bash
proman run processes.yaml --extension path/to/custom_process.py
```

This flexibility allows you to integrate Proman into a wide range of applications.

## Project Structure

```
proman/
├── __init__.py
├── cli.py             # Command-line interface for Proman
├── config.py          # YAML configuration parser and process initializer
├── environment.py     # Utilities to validate Python interpreter paths
├── manager.py         # Core process manager implementation
├── paths.py           # Path resolution utilities
├── processes.py       # Base process class and standard implementations (PythonProcess, ShellProcess)
└── server.py          # Web server and dashboard for process management
```


