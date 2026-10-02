import re


def slugify(text):
    """Lowercase, replace runs of non-alphanumerics with a single '-', strip leading/trailing '-'."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]", "-", text)
    return text
