"""TEST UTILS - HELPERS
Random misc helpers
"""

__all__ = ("clear_markdown",)


def clear_markdown(text: str) -> str:
    """Given a text with Markdown, make it look like the text defined on the messages.yaml file.
    For now just replace double ** or __ with single * or _
    """
    return text.replace("**", "*").replace("__", "_")
