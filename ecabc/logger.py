#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/logger.py
#  v.1.2.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program sets up the logger for the artificial bee colony
#

import os
import logging
import datetime

### Setup logger
def get_logger(printLevel):
    logger = logging.getLogger('abc_logger')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('logs/{}.log'.format(datetime.datetime.now()))
    fh.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(printLevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

def setup_folder():
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
    except Exception as e:
        raise e