#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
from pyutils import get_logger;
from oxapi import *

if __name__ == '__main__':

    logger = get_logger("_export", "INFO")

    with OxHttpAPI.get_session(logger=logger) as ox:
        # result = ox.get("export", "ICAL", {'folder': 1607})
        try:
            result = ox.export("126")
            print result
        except ValueError as e:
            logger.error(e.message)
