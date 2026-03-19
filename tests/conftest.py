import os
import sys


_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROTO = os.path.join(_ROOT, "proto")
for p in (_ROOT, _PROTO):
    if p not in sys.path:
        sys.path.insert(0, p)
