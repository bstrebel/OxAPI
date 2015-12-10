#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
from oxapi import *

def list_task_folders(ox):

    # for folder in ox._get_beans(OxFolders,'allVisible', {'content_type': 'tasks'}):
    #     print("{} [{}]".format(folder.title, folder.type))

    for folder in ox.get_folders('tasks'):
        print("{} [{}]".format(folder.title, folder.type))

def list_root_folders(ox):

    for folder in ox._get_beans(OxFolders, 'root'):
        print(folder.title)

def standard_task_folder(ox):

    folder = ox.get_standard_folder('tasks')
    print(folder.title)

if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:
        result = ox.get('config/currentTime')

    local = result['data']/1000
    utc = long(time.time())

    offset = long(round((utc-local),-1))
    print(offset/60/60)

