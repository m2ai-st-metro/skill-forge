"""Clean fixture: none of these lines may be flagged by the scanner."""

import os
import subprocess
import urllib.request

import yaml


def list_dir():
    # list argv, no shell: not command injection
    return subprocess.run(["ls", "-l"], check=True)


def load_config():
    # constant path, safe loader
    with open("/etc/app/config.yaml") as fh:
        return yaml.safe_load(fh)


# env lookup, not a hardcoded secret
API_KEY = os.environ["API_KEY"]

# secret-shaped words in benign positions
password_prompt = "Enter password:"
token_count = 5


def fetch_status():
    # constant URL: not SSRF
    return urllib.request.urlopen("https://status.example.com/api")


def static_path():
    # constant path join
    return os.path.join("/srv/app", "static")
