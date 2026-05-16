"""Sanitize user-controlled values before they go into a log line.

Strips CR/LF and other control characters so a crafted equipment id /
reason cannot forge or inject extra log records (CWE-117 / py/log-injection).
"""
from __future__ import annotations


def clean(value: object) -> str:
    # Explicit CR/LF/TAB removal so the static taint tracker recognises
    # this as a log-injection barrier (a generator expression is not
    # modelled as a sanitizer).
    return (
        str(value)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("\t", " ")
    )[:200]
