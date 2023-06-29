import copy
import hashlib
import io
import json
import logging
import os
import socket
import sys
import time
import warnings
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from six.moves import http_client
from urllib3.connection import HTTPConnection

from vinfra import exceptions
from vinfra.compat import addinfourl, urlparse, HTTPResponse

LOG = logging.getLogger(__name__)


def datetime_now():
    now = datetime.now()
    date = datetime.strftime(now, "%d.%m.%y-%H:%M:%S.%f")
    return date[:-3]


def _get_int_env(key, default=None):
    value = os.environ.get(key)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise exceptions.VinfraError("Can not convert %s to integer." % key)


class _JsonEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, (addinfourl, HTTPResponse)):
            return "addinfourl object of \"%s\"" % (
                o.url
            )
        if sys.version_info[0] == 2:
            if isinstance(o, file):
                return "File object (path=\"%s\"" % (
                    o.name
                )
        elif sys.version_info[0] == 3:
            if isinstance(o, io.IOBase):
                return "File object (path=\"%s\"" % (
                    o.name
                )
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return "Unable to encode object {}".format(type(o))


class Auth(object):
    def __init__(self, username, password, domain=None, project=None):
        self.username = username
        self.password = password
        self.domain = domain
        self.project = project

        self.token = None
        self.domain_id = None
        self.token = None
        self.scoped_token = None

    def _make_project_authenticate(self, session):
        projects = session.get(
            "/api/v2/accounts/projects", authenticated=False).json()['data']

        count = 0
        project_id = None
        for project in projects:
            if project['id'] == self.project:
                count += 1
                project_id = project['id']
            if project['name'] == self.project:
                count += 1
                project_id = project['id']

        if count == 0:
            if not projects:
                # there is no projects at all
                raise exceptions.VinfraError(
                    "Login has been disabled by the administrator")
            raise exceptions.VinfraError("No project with a name or ID of "
                                         "'{}' exists".format(self.project))
        elif count > 1:
            raise exceptions.VinfraError("More than one project exists with "
                                         "the name '{}'.".format(self.project))

        # NOTE(akurbatov): authenticated=False is essential here to avoid
        # recursion
        resp = session.post(
            "/api/v2/accounts/projects/{}/auth".format(project_id),
            authenticated=False, log=False)
        return resp.json()

    @staticmethod
    def needs_reauthenticate(session):
        for cookie in session.cookies:
            if cookie.name == 'session' and not cookie.is_expired():
                break
        else:
            return True

        return False

    def needs_scoped_reauthenticate(self):
        if self.project and not self.scoped_token:
            return True

        return False

    def make_authenticate(self, session):
        request_json = {
            "username": self.username,
            "password": self.password
        }
        if self.domain:
            request_json['domain'] = self.domain

        resp = session.post("/api/v2/login", authenticated=False,
                            json=request_json, log=False).json()
        self.domain_id = resp['domain_id']
        self.token = resp['token']
        self.make_scoped_authenticate(session)

    def make_scoped_authenticate(self, session):
        if self.project:
            data = self._make_project_authenticate(session)
            self.scoped_token = data['token']

    def get_headers(self, session):
        if self.needs_reauthenticate(session):
            self.make_authenticate(session)

        if self.needs_scoped_reauthenticate():
            self.make_scoped_authenticate(session)

        headers = {}
        if self.scoped_token:
            headers['X-Auth-Token'] = self.scoped_token

        return headers


class TCPKeepAliveHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):  # pylint: disable=arguments-differ
        options = list(HTTPConnection.default_socket_options)
        if sys.platform == 'linux2':
            options.extend([
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 7)
            ])
        elif sys.platform == 'darwin':
            options.extend([
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            ])
        # keepalive is not implemented for windows
        kwargs['socket_options'] = options
        return super(TCPKeepAliveHTTPAdapter, self).init_poolmanager(*args,
                                                                     **kwargs)


class Session(object):
    def __init__(self, url, auth=None, session=None):
        """Session controlled communication client.

        :param url: backend url
        :param auth: session authentication implementation
        :type auth: vinfra.session.BaseAuth
        :param session: session for rest requests
        :type session: requests.Session
        """
        self.url = url
        self.auth = auth
        self._json = _JsonEncoder()

        if not session:
            session = requests.Session()
            for schema in list(session.adapters):
                session.mount(schema, TCPKeepAliveHTTPAdapter())

        self.session = session

        self.session.verify = False
        warnings.filterwarnings('ignore', 'Unverified HTTPS request')

    @staticmethod
    def _process_header(header_name, header_value):
        secure_headers = ('x-auth-token',)
        header_name_lower = header_name.lower()

        if header_name_lower in secure_headers:
            token_hasher = hashlib.sha256()
            token_hasher.update(header_value.encode('utf-8'))
            header_value = '{SHA256}%s' % token_hasher.hexdigest()

        elif header_name_lower == 'set-cookie':
            session_value = None
            for item in header_value.split(';'):
                if '=' not in item:
                    continue
                key, value = item.split('=', 1)
                if key.lower() == 'session':
                    session_value = value

            if session_value:
                session_hasher = hashlib.sha256()
                session_hasher.update(session_value.encode('utf-8'))
                session_hash = '{SHA256}%s' % session_hasher.hexdigest()
                header_value = header_value.replace(session_value,
                                                    session_hash)

        return header_name, header_value

    @staticmethod
    def _process_data_request(data):
        data = copy.deepcopy(data)
        # /api/v2/accounts/change-password
        if 'current_password' in data:
            data['current_password'] = '<removed>'
        if 'new_password' in data:
            data['new_password'] = '<removed>'
        return data

    def _process_data_response(self, body):
        try:
            data = json.loads(body)

            # /api/v2/login
            # if 'token' in data:
            #    data['token'] = '<removed>'
            # if 'scoped_token' in data:
            #    data['scoped_token'] = '<removed>'

            return self._json.encode(data)

        except Exception:
            pass
        return body

    def _log_request(self, url, method, headers=None, data=None, json=None):
        if not LOG.isEnabledFor(logging.DEBUG):
            return

        string_parts = ['REQ: curl -g -i --insecure']
        string_parts.extend(['-X', method.upper()])
        string_parts.append(url)

        if headers:
            for header_name, header_value in headers.items():
                string_parts.append(
                    '-H "{}: {}"'.format(*self._process_header(header_name,
                                                               header_value))
                )

        for cookie in self.cookies:
            if cookie.name == 'session':
                cookie_hasher = hashlib.sha256()
                cookie_hasher.update(cookie.value.encode('utf-8'))
                cookie_hash = '{SHA256}%s' % cookie_hasher.hexdigest()
                string_parts.append("-b session={}".format(cookie_hash))

        if json:
            json = self._process_data_request(json)
            data = self._json.encode(json)

        if data:
            string_parts.append("-d '{}'".format(data))

        LOG.debug(' '.join(string_parts))

    def _log_response(self, resp):
        if not LOG.isEnabledFor(logging.DEBUG):
            return

        content_type = resp.headers.get('Content-Type', None)
        if content_type == 'application/json':
            text = self._process_data_response(resp.text)
        else:
            text = 'Omitted, Content-Type is set to {}.'.format(content_type)

        string_parts = ['RESP:', '[{}]'.format(resp.status_code)]

        for header_name, header_value in resp.headers.items():
            string_parts.append('{}: {}'.format(
                *self._process_header(header_name, header_value)))

        string_parts.append('\nRESP BODY: {}\n'.format(text))

        LOG.debug(' '.join(string_parts))

    def request(self, method, url, json=None, authenticated=True,
                raise_exc=True, request_id=None, **kwargs):
        timeout = kwargs.get('timeout')
        if not timeout:
            conn_timeout = _get_int_env('VINFRA_CONNECT_TIMEOUT', None)
            read_timeout = _get_int_env('VINFRA_READ_TIMEOUT', 100)
            kwargs['timeout'] = (conn_timeout, read_timeout)

        headers = kwargs.setdefault('headers', {})
        if request_id:
            headers['x-request-id'] = request_id

        if method.lower() in ['patch', 'post', 'put', 'delete']:
            headers['X-Requested-With'] = 'XMLHttpRequest'

        if authenticated:
            if not self.auth:
                raise Exception("auth attribute must be set")
            auth_headers = self.auth.get_headers(self)
            headers.update(auth_headers)

        if not urlparse(url).netloc:
            url = "{}/{}".format(self.url.rstrip('/'), url.lstrip('/'))

        if json is not None:
            headers.setdefault('Content-Type', 'application/json')

        resp = self._send_request(method, url, json=json, **kwargs)
        if raise_exc:
            resp.raise_for_status()

        return resp

    @staticmethod
    def _is_bad_status_line_error(err):
        if not (isinstance(err, requests.exceptions.ConnectionError) and
                err.args):
            return False

        inner_err = err.args[0]
        p_error_cls = requests.packages.urllib3.exceptions.ProtocolError  # pylint: disable=no-member
        return (
            isinstance(inner_err, p_error_cls) and
            len(inner_err.args) == 2 and
            inner_err.args[0] == 'Connection aborted.' and
            isinstance(inner_err.args[1], http_client.BadStatusLine)
        )

    @staticmethod
    def _is_connect_error(err):
        return isinstance(err, (requests.exceptions.ConnectionError,
                                requests.exceptions.Timeout))

    def _send_request(self, method, url, json=None, log=True,
                      connect_retries=0, connect_retry_delay=0.5,
                      _bad_status_line_retries=3, **kwargs):
        if log:
            self._log_request(url, method, headers=kwargs.get('headers'),
                              data=kwargs.get('data'),
                              json=json)
        try:
            resp = self.session.request(method, url, json=json, **kwargs)
        except Exception as err:
            if self._is_bad_status_line_error(err):
                _bad_status_line_retries -= 1
            elif self._is_connect_error(err):
                connect_retries -= 1
            else:
                raise

            if min(_bad_status_line_retries, connect_retries) < 0:
                raise

            LOG.debug('Request failure: %s. Retrying in %.1fs.',
                      err, connect_retry_delay)
            time.sleep(connect_retry_delay)

            return self._send_request(
                method, url, json=json, log=log,
                connect_retries=connect_retries,
                connect_retry_delay=connect_retry_delay * 2,
                _bad_status_line_retries=_bad_status_line_retries,
                **kwargs)

        if log:
            self._log_response(resp)

        return resp

    def get(self, url, **kwargs):
        """Perform a GET request.
        """
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request.
        """
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request.
        """
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request.
        """
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request.
        """
        return self.request('PATCH', url, **kwargs)

    @property
    def cookies(self):
        return self.session.cookies
