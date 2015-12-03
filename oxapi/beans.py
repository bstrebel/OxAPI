#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json, re, requests
from oxapi import *

class OxBean(object):

    map = {'id': 1,
           'created_by': 2,
           'creation_date': 4}

    @classmethod
    def attr(cls, key):
        if isinstance(key, str):
            return cls.map[key]
        else:
            for k, v in cls.map.items():
                if v == key: return k

    @classmethod
    def columns(cls, map):
        columns = []
        for key in sorted(map, key=map.__getitem__):
            columns.append(map[key])
        return columns

    @classmethod
    def index(cls, key):
        if isinstance(key, str):
            id = cls.map[key]
            return cls.columns.index(id)
        else:
            return cls.columns.index(key)

    def __init__(self, data, ox=None, timestamp=None):
        if ox: self._ox = ox
        else:  self._ox = OxHttpAPI.get_session()
        self._timestamp = timestamp
        self._data = data

    @property
    def module_type(self): return self._module_type

    @property
    def module_name(self): return self._module_name

    def data(self, data):
        self._data.update(data)

    def __getitem__(self, key):
        if isinstance(self._data, dict):
            return self._data.get(key, None)
        else:
            return self._data[self.index(key)]

    def __getattr__(self, key):
        if isinstance(self._data, dict):
            return self._data.get(key, None)
        else:
            return self._data[self.index(key)]

    def delete(self, ox=None):
        if not ox: ox=self._ox
        result = None
        if ox and self._data:
            data = {'id': self.id,
                    'folder': self.folder_id}
            params = {'timestamp': self._timestamp}
            result = ox.put(self._module, 'delete', params, data)
        return result

    def get(self, ox=None):
        if not ox: ox=self._ox
        if ox and self._data:
            params = {'id': self.id,
                    'folder': self.folder_id}
            content = ox.get(self._module, 'get', params)
            if content:
                self._timestamp = content.get('timestamp', None)
                self._data = content.get('data', None)

    def create(self, ox=None):
        if not ox: ox=self._ox
        if ox and self._data:
            content = ox.put(self._module, 'new', None, self._data)
            if content:
                self._timestamp = content.get('timestamp', None)
                self._data.update(content.get('data',{}))

    def update(self, ox=None):
        if not ox: ox=self._ox
        if ox and self._data:
            params = {'id': self.id,
                      'folder': self.folder_id,
                      'timestamp': self._timestamp}
            content = ox.put(self._module, 'update', params, self._data)
            if content:
                self._timestamp = content.get('timestamp', None)

    def upload(self, args=[{'content':None,'file':None, 'mimetype':'text/plain','name':'attachment.txt'}]):

        from requests.packages.urllib3.fields import RequestField
        from requests.packages.urllib3.filepost import encode_multipart_formdata

        ox = self._ox

        url = ox._url('attachment', 'attach')
        params = ox._params()

        meta = {'module': self.module_type,
                'attached': self.id,
                'folder': self.folder_id}

        counter = 0; fields = []
        for data in args:

            # json metadata
            rf = RequestField(name='json_' + str(counter) , data=json.dumps(meta))
            rf.make_multipart(content_disposition='form-data')
            fields.append(rf)

            # content: data or file
            filename = 'attachment.txt'
            mimetype = 'text/plain'
            content = None
            if 'content' in data:
                content = data['content']
            else:
                if 'file' in data:
                    filename = data['file']
                    if os.path.isfile(filename):
                        with open(filename, 'rb') as fh:
                            content = fh.read()

            if content is None:
                # TODO: process error
                return None

            # display name of the attachment
            if 'name' in data:
                filename = data['name']

            # mimetype
            # TODO: use mimetype module to guess the type if not set
            mimetype = 'text/plain'
            if 'mimetype' in data:
                mimetype = data['mimetype']

            rf = RequestField(name='file_' + str(counter), data=content, filename=filename)
            rf.make_multipart(content_disposition='form-data',content_type=mimetype)
            fields.append(rf)

        post_body, content_type = encode_multipart_formdata(fields)
        content_type = ''.join(('multipart/mixed',) + content_type.partition(';')[1:])

        headers = {'Content-Type': content_type}

        response = requests.post(url, cookies=ox._cookies,  params=params, headers=headers, data=post_body)
        if response and response.status_code == 200:
            regex='\((\{.*\})\)'
            match = re.search(regex, response.content)
            if match:
                return json.loads(match.group(1))

        return None

    @property
    def attachments(self):
        if self._attachments is None:
            self._attachments = self._ox.get_attachments(self)
        return self._attachments


class OxBeans(object):

    def __init__(self, ox):
        self._ox = ox
        self._timestamp = None
        self._content = None
        self._raw = None
        self._data = None

    def action(self, type, action, params):
        content = self._ox.get(self.module_name, action, params)
        if content:
            if isinstance(content, dict):
                if content.get('error'):
                    pass
                else:
                    self._timestamp = content.get('timestamp', None)
                    self._raw = content.get('data', None)
            else:
                self._content = content
        return self

    def __iter__(self):
        return iter(self._data)


# region __main__

if __name__ == '__main__':

    server = os.environ.get('OX_SERVER')
    user = os.environ.get('OX_USER')
    password = os.environ.get('OX_PASSWORD')



    data = {'id': '1234', 'title': 'title'}
    bean = OxBean(data)
    print(bean.id)
    print(bean['title'])

# endregion
