"""EXCEPTIONS
File-related exceptions
"""

__all__ = ("FileException",)

FileException = (FileNotFoundError, IOError, ValueError, AssertionError)
