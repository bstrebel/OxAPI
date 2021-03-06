#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,time,json,requests,re
from oxapi import *

class OxTask(OxBean):

    @staticmethod
    def get_status(tag):
        task_status = ['unknown', 'Not started', 'In progress', 'Done', 'Waiting', 'Deferred']
        if isinstance(tag, int):
            if tag < len(task_status):
                return task_status[tag]
        else:
            if tag:
                status_lower = [item.lower() for item in task_status]
                if tag.lower() in status_lower:
                    return status_lower.index(tag.lower())
        return None

    @staticmethod
    def get_priority(tag):
        # BUG: HTTP API returns number-like strings for priority
        task_priority = ['None', 'Low', 'Medium', 'High']
        if isinstance(tag, int):
            if tag < len(task_priority):
                return task_priority[tag]
        else:
            if tag:
                priority_lower = [item.lower() for item in task_priority]
                if tag.lower() in priority_lower:
                    return priority_lower.index(tag.lower())
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
           'percent_completed': 301,
           'actual_costs': 302,
           'actual_duration': 303,
           'billing_information': 305,
           'target_costs': 307,
           'target_duration': 308,
           'priority': 309,
           'currency': 312,
           'trip_meter': 313,
           'companies': 314,
           'date_completed': 315,
           'start_time': 201,
           'end_time': 202,
           'full_time': 401}

    # new columns available only since Rev. 7.6.1
    # but: works not for default folder 'Tasks'

    map761 = {'start_time': 316,
              'end_time': 317,
              'full_time': 401}

    map.update(OxBean.map)
    reverse = OxBean.map_reverse(map)

    columns = OxBean.columns(map)
    #fields = OxBean.fields(map)

    def __init__(self, data, ox=None, timestamp=None, columns=None):
        self._module_name = OxTask.module_name
        self._module_type = OxTask.module_type
        self._attachments = None
        self._path = None
        OxBean.__init__(self, data, ox, timestamp, columns)

    @property
    def _id(self): return self['id']

    @property
    def _time(self): return self['last_modified']

    @property
    def _key(self): return self['title']

    @property
    def _alarm_date(self): return self.alarm/1000 if self.alarm else None

    @property
    def _start_date(self): return self.start_date/1000 if self.start_date else None

    @property
    def _end_date(self): return self.end_date/1000 if self.end_date else None

    @property
    def _start_time(self): return self.start_time/1000 if self.start_time else None

    @property
    def _end_time(self): return self.end_time/1000 if self.end_time else None

    @property
    def _start_time_utc(self): return self.start_time/1000 + (self._ox.utc_offset) if self.start_time else None

    @property
    def _end_time_utc(self): return self.end_time/1000 + (self._ox.utc_offset) if self.end_time else None


    # @property
    # def _start_date(self): return self._checked_date('start')
    #
    # @property
    # def _end_date(self): return self._checked_date('end')
    #
    # def _checked_date(self, tag):
    #     key = tag + '_time'
    #     if self._data.get(key):
    #         return self._data[key]/1000
    #     else:
    #         key = tag + '_date'
    #         if self._data.get(key):
    #             return self._data[key]/1000
    #     return None


class OxTasks(OxBeans):

    module_name = 'tasks'

    def __init__(self, ox):
        OxBeans.__init__(self, ox)

    def action(self, action, params):

        if action == 'all':

            params = OxTask.check_columns(params)
            self._data = []
            OxBeans.action(self, OxTask, action, params)
            for raw in self._raw:
                self._data.append(OxTask(raw, self._ox, columns=self._columns))
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
