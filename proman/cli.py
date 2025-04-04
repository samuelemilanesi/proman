import argparse
import importlib
from pathlib import Path

from proman import server


def run(config_filepath, host, port, headless):
    app = server.ProcessManagerWebInterface(config_filepath, headless)
    app.run(host=host, port=port)


def load_module_from_path(module_path: str):
    path = Path(module_path)
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")

    # Use the file stem as the module name.
    module_name = path.stem

    # Create a module spec from the absolute path.
    spec = importlib.util.spec_from_file_location(module_name, str(path.resolve()))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for module: {module_path}")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)


def extend_proman(extension_modules_paths):
    for module_path in extension_modules_paths:
        load_module_from_path(module_path)


def main():
    parser = argparse.ArgumentParser(prog="proman", description="PROcess MANager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for the "run" command.
    run_parser = subparsers.add_parser("run", help="Run the process manager")
    run_parser.add_argument("configfilepath", help="Path to the configuration file")
    run_parser.add_argument(
        "--extension", nargs="+", default=[], help="Extension file(s) to load"
    )
    run_parser.add_argument(
        "--host", default="localhost", help="Host address to bind (default: localhost)"
    )
    run_parser.add_argument(
        "--port", type=int, default=5678, help="Port to bind (default: 5678)"
    )
    run_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no web interface)",
    )
    args = parser.parse_args()

    if args.command == "run":
        print(f"Running with config: {args.configfilepath}")
        if args.extension:
            print(f"Loading extensions: {args.extension}")
            extend_proman(args.extension)

        run(args.configfilepath, host=args.host, port=args.port, headless=args.headless)
    else:
        print(
            "Usage: proman run <configfilepath> [--extension <path/to/file1.py> <path/to/file2> ...] [--host <host>] [--port <port>]"
        )


if __name__ == "__main__":
    main()
