#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys, re, json, requests
from oxapi import *

def get_a_task(ox):

    folder = ox.get_standard_folder('tasks')
    task = list(ox.get_tasks(folder.id))[0]
    return task

def upload(bean, args=[{'content':None,'file':None, 'mimetype':'text/plain','name':'attachment.txt'}]):

    from requests.packages.urllib3.fields import RequestField
    from requests.packages.urllib3.filepost import encode_multipart_formdata

    ox = bean._ox

    url = ox._url('attachment', 'attach')
    params = ox._params()

    meta = {'module': bean.module_type,
            #'attached': bean.id,
            'folder': bean.folder_id}

    counter = 0; fields = []
    for data in args:

        # json metadata
        rf = RequestField(name='json_' + str(counter) ,data=json.dumps(meta))
        rf.make_multipart(content_disposition='form-data')
        fields.append(rf)

        # content: data or file to read
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
            #TODO: process error
            return None

        if 'name' in data:
            filename = data['name']

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

def create_attachment(ox, task):

        from requests.packages.urllib3.fields import RequestField
        from requests.packages.urllib3.filepost import encode_multipart_formdata

        url = ox._url('attachment', 'attach')
        params = ox._params()

        json_0 = {'module': task.module_type,
                  'attached': task.id,
                  'folder': task.folder_id}

        fields = []
        rf = RequestField(name='json_0',data=json.dumps(json_0))
        rf.make_multipart(content_disposition='form-data')
        fields.append(rf)

        rf = RequestField(name='file_0', data="TEXT", filename='attachment.txt')
        rf.make_multipart(content_disposition='form-data',content_type='text/plain')
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


if __name__ == '__main__':

    with OxHttpAPI.get_session() as ox:
        task = get_a_task(ox)

        # args = [{ 'file':'attachments_module.py' }]
        # upload(task, args)

        #create_attachment(ox,task)
        #attachments = list(ox.get_attachments(task))

        attachments = ox.get_attachments(task)
        pass


