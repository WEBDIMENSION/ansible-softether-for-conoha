#!/usr/bin/env python
""" This is a deploy for ansible program. """
import conoha.deploy as obj

obj.before_exec()
obj.exec()
obj.after_exec()
