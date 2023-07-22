#!/usr/bin/env python3

import logging
import os

# creates path to a log file if it doesn't exist, that's all!
class EnhancedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None, errors=None):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime, errors)