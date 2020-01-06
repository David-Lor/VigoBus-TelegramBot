"""HELPERS
Helper functions for setting loading & parsing
"""

__all__ = ("load_secrets_file",)


def load_secrets_file(path: str, path_startswith: bool) -> str:
    """Read the file from the given path, which should be a Docker-secrets-like file.
    If path_startswith=True, only load the file if the path given starts with "/" or "./".
    """
    if not path_startswith or (path.startswith("/") or path.startswith("./")):
        with open(path, "r") as secrets_file:
            return secrets_file.read().strip()
    else:
        return path
