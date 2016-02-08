#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, requests, json, re, logging
from pyutils import LogAdapter

class OxHttpAPI(object):

    # global session reference
    _session = None

    @staticmethod
    def get_session(server=None, user=None, password=None, logger=None):
        if not OxHttpAPI._session:
            if not server: server = os.environ.get('OX_SERVER')
            if not user: user = os.environ.get('OX_USER')
            if not password: password = os.environ.get('OX_PASSWORD')
            # if not logger: logger = logging.getLogger('oxapi')
            if server:
                OxHttpAPI._session = OxHttpAPI(server, logger=logger)
                if user:
                    OxHttpAPI._session.login(user, password)
        return OxHttpAPI._session

    @classmethod
    def set_session(cls, ox):
        OxHttpAPI._session = ox

    @staticmethod
    def hide_password(msg):
        if msg:
            msg = re.sub('password=.*&', 'password=*****&', msg, re.IGNORECASE)
        return msg

    def __init__(self, server, user=None, password=None, logger=None):

        from pyutils import LogAdapter, get_logger

        self._server = server
        self._user = user
        self._password = password
        self._session = None
        self._cookies = None
        self._offline = None
        self._utc_offset = None

        if logger is None:
            self._logger = get_logger('oxapi', logging.DEBUG)
        else:
            self._logger = logger

        self._adapter = LogAdapter(self._logger, {'package': 'oxapi', 'callback': OxHttpAPI.hide_password})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self:
            if self.authenticated:
                self.logout()

    @property
    def logger(self):return self._adapter

    @property
    def server(self): return self._server

    @property
    def user(self): return self._user

    @property
    def password(self): return self._password

    @property
    def authenticated(self): return self._session is not None

    @property
    def offline(self): return self._offline == True

    @property
    def online(self): return self._offline == False

    @property
    def utc_offset(self):
        if self._utc_offset is None:
            result = self.get('config/currentTime')
            local = result['data']/1000
            utc = long(time.time())
            self._utc_offset = long(round((utc - local),-2) * 1000)
            self.logger.debug('UTC offset set to %d milliseconds' % (self._utc_offset))
        return self._utc_offset

    @property
    def serverVersion(self):
        return self.config('serverVersion')

    def module_class(self, module):

        from oxapi import OxTasks, OxAttachments
        return {'tasks': OxTasks,
                'attachment': OxAttachments}.get(module)

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
                    self.logger.debug("Response content: [%s]" % (response.content.decode('utf-8')))
                    if response.content.startswith('{'):
                        content = response.json(encoding='UTF-8')
                        if content.get('error'):
                            # print(json.dumps(content, indent=4, ensure_ascii=False, encoding='utf-8'))
                            self.logger.error(json.dumps(content, ensure_ascii=False, encoding='utf-8'))
                        return content
                return response.content
            else:
                self.logger.error("Response: %d" % (response.status_code))
                #print(response.status_code)
        return None

    def _url(self, module, action):
        """
        Pre process web request
        :param module:
        :param action:
        :return: formatted URL
        """
        url = self._server + '/ajax/' + module
        if action:
            url += '?action=' + action
        self.logger.debug("Request url: %s" % (url))
        return url

    def _params(self, params=None):
        if params is None: params = {}
        password = params.get('password')
        params['session'] = self._session
        if password: params['password'] = '*****'
        self.logger.debug("Request params: %s" % (params))
        if password: params['password'] = password
        return params

    def _request(self, call, module, action, params, data=None):
        try:
            self._offline = True
            self.logger.debug('Request call: [%s] with body %s' % (call.func_name, data))
            response = call(self._url(module, action), cookies=self._cookies, params=self._params(params), data=data)
            self.logger.debug('Request url: %s' % (response.request.path_url))
        except requests.exceptions.RequestException as e:
            self.logger.error("Request exception: %s" % (e))
            return None
        self._offline = False
        return self._response(response)

    def get(self, module, action=None, params=None):
        return self._request(requests.get, module, action, params)

    def post(self, module, action, params):
        return self._request(requests.post, module, action, params)

    def put(self, module, action, params, data=None):
        body = data
        if data:
            # if isinstance(data, dict):
            #     body = json.dumps(data,ensure_ascii=False,encoding='utf-8')
            #body = json.dumps(data,ensure_ascii=False,encoding='utf-8')
            body = json.dumps(data)
        return self._request(requests.put, module, action, params, data=body)

    def login(self, user=None, password=None):

        if user: self._user = user
        if password: self._password = password

        params = {"name": self._user,
                  "password": self._password}

        content = self.post('login', 'login', params)
        if content and 'session' in content:
            self.logger.debug("User %s successfully logged in at %s" % (user, self._server))
            self._session = content['session']
        else:
            self.logger.error("Login for %s at %s failed" % (user, self._server))

    def logout(self):
        self.get('login', 'logout', {})
        self._session = None
        self._cookies = None
        self.logger.debug("User %s logged out!" % (self._user))

    def config(self, path):
        result = self.get('config' + '/' + path)
        return result.get('data')

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

    def get_folders(self, type, columns=None):
        """
        Get folders of spec. module type
        :param type: folder type, e.g. 'tasks'
        :return: list of OxFolder
        """
        from oxapi import OxFolders
        return self._get_beans(OxFolders, 'allVisible', {'content_type': type, 'columns': columns})

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
        folder = self._get_beans(OxFolders, 'get', {'id': id})
        # folder._module = folder._module
        return folder

    def get_folder_by_name(self, title, type):
        """
        Get folder by name
        :param title: folder name to search for
        :param type: folder type, e.g. 'tasks'
        :return: OxFolder
        """
        for folder in self.get_folders(type, ['id', 'title']):
            if folder.title == title:
                return self.get_folder_by_id(folder.id)

    def get_standard_folder(self, type):
        """
        Get the default folder for module type
        :param type:
        :return:
        """
        for folder in self.get_folders(type, ['id', 'title', 'standard_folder']):
            if folder.standard_folder:
                return self.get_folder_by_id(folder.id)

    def get_folder(self, type, guess=None):
        '''
        Get OxFolder of sepcified type and (optional) name
        :param type: folder type (e.g. 'tasks'
        :param guess: name or id or nothing for standard folder
        :return:
        '''
        from oxapi import OxFolder

        if not guess:
            return self.get_standard_folder(type)

        if isinstance(guess, OxFolder):
            return guess


        if isinstance(guess, int):
            guess = str(guess)

        if re.match('^\d+$', guess):
            return self.get_folder_by_id(guess)
        else:
            return self.get_folder_by_name(guess, type)

    """ Public task module wrapper """

    def get_tasks(self, folder, columns=None):
        from oxapi import OxTasks
        return self._get_beans(OxTasks, 'all', {'folder': folder, 'columns': columns})

    def get_task(self, folder, id):
        from oxapi import OxTasks
        return self._get_beans(OxTasks, 'get', {'id': id, 'folder': folder})

    def delete_task(self, folder, id):
        from oxapi import OxTasks, OxTask
        task = self._get_beans(OxTasks, 'get', {'id': id, 'folder': folder})
        return task.delete()

    def move_task(self, folder, id, target):
        from oxapi import OxTasks, OxTask
        task = self._get_beans(OxTasks, 'get', {'id': id, 'folder': folder})
        return task.move(target)

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


