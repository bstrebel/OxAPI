#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,json,requests
from oxapi import *


def get_a_task(ox):

    folder = ox.get_standard_folder('tasks')
    task = list(ox.get_tasks(folder.id))[0]
    return task


def get_task(ox):

    TASK=44308
    FOLDER=1958

    # low level get request
    # content = ox.get('tasks','get', {"id": TASK, "folder": FOLDER})
    # print(content['data']['title'])

    # bean factory wrapper
    task = ox.get_task(FOLDER, TASK)
    #print(task.title)
    return task

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

    MyFolder='1958'
    Tasks='246'
    Updated='44308'

    with OxHttpAPI.get_session() as ox:
        #list_tasks(ox)
        task = ox.get_task(Tasks,Updated)
        #data = task.data
        #task.upload([{'content': "Text", 'mimetype': 'text/plain', 'name': 'attachment.txt'}])

        task.load()
        #task.expand()

        #folder = task.folder_id
        #task._data['folder_id'] = '1958'
        #task._data['title'] = 'Updated'
        #id = task.id
        #folder_id = task.folder_id
        #task._data = {'id': id, 'folder_id': folder_id}
        #result = task.move('1958')
        pass




