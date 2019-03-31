#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.2.3
#
#  Developed in 2019 by Sanskriti Sharma <sanskriti_sharma@student.uml.edu>
#  & Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

# Stdlib imports
from random import randint
import uuid

# 3rd party imports
import numpy as np


class EmployerBee:

    def __init__(self, values=[]):
        '''EmployerBee object: stores individual employer bee information such
        as ID, position (current values), fitness function return value,
        fitness score, and probability of being chosen during the onlooker
        phase

        Args:
            values (list): position/current values for the bee
        '''

        self.values = values
        self.score = None
        self.probability = 0
        self.failed_trials = 0
        self.id = uuid.uuid4()
        self.error = None

    def get_score(self, error=None):
        '''Calculate bee's fitness score given a value returned by the fitness
        function

        Args:
            error (float): value returned by the fitness function

        Returns:
            float: derived fitness score
        '''

        if error is not None:
            self.error = error
        if self.error >= 0:
            return 1 / (self.error + 1)
        else:
            return 1 + abs(self.error)

    def calculate_probability(self, fitness_total):
        '''Calculates the probability that the bee is chosen during the
        onlooker phase

        Args:
            fitness_total (float): sum of fitness scores from all bees
        '''

        self.probability = self.score / fitness_total


class OnlookerBee:

    def __init__(self):
        '''OnlookerBee object: stores best-performing bees, function for
        calculating merged position of two bees
        '''

        self.best_employers = []

    def calculate_positions(self, first_bee_val, second_bee_val, value_range):
        '''Calculate the new value/position for two given bee values

        Args:
            first_bee_val (int or float): value from the first bee
            second_bee_val (int or float): value from the second bee
            value_ranges (tuple): "(value type, (min_val, max_val))" for the
                given value

        Returns:
            int or float: new value
        '''

        value = first_bee_val + np.random.uniform(-1, 1) \
            * (first_bee_val - second_bee_val)
        if value_range[0] == 'int':
            value = int(value)
        if value > value_range[1][1]:
            value = value_range[1][1]
        if value < value_range[1][0]:
            value = value_range[1][0]

        return value
