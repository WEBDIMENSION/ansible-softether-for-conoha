#!/usr/bin/env python
""" This is a deploy for ansible program. """
# import subprocess

# try:
#     print("Start flake8")
#     subprocess.run("flake8 deploy/ deploy.py", shell=True, check=True)
# except subprocess.CalledProcessError:
#     print("can not exec ansible-lint")

# try:
#     print("Start ansible-lint")
#     subprocess.run("ansible-lint site.yml", shell=True, check=True)
# except subprocess.CalledProcessError:
#     print("can not exec ansible-lint")

# try:
#     print("Start tests")
#     subprocess.run("deploy/deploy.py", shell=True, check=True)
# except subprocess.CalledProcessError:
#     print("can not exec deploy/deploy.py")
import subprocess

try:
    print("Start deploy")
    subprocess.run("deploy/deploy.py", shell=True, check=True)
except subprocess.CalledProcessError:
    print("can not exec deploy.py")
