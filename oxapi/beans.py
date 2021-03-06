#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json, re, requests
from oxapi import *

class OxBean(object):

    map = {'id': 1,
           'created_by': 2,
           'creation_date': 4}

    reverse = {}
    # reverse = {1: 'id',
    #            2: 'created_by',
    #            3: 'creation_date'}

    @classmethod
    def check_columns(cls, params):

        columns = cls.columns

        if params.get('columns') is not None:

            columns = []
            ref = params['columns']
            if not isinstance(ref, list):
                ref = list(ref.split(','))
            for column in ref:
                if isinstance(column, int):
                    columns.append(column)
                else:
                    if re.match('^\d+$', column):
                        columns.append(int(column))
                    else:
                        columns.append(cls.map.get(column))

        params.update({'columns': ",".join(map(lambda id: str(id), sorted(set(columns))))})
        return params

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
    def map_reverse(cls, map):
        reverse = {}
        for key in sorted(map, key=map.__getitem__):
            reverse[map[key]] = key
        return reverse

    @classmethod
    def index(cls, key):
        if isinstance(key, str):
            id = cls.map[key]
            return cls.columns.index(id)
        else:
            return cls.columns.index(key)

    def __init__(self, data, ox=None, timestamp=None, columns=None):
        if ox: self._ox = ox
        else:  self._ox = OxHttpAPI.get_session()
        self._timestamp = timestamp
        self._data = data
        self._columns = columns

    @property
    def ox(self): return self._ox

    @property
    def module_type(self): return self._module_type

    @property
    def module_name(self): return self._module_name

    @property
    def timestamp(self): return self._timestamp

    @property
    def time(self):
        if self.last_modified_utc is not None:
            return self.last_modified_utc
        return self.last_modified + self._ox.utc_offset

    @property   # evernote compatible representation of categories
    def tagNames(self): return self.tag_names('ascii')

    @property
    def categories(self): return self._data.get('categories','')

    @property
    def exists(self): return self._data is not None

    def get_url(self):
        # https://ox.digitec.de/appsuite/#!&app=io.ox/tasks&folder=1963&id=1963.43941

        url =  "%s/appsuite/#!&app=io.ox/%s&folder=%s&id=%s.%s" % (self.ox.server,
                                                                   self.module_name,
                                                                   self.folder_id,
                                                                   self.folder_id,
                                                                   self.id)
        return url

    def tag_names(self, encoding=None):
        '''
        categories spliited into a list of names
        :param encoding: use ascii for Evernote compatible encoding
        :return: list of encoded tag names
        '''
        names = []
        if self.categories:
            for tag in self.categories.split(','):
                name = tag
                if encoding is 'ascii':
                    if isinstance(tag, unicode):
                        name = tag.encode('utf-8')
                names.append(name)
        return names

    def expand(self, content_data=None):
        '''
        get attribute hash representation of data list
        :param content_data: attribute list
        :return: attribute hash
        '''
        replace = False

        if not content_data:
            if not self._data:
                return None
            else:
                content_data = self._data
                replace = True

        if isinstance(content_data, list):

            assert len(content_data) == len(self.columns),\
                'Number of attributes does not match the number of data columns!'

            data = {}
            max = len(content_data) - 1
            for index in range(0, max):
                value = content_data[index]
                key = self.reverse[self.columns[index]]
                data[key] = value

            if replace:
                self._data = data

            return data
        else:
            return content_data

    def _check_bean(self, ox=None):
        if not ox: ox=self._ox
        result = True
        if self._timestamp is None:
            ox.logger.error('Bean request will fail without timestamp!')
            result = False
        if not isinstance(self._data, dict):
            ox.logger.error('Bean request will fail without data')
            result = False
        return result

    def index(self, key):

        if isinstance(key, str):
            key = self.map[key]

        if self._columns is None:
            return self.columns.index(key)
        else:
            return self._columns.index(key)

    def __getitem__(self, key):
        if self._data is None: return None
        if isinstance(self._data, dict):
            return self._data.get(key, None)
        else:
            return self._data[self.index(key)]

    def __getattr__(self, key):
        if self._data is None: return None
        if isinstance(self._data, dict):
            return self._data.get(key)
        else:
            return self._data[self.index(key)]

    def __setitem__(self, key, value):

        # replaces @categories.setter
        if key == 'categories':
            if isinstance(value, list):
                value = ','.join(value)

        if isinstance(self._data, dict):
            self._data[key] = value
        else:
            self._data[self.index(key)] = value

    def __setattr__(self, key, value):
        if key in self.map:
            self.__setitem__(key, value)
        else:
            self.__dict__[key] = value

    def delete(self, ox=None):
        if not ox: ox=self._ox
        if not self._check_bean(ox): return None
        result = None
        if ox and self._data:
            data = {'id': self.id,
                    'folder': self.folder_id}
            params = {'timestamp': self._timestamp}
            result = ox.put(self._module_name, 'delete', params, data)
        return result

    def get(self, ox=None):
        if not ox: ox=self._ox
        if ox and self._data:
            params = {'id': self.id,
                    'folder': self.folder_id}
            content = ox.get(self._module_name, 'get', params)
            if content:
                self._timestamp = content.get('timestamp', None)
                self._data = content.get('data', None)
        return self

    def load(self, ox=None):
        return self.get(ox)

    def create(self, ox=None):
        if not ox: ox=self._ox
        if ox and self._data:
            content = ox.put(self._module_name, 'new', None, self._data)
            if content:
                self._timestamp = content.get('timestamp', None)
                self._data.update(content.get('data',{}))
                # return self.id, self._timestamp
                return self
        return None

    def update(self, ox=None, new_folder=None):
        if not ox: ox=self._ox
        if not self._check_bean(ox): return None
        current_folder = self.folder_id
        if ox and self._data:
            if new_folder:
                self._data['folder_id'] = new_folder

            params = {'id': self.id,
                      'folder': current_folder,
                      'timestamp': self._timestamp}
            content = ox.put(self._module_name, 'update', params, self._data)
            if content:
                self._timestamp = content.get('timestamp', None)
        return self

    def move(self, target, ox=None):
        if not ox: ox=self._ox
        if target is not None:
            target_folder = ox.get_folder(self.module_name, target)
            if target_folder:
                return self.update(ox=ox, new_folder=target_folder.id)
        else:
            # TODO: argument exception
            pass
        return None

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

        if ox:
            if isinstance(ox, OxHttpAPI):
                self._ox = ox
            else:
                self._ox = OxHttpAPI.get_session(**ox)
        else:
            self._ox = OxHttpAPI.get_session()

        self._timestamp = None
        self._content = None
        self._raw = None
        self._data = None
        self._columns = None

    def action(self, type, action, params):
        content = self._ox.get(self.module_name, action, params)
        if content:
            if isinstance(content, dict):
                if content.get('error'):
                    pass
                else:
                    self._timestamp = content.get('timestamp', None)
                    self._raw = content.get('data', None)

                    if params.get('columns'):
                        self._columns = map(lambda id: int(id), params['columns'].split(','))
                    else:
                        self._columns = None
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
