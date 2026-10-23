"""Planted fixture for vuln-triage tests: exactly 3 known findings.

Never import or execute this module. The key below is fake (FAKEKEY_ prefix)
and exists only so the scanner has a deterministic secret-shaped target.
"""

import os
import os.path

BASE_DIR = "/srv/app/files"


def run_user_command(user_cmd):
    # PLANTED-1: command injection (os.system with f-string interpolation)
    os.system(f"convert {user_cmd} out.png")


# PLANTED-2: hardcoded fake key
API_KEY = "FAKEKEY_abcdef1234567890"


def read_user_file(request):
    # PLANTED-3: unsafe path join on user-supplied filename
    full = os.path.join(BASE_DIR, request.args["filename"])
    return open(full).read()
