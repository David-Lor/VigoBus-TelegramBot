"""TESTS - UTILS - HELPERS
Random misc helpers
"""

# # Native # #
import socket
import inspect

__all__ = ("clear_markdown", "get_free_port", "get_test_function_name")


def clear_markdown(text: str) -> str:
    """Given a text with Markdown, make it look like the text defined on the messages.yaml file.
    For now just replace double ** or __ with single * or _
    """
    return text.replace("**", "*").replace("__", "_")


def get_free_port() -> int:
    """Return a free TCP port on the current host. To be used as port of Fake APIs during tests.
    """
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_test_function_name():
    """Return the function name of the current callable sequence, where the name starts with test_
    """
    current_frame = inspect.currentframe()
    return next(frame.function for frame in inspect.getouterframes(current_frame) if frame.function.startswith("test_"))
