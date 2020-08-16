#!/usr/bin/env python
""" This is a testinfra for ansible program. """
import docker as obj

obj.before_exec()
obj.exec()
obj.after_exec()
