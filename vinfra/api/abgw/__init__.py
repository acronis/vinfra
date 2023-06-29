import json
import sys

from vinfra import exceptions
from vinfra.api_versions import version_wrap
from vinfra.api import base, failure_domains
from vinfra.api.compute.storage_policies import get_api_redundancy
from vinfra.utils import flatten_args

from vinfra.api.abgw.georeplication import GeoReplication
from vinfra.api.abgw.registrations import AbgwRegistrationsApi


# pylint: disable=function-redefined
class AbgwApi(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw".format(base.get_id(self.cluster))
        super(AbgwApi, self).__init__(cluster.manager.api)
        self.storage_params = StorageParams(self.cluster)
        self.volume_params = VolumeParams(self.cluster)
        self.geo_replication = GeoReplication(self.cluster)
        self.registrations = AbgwRegistrationsApi(self.cluster)
        self.sysinfo_conf = SysinfoConf(self.cluster)
        self.limits_params = ClientLimits(self.cluster)

    def _adjust_nodes(self, nodes):
        abgw_private = 'Backup (ABGW) private'
        network_id_with_abgw_private = None

        for network in self.api.networks.list():
            if abgw_private in network.traffic_types:
                network_id_with_abgw_private = network.id
                break
        else:
            msg = (
                "Networks with the following required traffic types "
                "not found: {!r}".format(abgw_private)
            )
            raise exceptions.VinfraError(msg)
        nodes_data = []
        errors = list()
        for node in nodes:
            for iface in node.ifaces_manager.list():
                if iface.network == network_id_with_abgw_private:
                    nodes_data.append({
                        'node_id': base.get_id(node),
                        'private_iface': iface.name
                    })
                    break
            else:
                errors.append(
                    "Traffic type {!r} is not assigned on node {!r}".format(
                        abgw_private, node['host']
                    ))
        if errors:
            raise exceptions.VinfraError("\n".join(errors))
        return nodes_data

    @version_wrap("2.0", "5.0.1")
    def assign_nodes(self, nodes):
        nodes = self._adjust_nodes(nodes)
        url = "{}/assign".format(self.base_url)
        data = {"nodes": nodes}
        return self.client.post_async(url, json=data)

    @version_wrap("5.1.0")
    def assign_nodes(self, nodes):
        nodes = self._adjust_nodes(nodes)
        url = "{}/nodes/join/".format(self.base_url)
        data = {"nodes": nodes}
        return self.client.post_async(url, json=data)

    @version_wrap("2.0", "5.0.1")
    def get_nodes(self):
        return self.client.get(url="{}/nodes/".format(self.base_url))

    @version_wrap("5.1.0")
    def get_nodes(self):
        return self.get()['hosts']

    @version_wrap("2.0", "5.0.1")
    def create_async(
            self, nodes, domain,
            reg_server, reg_account, reg_password,
            tier, failure_domain, redundancy,
            storage_type, storage_params=None,
    ):
        nodes = self._adjust_nodes(nodes)
        redundancy = get_api_redundancy(redundancy)

        data = flatten_args(
            nodes=nodes,
            domain=domain,
            reg_server=reg_server,
            reg_account=reg_account,
            reg_password=reg_password,
            storage_type=storage_type,
            storage_params=storage_params,
            tier=tier,
            failure_domain=failure_domain,
            redundancy=redundancy,
        )
        if "storage_params" in data:
            self.storage_params.verify(
                nodes=nodes, storage_params=storage_params,
                storage_type=storage_type
            )
        url = "{}/register/".format(self.base_url)
        return self.client.post_async(url, json=data)

    @version_wrap("5.1.0")
    def create_async(
            self, nodes, name, address,
            account_server, username, password,
            tier, failure_domain, redundancy,
            storage_type, storage_params=None, location=None
    ):
        nodes = self._adjust_nodes(nodes)
        redundancy = get_api_redundancy(redundancy)

        data = flatten_args(
            nodes=nodes,
            name=name,
            address=address,
            account_server=account_server,
            location=location,
            username=username,
            password=password,
            storage_type=storage_type,
            storage_params=storage_params,
            tier=tier,
            failure_domain=failure_domain,
            redundancy=redundancy,
        )
        if "storage_params" in data:
            self.storage_params.verify(
                nodes=nodes, storage_params=storage_params,
                storage_type=storage_type
            )
        url = "{}/deploy-standalone/".format(self.base_url)
        return self.client.post_async(url, json=data)

    def deploy_reverse_proxy_async(
            self, nodes, upstream_info_file,
            tier, failure_domain, redundancy,
            storage_type, storage_params=None
    ):
        nodes = self._adjust_nodes(nodes)
        redundancy = get_api_redundancy(redundancy)

        data = flatten_args(
            nodes=nodes,
            storage_type=storage_type,
            storage_params=storage_params,
            tier=tier,
            failure_domain=failure_domain,
            redundancy=redundancy,
        )
        if "storage_params" in data:
            self.storage_params.verify(
                nodes=nodes, storage_params=storage_params,
                storage_type=storage_type
            )
        url = "{}/deploy-reverse-proxy/".format(self.base_url)
        files = {'json': (None, json.dumps(data), 'application/json'),
                 'upstream-info': upstream_info_file}

        resp = self.client.post(url, files=files)
        return _BackupGatewayTask(self, resp)

    def turn_to_upstream_async(self, address):
        data = {
            "address": address,
        }
        url = "{}/reverse-proxying/turn-to-upstream/".format(self.base_url)
        resp = self.client.post(url, json=data)
        return _BackupGatewayTask(self, resp)

    def deploy_upstream_async(
            self, nodes, address,
            tier, failure_domain, redundancy,
            storage_type, storage_params=None
    ):
        nodes = self._adjust_nodes(nodes)
        redundancy = get_api_redundancy(redundancy)

        data = flatten_args(
            nodes=nodes,
            address=address,
            storage_type=storage_type,
            storage_params=storage_params,
            tier=tier,
            failure_domain=failure_domain,
            redundancy=redundancy,
        )
        if "storage_params" in data:
            self.storage_params.verify(
                nodes=nodes, storage_params=storage_params,
                storage_type=storage_type
            )
        url = "{}/deploy-upstream/".format(self.base_url)
        resp = self.client.post(url, json=data)
        return _BackupGatewayTask(self, resp)

    def download_upstream_info(self, output_file=None):
        def ostream():
            return open(output_file, 'wb') if output_file else sys.stdout

        upstream_info_stream = self.client.send_request_raw(
            method="get",
            url="{}/reverse-proxying/upstream-info/".format(self.base_url),
            stream=True
        )
        with ostream() as fout:
            for chunk in upstream_info_stream:
                fout.write(chunk)

    def add_new_upstream_async(self, upstream_info_file):
        resp = self.client.post(
            url="{}/reverse-proxying/add-new-upstream/".format(self.base_url),
            data=upstream_info_file,
            headers={
                'Content-Type': 'application/octet-stream',
            }
        )
        return _BackupGatewayTask(self, resp)

    def retry(self, process_id=None):
        id_string = ('/' + process_id + '/') if process_id else '/'
        url = "{}/process{}retry/".format(self.base_url, id_string)
        return self.client.post(url)

    def show_process(self, process_id=None):
        id_string = ('/' + process_id + '/') if process_id else '/'
        url = "{}/process{}".format(self.base_url, id_string)
        return self.client.get(url)

    @version_wrap("2.0.0", "5.0.1")
    def get(self):
        url = "{}/register/".format(self.base_url)
        return self.client.get(url)

    @version_wrap("5.1.0")
    def get(self):
        url = "{}/deployment-info/".format(self.base_url)
        return self.client.get(url)

    @version_wrap("2.0.0", "5.0.1")
    def release_nodes(self, nodes):
        url = "{}/release/".format(self.base_url)
        data = {"nodes": nodes}
        return self.client.post_async(url, json=data)

    @version_wrap("5.1.0")
    def release_nodes(self, nodes):
        url = "{}/nodes/leave/".format(self.base_url)
        data = {"nodes": nodes}
        return self.client.post_async(url, json=data)

    @version_wrap("2.0.0", "5.0.1")
    def release(self, reg_account, reg_password, force=None):
        url = "{}/release/".format(self.base_url)
        nodes = [_['id'] for _ in self.get_nodes()]
        data = {
            "nodes": nodes,
            "reg_account": reg_account, "reg_password": reg_password,
        }
        if force is not None:
            data["force"] = force
        return self.client.post_async(url, json=data)

    @version_wrap("5.1.0")
    def release(self):
        url = "{}/nodes/leave/".format(self.base_url)
        nodes = [_['id'] for _ in self.get_nodes()]
        data = {"nodes": nodes}
        return self.client.post_async(url, json=data)

    @version_wrap("2.0.0", "5.0.1")
    def renew_certificates(self, reg_server, reg_account, reg_password):
        url = "{}/register/".format(self.base_url)
        data = {
            "reg_account": reg_account, "reg_password": reg_password,
            "reg_server": reg_server
        }
        return self.client.put_async(url, json=data)


class VolumeParams(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/volume-params".format(
            base.get_id(self.cluster))
        super(VolumeParams, self).__init__(cluster.manager.api)

    def get(self):
        with failure_domains.api_version(self.client):
            return self.client.get(self.base_url)

    def change(self, redundancy, failure_domain, tier):
        data = {
            "redundancy": redundancy.to_api_dict(),
            "failure_domain": failure_domain,
            "tier": tier,
        }
        return self.client.put_async(self.base_url, json=data)


class StorageParams(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/storage-params".format(
            base.get_id(self.cluster))
        super(StorageParams, self).__init__(cluster.manager.api)

    def get(self):
        return self.client.get(self.base_url)

    def change(self, storage_type, storage_params):
        return self.client.put(
            self.base_url, json={
                'storage_params': storage_params,
                'storage_type': storage_type
            }
        )

    def verify(self, nodes, storage_type, storage_params):
        return self.client.post(
            url="{}/verify/".format(self.base_url),
            json={
                "nodes": nodes,
                "storage_params": storage_params,
                "storage_type": storage_type
            }
        )


class _BackupGatewayTask(base.PollTask):
    def __init__(self, api, resp):
        super(_BackupGatewayTask, self).__init__()
        self.api = api
        self.resp = resp

    def poll(self):
        process = self.get_info()
        if process is None:
            task = self.api.api.tasks.get(self.resp['task_id'])
            if task.state in ['success']:
                return {}

            elif task.state in ['aborted', 'cancelled', 'failed']:
                raise exceptions.VinfraError(
                    task.details or 'Task completed in {} state'.format(
                        task.state))

            return None

        elif process.get('failed'):
            return process

        return None

    def get_info(self):
        url = "{}/process/".format(self.api.base_url)
        return self.api.client.get(url)


class SysinfoConf(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/sysinfo-log".format(
            base.get_id(self.cluster))
        super(SysinfoConf, self).__init__(cluster.manager.api)

    def get(self):
        return self.client.get(self.base_url)

    def delete(self):
        return self.client.delete_async(self.base_url)

    def create(
            self,
            path=None,
            max_file_size=None,
            max_total_size=None,
            max_age=None
    ):
        data = {}
        if path is not None:
            data['path'] = path
        if max_file_size is not None:
            data['max_file_size'] = max_file_size
        if max_total_size is not None:
            data['max_total_size'] = max_total_size
        if max_age is not None:
            data['max_age'] = max_age
        return self.client.post_async(self.base_url, json=data)

    def update(
            self,
            path=None,
            max_file_size=None,
            max_total_size=None,
            max_age=None
    ):
        data = {}
        if path is not None:
            data['path'] = path
        if max_file_size is not None:
            data['max_file_size'] = max_file_size
        if max_total_size is not None:
            data['max_total_size'] = max_total_size
        if max_age is not None:
            data['max_age'] = max_age
        return self.client.put_async(self.base_url, json=data)


class ClientLimits(base.VinfraApi):

    def __init__(self, cluster):
        self.cluster = cluster
        self.base_url = "/{}/abgw/limits-params/".format(
            base.get_id(self.cluster))
        super(ClientLimits, self).__init__(cluster.manager.api)

    def get(self):
        return self.client.get(self.base_url)

    def update(
            self,
            max_connections=None,
            max_ingress=None,
            max_egress=None,
            apply_on_all_nodes=False
    ):
        data = {}
        if max_connections is not None:
            data['max_connections'] = max_connections
        if max_ingress is not None:
            data['max_ingress'] = max_ingress
        if max_egress is not None:
            data['max_egress'] = max_egress
        if apply_on_all_nodes:
            data['apply_on_all_nodes'] = apply_on_all_nodes

        return self.client.put_async(self.base_url, json=data)
