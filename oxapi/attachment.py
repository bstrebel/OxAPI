#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,time,json,requests
from oxapi import *


class OxAttachment(OxBean):

    module_name = 'attachment'
    module_type = None

    map = {'folder': 800,
           'attached': 801,
           'module': 802,
           'filename': 803,
           'filesize': 804,
           'file_mimetype': 805,
           'rtf_flag': 806}

    map.update(OxBean.map)
    columns = OxBean.columns(map)

    def __init__(self, data, ox=None, timestamp=None):
        self._document = None
        self._module = 'attachment'
        OxBean.__init__(self, data, ox, timestamp)

    @property
    def document(self):
        if not self._document:
            if self._data:
                params = {'module': self.module,
                          'attached': self.attached,
                          'id': self.id,
                          'folder': self.folder}

                document = self._ox.get(self._module, 'document', params)
                if document:
                    #self._timestamp = content.get('timestamp', None)
                    self._document = document

        return self._document


class OxAttachments(OxBeans):

    module_name = 'attachment'

    def __init__(self, ox):
        OxBeans.__init__(self, ox)

    def action(self, action, params):

        if action == 'all':
            params.update({'columns': ",".join(map(lambda id: str(id), OxAttachment.columns))})
            self._data = []
            OxBeans.action(self, OxAttachment, action, params)
            if self._raw:
                folder = params['folder']
                id = OxAttachment.map['folder']
                pos = OxAttachment.columns.index(id)
                for raw in self._raw:
                    # workaround because of Open-Xchange bug
                    if raw[pos] == 0: raw[pos] = folder
                    self._data.append(OxAttachment(raw, self._ox))
            return self

        elif action == 'get':

            self._data = None
            OxBeans.action(self, OxAttachment, action, params)
            self._data = OxAttachment(self._raw, self._ox, self._timestamp)
            return self._data

        elif action == 'document':

            self._data = None
            OxBeans.action(self, OxAttachment, action, params)
            self._data = OxAttachment(self._raw, self._content, self._ox, self._timestamp)
            return self._data

# region __main__

if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:
        task = ox.get_task('246','43806')
        attachments = ox.get_attachments(task)
        pass

# endregion
