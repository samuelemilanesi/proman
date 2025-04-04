from proman.processes import Process


class ProcessManager:
    def __init__(self):
        self.processes = {}

    def register_process(self, process: Process):
        self.processes[process.name] = process
        if process.active:
            process._start()
        print(f"Process '{process.name}' added.")

    def start_process(self, name):
        process = self.processes.get(name)
        if process:
            process._start()
        else:
            print(f"No process named '{name}' found.")

    def stop_process(self, name):
        process = self.processes.get(name)
        if process:
            process._stop()
        else:
            print(f"No process named '{name}' found.")

    def describe_process(self, name):
        process = self.processes.get(name)
        if process:
            return process._describe()
        else:
            print(f"No process named '{name}' found.")
            return {}

    def list_processes(self):
        return list(self.processes.keys())

    def start_all(self):
        for process in self.processes.values():
            process._start()

    def stop_all(self):
        for process in self.processes.values():
            process._stop()
