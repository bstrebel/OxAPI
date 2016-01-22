#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,json
from oxapi import *

class OxFolder(OxBean):

    module_name = 'folders'
    module_type = None

    map = {'modified_by': 3,
           'last_modified': 5,
           'last_modified_utc': 6,
           'folder_id': 20,
           'title': 300,
           'module': 301,
           'type': 302,
           'subfolders': 304,
           'own_rights': 305,
           'permissions': 306,
           'summary': 307,
           'standard_folder': 308,
           'total': 309,
           'new': 310,
           'unread': 311,
           'deleted': 312,
           'capabilities': 313,
           'subscribed': 314,
           'subsr_subflds': 315,
           'standard_folder_type': 316,
           'supported_capabilties': 317,
           'account_id': 318}

    map.update(OxBean.map)
    reverse = OxBean.map_reverse(map)
    columns = OxBean.columns(map)

    def __init__(self, data, ox=None, timestamp=None, columns=None):
        self._path = None
        OxBean.__init__(self, data, ox, timestamp, columns)

    def items(self, columns=None):
        ox = self._ox
        module = ox.module_class(self.module)
        return ox._get_beans(module, 'all', {'folder': self.id, 'columns': columns})

class OxFolders(OxBeans):

    module_name = 'folders'

    def __init__(self, ox):
        OxBeans.__init__(self, ox)

    def action(self, action, params):

        if action == 'root':

            params = OxFolder.check_columns(params)
            self._data = []
            OxBeans.action(self, OxFolder, action, params)
            for raw in self._raw:
                self._data.append(OxFolder(raw, self._ox, columns=self._columns))
            return self

        elif action == 'allVisible':

            params = OxFolder.check_columns(params)
            self._data = []
            OxBeans.action(self, OxFolder, action, params)
            for key in self._raw:
                for raw in self._raw[key]:
                    self._data.append(OxFolder(data=raw, ox=self._ox, columns=self._columns))
            return self

        elif action == 'path':

            params = OxFolder.check_columns(params)
            self._data = []
            OxBeans.action(self, OxFolder, action, params)
            for raw in self._raw:
                self._data.append(OxFolder(raw, self._ox, columns=self._columns))
            return self

        elif action == 'get':

            self._data = None
            OxBeans.action(self, OxFolder, action, params)
            self._data = OxFolder(self._raw, self._ox)
            return self._data


# region __main__

if __name__ == '__main__':

    print OxFolder.columns()


    # from oxapi import OxHttpAPI
    #
    # server = os.environ.get('OX_SERVER')
    # user = os.environ.get('OX_USER')
    # password = os.environ.get('OX_PASSWORD')
    #
    # ox = OxHttpAPI(server)
    # ox.login(user, password)
    #
    # response = ox.get('folders','root', {'columns': '1,2,3,4,5,6,20,300,301,302,304'})
    #
    # ox.logout()

# endregion
