#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.1.2.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This class handles output for ecabc
#

class Output:

    def __init__(self, print):
        self._print = print

    def print(self, arg):
        if (self._print):
            print(arg)