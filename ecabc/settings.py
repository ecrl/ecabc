#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.1.2.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This class stores the settings for the the bee colony
#

import json
import os.path
import sys

class Settings:

    def __init__(self, valueRanges, iterationAmount, endValue, amountOfEmployers, filename, processes):
        self._valueRanges = valueRanges
        self._iterationAmount = iterationAmount
        self._amountOfEmployers = amountOfEmployers
        self._filename = filename
        self._bestValues = []
        self._processes = processes
        self._bestScore = None
        self._minimize = True
        self._printFeedback = True
        self._endValue = endValue

    ### Save the current settings
    def saveSettings(self):
        data = dict()
        data['valueRanges'] = self._valueRanges
        data['bestValues'] = self._bestValues
        data['minimize'] = self._minimize
        data['printFeedback'] = self._printFeedback
        data['amountOfEmployers'] = self._amountOfEmployers
        data['bestScore'] = self._bestScore
        data['processes'] = self._processes
        if self._iterationAmount == None:
            data['iterationAmount'] = -1
            data['endValue'] = self._endValue
        else:
            data['iterationAmount'] = self._iterationAmount
            data['endValue'] = -1
        with open(self._filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    ### Import settings to current settings class
    def importSettings(self):
        self._filename = self._filename
        if not os.path.isfile(self._filename):
            raise FileNotFoundError('could not open setting file')
        else:
            with open(self._filename, 'r') as jsonFile:
                data = json.load(jsonFile)
                self._processes = data['processes']
                self._valueRanges = data['valueRanges']
                self._bestValues = data['bestValues']
                self._minimize = data['minimize']
                self._printFeedback = data['printFeedback']
                self._amountOfEmployers = data['amountOfEmployers']
                self._bestScore = data['bestScore']
                if data['iterationAmount'] == -1:
                    self._iterationAmount = None
                    self._endValue = data['endValue']
                else:
                    self._iterationAmount = data['iterationAmount']
                    self._amountOfEmployers = -1

    ### Update the current best score/values
    def update(self, score, values):
        if self._minimize: 
            if score < self._bestScore or self._bestScore == None:
                self._bestScore = score
                self._bestValues = values
        elif not self._minimize:
            if score > self._bestScore or self._bestScore == None:
                self._bestScore = score
                self._bestValues = values

