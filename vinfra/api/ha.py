import socket
import sys

from requests import adapters
from urllib3.connection import HTTPConnection

from vinfra import api_versions
from vinfra import exceptions
from vinfra.api import base


try:
    TCP_USER_TIMEOUT = socket.TCP_USER_TIMEOUT
except AttributeError:
    TCP_USER_TIMEOUT = 18


class LinuxHTTPAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):  # pylint: disable=arguments-differ
        options = list(HTTPConnection.default_socket_options)
        options.extend([
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5),
            (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3),
            # TCP_USER_TIMEOUT overtakes keepalive TCP_KEEPCNT
            # (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3),
            (socket.IPPROTO_TCP, TCP_USER_TIMEOUT, 5)
        ])
        kwargs['socket_options'] = options
        return super(LinuxHTTPAdapter, self).init_poolmanager(*args, **kwargs)


class HaTask(base.BackendTask):
    def __init__(self, api, data):
        super(HaTask, self).__init__(api, data, connect_retries=8,
                                     connect_retry_delay=0.5)

    def wait(self, timeout=None):
        if sys.platform != 'linux2':
            return super(HaTask, self).wait(timeout=timeout)

        # replace global adapter can have some affect to parallel runs
        adaper_prefix = 'https://'
        adapter = self.api.session.session.get_adapter(adaper_prefix)
        try:
            self.api.session.session.close()
            self.api.session.session.mount(adaper_prefix, LinuxHTTPAdapter())
            return super(HaTask, self).wait(timeout=timeout)
        finally:
            self.api.session.session.mount(adaper_prefix, adapter)


class HaConfig(object):
    def __init__(self, api):
        self.api = api

    def get(self):
        ha_config = self.api.client.get("/ha/configs")
        # Note(akurbatov): backend API returns empty response if ha is not
        # configured. Forcibly raise exception then:
        if not ha_config:
            raise exceptions.VinfraError("No HA configuration exists")
        return ha_config

    def create_async(self, nodes, virtual_ips, force=None):
        data = {'nodes': [base.get_id(node) for node in nodes]}
        data['virtual_ips'] = []

        for network, ip_addr, addr_type in virtual_ips:
            vip = {
                'roles_set': base.get_id(network),
                'ip': str(ip_addr),
            }
            if addr_type and self.api.api_version >= api_versions.HCI_VER_35:
                vip['method'] = addr_type
            data['virtual_ips'].append(vip)

        if force is not None:
            data['force'] = force
        data = self.api.client.post("/ha/configs", json=data)
        return HaTask(self.api, data)

    def delete_async(self):
        data = self.api.client.delete("/ha/configs")
        return HaTask(self.api, data)

    def update_async(self, nodes=None, virtual_ips=None, force=None):
        data = {}
        if nodes:
            data['nodes'] = [base.get_id(node) for node in nodes]
        if virtual_ips:
            data['virtual_ips'] = []
            for network, ip_addr, addr_type in virtual_ips:
                vip = {
                    'roles_set': base.get_id(network),
                    'ip': str(ip_addr),
                }
                if (addr_type and
                        self.api.api_version >= api_versions.HCI_VER_35):
                    vip['method'] = addr_type
                data['virtual_ips'].append(vip)

        if force is not None:
            data['force'] = force

        data = self.api.client.patch("/ha/configs", json=data)
        return HaTask(self.api, data)

    def add_node_async(self, nodes, without_controller_service):
        data = {}
        if nodes:
            data['nodes'] = [base.get_id(node) for node in nodes]

        data['with_controller'] = not without_controller_service

        data = self.api.client.patch("/ha/nodes/", json=data)
        return HaTask(self.api, data)

    def remove_node_async(self, node, force=False):
        node_id = base.get_id(node)
        url = "{}/{}".format("/ha/nodes", node_id)
        data = dict()
        if force is not None:
            data['force'] = force
        data = self.api.client.delete(url, json=data)
        return HaTask(self.api, data)
