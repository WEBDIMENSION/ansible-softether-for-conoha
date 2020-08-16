#!/usr/bin/env python
""" This is a testinfra for ansible program. """

import subprocess

try:
    print("Start tests")
    subprocess.run("tests/tests.py", shell=True, check=True)
except subprocess.CalledProcessError:
    print("can not exec tests.py")
