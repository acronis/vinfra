# pylint: disable=protected-access
import collections
import json

from vinfra.api.base import BackendTask
from vinfra.compat import urlencode


Response = collections.namedtuple('Response', ['data', 'request_id'])


class ApiVersion(object):
    """
    self client.get(...)
    with ApiV2(self.client) as api_v2:
        api_v2.put(...)
        with ApiV3(client) as api_v3:
           api_v3.post(...)
    """
    def __init__(self, client):
        self.__client = client
        self.__original = None

    @classmethod
    def version(cls):
        raise NotImplementedError

    def __enter__(self):
        self.__original = self.__client.api_version
        self.__client._Client__api_version = self.version()
        return self.__client

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__original:
            self.__client._Client__api_version = self.__original


class ApiV2(ApiVersion):
    @classmethod
    def version(cls):
        return "/api/v2"


class ApiV3(ApiVersion):
    @classmethod
    def version(cls):
        return "/api/v3"


class Client(object):
    def __init__(self, api, version=ApiV2.version()):
        self.api = api
        self.__api_version = version

    @property
    def api_version(self):
        return self.__api_version

    def send_request_raw(self, method, url, **kwargs):
        params = kwargs.pop('params', None)
        query_params = kwargs.pop('query_params', None)
        if params and query_params:
            raise ValueError('params and query mutually exclusive')

        url = "{}/{}".format(self.api_version, url.strip('/'))
        if params:
            params = json.dumps(params, separators=(',', ':'))
            url += "/?{}".format(urlencode({'params': params}))
        elif query_params:
            url += "/?{}".format(urlencode(query_params))

        response = self.api.session.request(method, url, **kwargs)
        return response

    def send_request(self, method, url, **kwargs):
        response = self.send_request_raw(method, url, **kwargs)
        content_type = response.headers.get('Content-Type')
        request_id = response.headers.get('x-request-id')
        if content_type == 'application/json':
            if response.text:
                data = response.json()
            else:
                data = response.text
        elif content_type == 'application/octet-stream':
            data = None
        else:
            data = response.text
        return Response(data, request_id)

    def _send_task(self, method, url, task_params=None, **kwargs):
        resp = self.send_request(method, url, **kwargs)

        task_params = task_params or {}
        task_params['request_id'] = resp.request_id
        return BackendTask(self.api, resp.data, **task_params)

    def get(self, url, **kwargs):
        resp = self.send_request("get", url, **kwargs)
        return resp.data

    def put(self, url, **kwargs):
        resp = self.send_request("put", url, **kwargs)
        return resp.data

    def post(self, url, **kwargs):
        resp = self.send_request("post", url, **kwargs)
        return resp.data

    def delete(self, url, **kwargs):
        resp = self.send_request("delete", url, **kwargs)
        return resp.data

    def patch(self, url, **kwargs):
        resp = self.send_request("patch", url, **kwargs)
        return resp.data

    # async
    def put_async(self, url, **kwargs):
        return self._send_task("put", url, **kwargs)

    def post_async(self, url, **kwargs):
        return self._send_task("post", url, **kwargs)

    def patch_async(self, url, **kwargs):
        return self._send_task("patch", url, **kwargs)

    def delete_async(self, url, **kwargs):
        return self._send_task("delete", url, **kwargs)
