"""Register-shift probes (Python): shell=True, unsafe yaml, pickle."""

import os
import pickle
import subprocess

import yaml


def probe(cmd, blob, doc):
    subprocess.run(cmd, shell=True)  # probe: shell=True command injection
    data = yaml.load(doc)  # probe: unsafe yaml load
    obj = pickle.loads(blob)  # probe: unsafe pickle
    return data, obj


def probe_concat(user_input, expr):
    os.system("ls " + user_input)  # probe: os.system string-concat injection
    return eval(expr)  # probe: python eval on untrusted input
