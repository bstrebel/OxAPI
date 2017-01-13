#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
from oxapi import *

if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:
        result = ox.get("export", "ICAL", {'folder': 1607})
