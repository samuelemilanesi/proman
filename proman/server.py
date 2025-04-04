import webbrowser

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from proman.config import ConfigParser
from proman.paths import toabs


class ProcessManagerWebInterface:
    def __init__(self, config_filepath: str, headless=False):
        self.config_filepath = config_filepath
        self.app = FastAPI()
        self._setup_manager()

        self.headless = headless

        if not self.headless:
            static_dir = toabs(__file__, "./frontend")
            self.app.mount(
                "/static",
                StaticFiles(directory=static_dir),
                name="static",
            )

        self._setup_routes()

    def _setup_manager(self):
        # Initialize the ProcessManager using the YAML configuration.
        config_parser = ConfigParser(self.config_filepath)
        self.manager = config_parser.init_process_manager()

    def _setup_routes(self):
        # Enable CORS to allow requests from any origin.
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/api/status")
        def get_status():
            return {name: proc.status for name, proc in self.manager.processes.items()}

        @self.app.post("/api/start/{process_name}")
        def start_process(process_name: str):
            if process_name not in self.manager.processes:
                raise HTTPException(
                    status_code=404, detail=f"Process '{process_name}' not found"
                )
            self.manager.start_process(process_name)
            return {"result": f"Process '{process_name}' started."}

        @self.app.post("/api/stop/{process_name}")
        def stop_process(process_name: str):
            if process_name not in self.manager.processes:
                raise HTTPException(
                    status_code=404, detail=f"Process '{process_name}' not found"
                )
            self.manager.stop_process(process_name)
            return {"result": f"Process '{process_name}' stopped."}

            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Process Manager Dashboard</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100">
                <div class="container mx-auto p-4">
                    <h1 class="text-3xl font-bold text-center mb-6">Process Manager Dashboard</h1>
                    <div id="status" class="overflow-x-auto"></div>
                </div>
                <script>
                    async function fetchStatus() {
                        const response = await fetch("/api/status");
                        const status = await response.json();
                        let html = `
                        <table class="min-w-full bg-white shadow-md rounded-lg">
                            <thead>
                                <tr>
                                    <th class="py-2 px-4 border-b">Process</th>
                                    <th class="py-2 px-4 border-b">Status</th>
                                    <th class="py-2 px-4 border-b">Actions</th>
                                </tr>
                            </thead>
                            <tbody>`;
                        for (let key in status) {
                            const stat = status[key];
                            const statusColor = stat === "running" ? "text-green-600" :
                                                  stat === "stopped" ? "text-gray-600" :
                                                  stat === "failed" ? "text-red-600" : "text-yellow-600";
                            html += `
                                <tr class="hover:bg-gray-100">
                                    <td class="py-2 px-4 border-b">${key}</td>
                                    <td class="py-2 px-4 border-b ${statusColor}">${stat}</td>
                                    <td class="py-2 px-4 border-b">
                                        <button onclick="startProcess('${key}')" class="bg-green-500 hover:bg-green-600 text-white py-1 px-2 rounded mr-2">Start</button>
                                        <button onclick="stopProcess('${key}')" class="bg-red-500 hover:bg-red-600 text-white py-1 px-2 rounded">Stop</button>
                                    </td>
                                </tr>`;
                        }
                        html += `
                            </tbody>
                        </table>`;
                        document.getElementById("status").innerHTML = html;
                    }
                    
                    async function startProcess(name) {
                        await fetch(`/api/start/${name}`, {method: "POST"});
                        fetchStatus();
                    }
                    
                    async function stopProcess(name) {
                        await fetch(`/api/stop/${name}`, {method: "POST"});
                        fetchStatus();
                    }
                    
                    // Poll every 2 seconds for updates.
                    setInterval(fetchStatus, 2000);
                    fetchStatus();
                </script>
            </body>
            </html>
            """
            return html_content

        @self.app.get("/api/info/{process_name}")
        def process_info(process_name: str):
            if process_name not in self.manager.processes:
                raise HTTPException(
                    status_code=404, detail=f"Process '{process_name}' not found"
                )
            return self.manager.describe_process(process_name)

        if not self.headless:

            @self.app.get("/")
            def serve_index():
                index_file = toabs(__file__, "./frontend/index.html")
                return FileResponse(index_file)

    def run(self, host="localhost", port=5555, debug=True):
        if not self.headless:
            webbrowser.open(f"http://{host}:{port}")

        uvicorn.run(
            self.app, host=host, port=port, log_level="debug" if debug else "info"
        )


if __name__ == "__main__":
    interface = ProcessManagerWebInterface("processes.yaml")
    interface.run()
