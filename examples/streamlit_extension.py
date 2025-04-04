"""
Example of extension file that defines a "StreamlitProcess" to run streamlit python scripts.
"""

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
        cmd = f"{executable} -m streamlit run {self.target} --server.port {self.port} --server.address {self.host} --server.headless true"
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
