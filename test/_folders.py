#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from oxapi import *

def list_task_folders(ox):

    # for folder in ox._get_beans(OxFolders,'allVisible', {'content_type': 'tasks'}):
    #     print("{} [{}]".format(folder.title, folder.type))

    for folder in ox.get_folders('tasks'):
        folder.expand()
        print("{} [{}]".format(folder.title, folder.type))

def list_root_folders(ox):

    for folder in ox._get_beans(OxFolders, 'root'):
        print(folder.title)

def standard_task_folder(ox):

    folder = ox.get_standard_folder('tasks')
    print(folder.title)

if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:
        list_root_folders(ox)
        list_task_folders(ox)
        standard_task_folder(ox)
