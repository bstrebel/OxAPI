#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,json,requests
from oxapi import *


def get_a_task(ox):

    folder = ox.get_standard_folder('tasks')
    task = list(ox.get_tasks(folder.id))[0]
    return task


def get_task(ox):

    TASK=43785
    FOLDER=1956

    # low level get request
    # content = ox.get('tasks','get', {"id": TASK, "folder": FOLDER})
    # print(content['data']['title'])

    # bean factory wrapper
    task = ox.get_task(FOLDER, TASK)
    print(task.title)

def list_tasks(ox):

    folder = ox.get_standard_folder('tasks')
    for task in ox.get_tasks(folder.id):
        print(task.title)
        for attachment in task.attachments:
            print("\t{} ({:d} bytes)".format(attachment.filename,attachment.filesize))
            # if attachment.file_mimetype == 'text/plain':
            #     document = attachment.document

if __name__ == '__main__':

    #from secrets import server, user, password

    with OxHttpAPI.get_session() as ox:
        #list_tasks(ox)
        task = get_a_task(ox)
        #task.upload([{'content': "Text", 'mimetype': 'text/plain', 'name': 'attachment.txt'}])
        task.load()
        folder = task.folder_id
        task._data['folder_id'] = '1958'
        result = task.update(folder=folder)
        pass




