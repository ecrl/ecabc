#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.0.0
#  Developed in 2018 by Sanskriti Sharma <Sanskriti_Sharma@student.uml.edu> and Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This class stores the settings for the the bee colony
#

import json
import os.path
import sys

class Settings:

    def __init__(self, valueRanges, num_employers, filename=None):
        self._valueRanges = valueRanges
        self._num_employers = num_employers
        self._best_values = []
        self._best_score = None
        self._minimize = True

    ### Save the current settings
    def save_settings(self, filename):
        data = dict()
        data['valueRanges'] = self._valueRanges
        data['best_values'] = self._best_values
        data['minimize'] = self._minimize
        data['num_employers'] = self._num_employers
        data['best_score'] = self._best_score
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    ### Import settings to current settings class
    def import_settings(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError('could not open setting file')
        else:
            with open(filename, 'r') as jsonFile:
                data = json.load(jsonFile)
                self._valueRanges = data['valueRanges']
                self._best_values = data['best_values']
                self._minimize = data['minimize']
                self._num_employers = data['num_employers']
                self._best_score = data['best_score']

    ### Update the current best score/values, returns True if scores were updated
    def update(self, score, values):
        if self._minimize: 
            if self._best_score == None or score < self._best_score:
                self._best_score = score
                self._best_values = values
                return True
        elif not self._minimize:
            if self._best_score == None or score > self._best_score:
                self._best_score = score
                self._best_values = values
                return True
        return False

    def get_best(self):
        return (self._best_score, self._best_values)

