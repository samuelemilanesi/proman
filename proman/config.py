import ast

import yaml

from proman.manager import ProcessManager
from proman.processes import Process


# ------------------------------------------------------------------------------
# YAML Multi-Constructor for Process classes.
# ------------------------------------------------------------------------------
def process_multi_constructor(loader, tag_suffix, node):
    """
    Handles YAML tags like !PythonProcess, !ShellProcess, or !CustomProcess.
    It looks up the Process subclass in the registry, parses the node into a
    configuration dictionary, instantiates the process using an empty constructor,
    and then calls _initialize() with the parsed configuration.
    """
    cls = Process.registry.get(tag_suffix)
    if cls is None:
        raise ValueError(f"Unknown process class: {tag_suffix}")

    # Parse the node into a config dictionary.
    if isinstance(node, yaml.ScalarNode):
        scalar_val = loader.construct_scalar(node).strip()
        if not scalar_val:
            config_dict = {}
        else:
            tokens = scalar_val.split()
            config_dict = {}
            # Tokens in key=value form are added as keyword arguments.
            # Other tokens are collected under the "args" key.
            for token in tokens:
                if "=" in token:
                    key, val = token.split("=", 1)
                    try:
                        val = ast.literal_eval(val)
                    except Exception:
                        pass
                    config_dict[key] = val
                else:
                    config_dict.setdefault("args", []).append(token)
    elif isinstance(node, yaml.MappingNode):
        config_dict = loader.construct_mapping(node, deep=True)
    else:
        raise ValueError(f"Unsupported node type {node} for process class {tag_suffix}")

    # Instantiate the process with an empty constructor and initialize it.
    instance = cls()
    instance._initialize(config_dict)
    return instance


# Register the multi-constructor for all YAML tags starting with "!"
yaml.add_multi_constructor("!", process_multi_constructor, Loader=yaml.SafeLoader)

# ------------------------------------------------------------------------------
# ConfigParser that instantiates and initializes processes.
# ------------------------------------------------------------------------------


class ConfigParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        with open(self.filepath, "r") as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)

        processes = {}
        # Each key in the YAML mapping corresponds to a process name.
        # The value is already a fully initialized Process instance.
        for process_name, process_instance in config.items():
            if not isinstance(process_instance, Process):
                raise ValueError(
                    f"Process {process_name} did not produce a valid Process instance"
                )
            # If the process's name wasn’t set during initialization, inject it.
            if getattr(process_instance, "name", None) is None:
                process_instance.name = process_name
            processes[process_name] = process_instance
        return processes

    def init_process_manager(self):
        processes = self.parse()
        manager = ProcessManager()
        for _, proc in processes.items():
            manager.register_process(proc)
        return manager


if __name__ == "__main__":
    # Assume the YAML configuration is stored in "processes.yaml".
    #
    # Example YAML file using mapping style:
    #
    # process_foo: !PythonProcess
    #   target: "C:/Users/xyz/Projects/local/foo.py"
    #   args: [1, "flag-2", true]
    #   kwargs:
    #     flag3: true
    #     flag5: false
    #
    # Or scalar shorthand style:
    #
    # process_bar: !ShellProcess "command='source smth.bat'"
    #
    config_parser = ConfigParser("processes.yaml")
    processes = config_parser.parse()
    for name, process in processes.items():
        print(f"{name}: {process}")
