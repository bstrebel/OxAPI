#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, requests, json, re

class OxHttpAPI(object):

    # global session reference
    _session = None

    @staticmethod
    def get_session(server=None, user=None, password=None):
        if not OxHttpAPI._session:
            if not server: server = os.environ.get('OX_SERVER')
            if not user: user = os.environ.get('OX_USER')
            if not password: password = os.environ.get('OX_PASSWORD')
            if server:
                OxHttpAPI._session = OxHttpAPI(server)
                if user:
                    OxHttpAPI._session.login(user, password)
        return OxHttpAPI._session

    @staticmethod
    def set_session(ox):
        OxHttpAPI._session = ox

    def __init__(self, server, user=None, password=None):

        self._server = server
        self._user = user
        self._password = password
        self._session = None
        self._cookies = None
        self._offline = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.authenticated:
            self.logout()

    @property
    def authenticated(self): return self._session is not None

    @property
    def offline(self): return self._offline == True

    @property
    def online(self): return self._offline == False

    def _response(self, response):
        """
        Post process web request response
        :param response: web request response
        :return: json object content
        """
        if response:
            if response.status_code == 200:
                if self._cookies is None: self._cookies = response.cookies;
                if response.content:
                    if response.content.startswith('{'):
                        content = response.json(encoding='UTF-8')
                        if content.get('error'):
                            print(json.dumps(content, indent=4, ensure_ascii=False, encoding='utf-8'))
                        return content
                    else:
                        return response.content
                else:
                    return response
            else:
                print(response.status_code)
        return None

    def _url(self, module, action):
        """
        Pre process web request
        :param module:
        :param action:
        :return: formatted URL
        """
        return self._server + '/ajax/' + module + '?action=' + action

    def _params(self, params=None):
        if params is None: params = {}
        params['session'] = self._session
        return params

    def _request(self, call, module, action, params, data=None):
        try:
            self._offline = True
            response = call(self._url(module, action), cookies=self._cookies, params=self._params(params), data=data)
        except requests.exceptions.RequestException as e:
            print e
            return None
        self._offline = False
        return self._response(response)

    def get(self, module, action, params):
        return self._request(requests.get, module, action, params)

    def post(self, module, action, params):
        return self._request(requests.post, module, action, params)

    def put(self, module, action, params, data=None):
        body = data
        if data:
            if isinstance(data, dict):
                body = json.dumps(data,ensure_ascii=False,encoding='utf-8')
        return self._request(requests.put, module, action, params, data=body)

    def login(self, user=None, password=None):

        if user: self._user = user
        if password: self._password = password

        params = {"name": self._user,
                  "password": self._password}

        content = self.post('login', 'login', params)
        if 'session' in content:
            self._session = content['session']

    def logout(self):
        self.get('login', 'logout', {})
        self._session = None
        self._cookies = None

    def _get_beans(self, beans, action, params={}):
        """
        Generic bean factory call
        :param beans: bean collection class, e.g. OxFolders
        :param action: API action
        :param params: API action params
        :return: json encoded response content
        """
        return beans(self).action(action, params)

    """ Public folder module wrapper """

    def get_root_folders(self):
        """
        Get root folders
        :return: list of OxFolder
        """
        from oxapi import OxFolders
        return self._get_beans(OxFolders, 'root')

    def get_folders(self, type):
        """
        Get folders of spec. module type
        :param type: folder type, e.g. 'tasks'
        :return: list of OxFolder
        """
        from oxapi import OxFolders
        return self._get_beans(OxFolders, 'allVisible', {'content_type': type})

    def get_folder_path(self, id):
        """
        Get folder path
        :param id: the folder id string
        :return: OxFolder
        """
        from oxapi import OxFolders
        return self._get_beans(OxFolders, 'path', {'id': id})

    def get_folder_by_id(self, id):
        """
        Get folder details
        :param id: the folder id string
        :return: OxFolder
        """
        from oxapi import OxFolders
        return self._get_beans(OxFolders, 'get', {'id': id})

    def get_folder_by_name(self, title, type):
        """
        Get folder by name
        :param title: folder name to search for
        :param type: folder type, e.g. 'tasks'
        :return: OxFolder
        """
        for folder in self.get_folders(type):
            if folder.title == title:
                return self.get_folder_by_id(folder.id)

    def get_standard_folder(self, type):
        """
        Get the default folder for module type
        :param type:
        :return:
        """
        for folder in self.get_folders(type):
            if folder.standard_folder:
                return self.get_folder_by_id(folder.id)

    def get_folder(self, type, guess=None):

        if guess is None:
            return self.get_standard_folder(type)

        if isinstance(guess, int):
            guess = str(guess)

        if re.match('^\d+$', guess):
            return self.get_folder_by_id(guess)
        else:
            return self.get_folder_by_name(guess, type)

    """ Public task module wrapper """

    def get_tasks(self, folder):
        from oxapi import OxTasks
        return self._get_beans(OxTasks, 'all', {'folder': folder})

    def get_task(self, folder, id):
        from oxapi import OxTasks
        return self._get_beans(OxTasks, 'get', {'id': id, 'folder': folder})

    def delete_task(self, folder, id):
        from oxapi import OxTasks, OxTask
        task = self._get_beans(OxTasks, 'get', {'id': id, 'folder': folder})
        return task.delete()
        #return self._get_beans(OxTasks, 'delete', {'id': id, 'folder': folder})

    """ Attachment module wrapper """

    def get_attachments(self, bean):
        from oxapi import OxAttachments
        return self._get_beans(OxAttachments, 'all', {'module': bean.module_type, 'attached': bean.id,  'folder': bean.folder_id})

    # def get_attachments(self, module, folder, id):
    #     from oxapi import OxAttachments
    #     return self._get_beans(OxAttachments, 'all', {'module': module, 'attached': id,  'folder': folder})

    def get_attachment(self, module, folder, id, attachment):
        from oxapi import OxAttachments
        return self._get_beans(OxAttachments, 'get', {'module': module, 'attached': id,  'folder': folder, 'id': attachment})

    def load_attachment(self, module, folder, id, attachment):
        from oxapi import OxAttachments
        return self._get_beans(OxAttachments, 'document', {'module': module, 'attached': id,  'folder': folder, 'id': attachment})

# region __main__

if __name__ == '__main__':

    server = None
    user = None
    password = None

    if len(sys.argv) > 3:
        server = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
    else:
        server = os.environ.get('OX_SERVER')
        user = os.environ.get('OX_USER')
        password = os.environ.get('OX_PASSWORD')

    with OxHttpAPI(server) as ox:
        ox.login(user,password)
        print(ox.authenticated)

# endregion

