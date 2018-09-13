#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/logger.py
#  v.2.0.0
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program sets up the logger for the artificial bee colony, a wrapper around the python logging class
#

import os
import logging
import datetime

class Logger:

    def __init__(self, print_level, logger_name):
        self.__logger = logging.getLogger(logger_name)
        self.__logger.setLevel(logging.DEBUG)
        self.__folder = datetime.datetime.now()
        self.__log_levels = {
            logging.DEBUG : "Debug",
            logging.INFO : "Info",
            logging.WARN : "Warn", 
            logging.ERROR : "Error", 
            logging.FATAL : "Fatal",
            logging.NOTSET : "All"
        }
        self.__setup_folders()
        self.__setup_file_handlers()
        self.__setup_stream_handler(print_level)

    def debug(self, message, *args, **kwargs):
        self.__logger.debug(message)

    def info(self, message, *args, **kwargs):
        self.__logger.info(message)

    def warn(self, message, *args, **kwargs):
        self.__logger.warn(message)

    def fatal(self, message, *args, **kwargs):
        self.__logger.fatal(message)

    ### Set up various files logger will be outputting to
    def __setup_file_handlers(self):
        for log_level in self.__log_levels:
            fh = logging.FileHandler('logs/{}/{}.log'.format(self.__folder, self.__log_levels[log_level]))
            fh.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            if log_level != logging.NOTSET:
                fh.addFilter(MyFilter(log_level))
            self.__logger.addHandler(fh)

    ### Set up stream handler to output data to console
    def __setup_stream_handler(self, print_level):
        sh = logging.StreamHandler()
        sh.setLevel(print_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        sh.setFormatter(formatter)
        self.__logger.addHandler(sh)

    ### Set up folder hierarchy
    def __setup_folders(self):
        try:
            if not os.path.exists('logs/{}'.format(self.__folder)):
                os.makedirs('logs/{}'.format(self.__folder))
        except Exception as e:
            raise e

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level
