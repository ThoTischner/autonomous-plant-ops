"""Sanitize user-controlled values before they go into a log line.

Strips CR/LF and other control characters so a crafted equipment id /
reason cannot forge or inject extra log records (CWE-117 / py/log-injection).
"""
from __future__ import annotations


def clean(value: object) -> str:
    s = str(value)
    return "".join(c if c.isprintable() else " " for c in s)[:200]
