from pathlib import Path


def toabs(base, relpath):
    return (Path(base).parent / relpath).resolve()
