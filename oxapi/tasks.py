#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,time,json,requests
from oxapi import *

class OxTask(OxBean):

    @staticmethod
    def get_status(tag):
        task_status = ['unknown', 'not started', 'in progress', 'done', 'waiting', 'deferred']
        if isinstance(tag, int):
            if tag < len(task_status):
                return task_status[tag]
        else:
            if tag in task_status:
                return task_status.index(tag)
        return None

    module_name = 'tasks'
    module_type = 4

    map = {'modified_by': 3,
           'last_modified': 5,
           'folder_id': 20,
           'categories': 100,
           'private_flag': 101,
           'color_label': 102,
           'number_of_attachments': 104,
           'lastModifiedOfNewestAttachmentUTC': 105,

           'title': 200,
           'start_date': 201,
           'end_date': 202,
           'note': 203,
           'alarm': 204,

           'status': 300,
           'type': 302}

    map.update(OxBean.map)
    columns = OxBean.columns(map)

    def __init__(self, data, ox=None, timestamp=None):
        self._module_name = OxTask.module_name
        self._module_type = OxTask.module_type
        self._attachments = None
        self._path = None
        OxBean.__init__(self, data, ox, timestamp)


class OxTasks(OxBeans):

    module_name = 'tasks'

    def __init__(self, ox):
        OxBeans.__init__(self, ox)

    def action(self, action, params):

        if action == 'all':

            params.update({'columns': ",".join(map(lambda id: str(id), OxTask.columns))})
            self._data = []
            OxBeans.action(self, OxTask, action, params)
            for raw in self._raw: self._data.append(OxTask(raw, self._ox))
            return self

        elif action == 'get':

            self._data = None
            OxBeans.action(self, OxTask, action, params)
            self._data = OxTask(self._raw, self._ox, self._timestamp)
            return self._data

# region __main__

if __name__ == '__main__':

    task = OxTask({})
    print task.module_name

# endregion
