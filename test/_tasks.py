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

def test_ox_beans(ox):

    MyFolder='1958'
    Tasks='246'
    Updated='44308'
    OxSync='1963'
    Task='44298'

    with OxHttpAPI.get_session() as ox:

        #list_tasks(ox)
        task = ox.get_task(OxSync,Task)
        #data = task.data
        #task.upload([{'content': "Text", 'mimetype': 'text/plain', 'name': 'attachment.txt'}])

        #task.load()
        #task.expand()

        #folder = task.folder_id
        #task._data['folder_id'] = '1958'
        #task._data['title'] = 'Updated'
        #id = task.id
        #folder_id = task.folder_id
        #task._data = {'id': id, 'folder_id': folder_id}
        #result = task.move('1958')

        # task._data['status'] = OxTask.get_status('In progress')
        # task._data['priority'] = OxTask.get_priority('High')
        # task._data['private_flag'] = False

        #task._data['status'] = -1

        tags = task.tagNames


        cat = task.categories
        task.categories = ['A', 'B']

        cat = task['categories']
        task['categories'] = ['a', 'b']

        cat = task._data['categories']
        task._data['categories'] = ','.join(['A', 'B'])




        task._data['priority'] = 'null'
        task.private_flag = False
        task['private_flag'] = True

        task.update()
        task.load()

        pass

def check_folder_columns(ox, folder):

    assert type(ox) is OxHttpAPI, 'OxHttpAPI session required!'

    folder = ox.get_folder('tasks', folder)
    print folder.title
    tasks = ox.get_tasks(folder.id, ['id', 'title', 'start_date', 'end_date'])
    for task in tasks:
        print task.title


if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:

        check_folder_columns(ox, 'MyTasks')
        #check_folder_columns(ox, 'Tasks')






