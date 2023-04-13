from vinfra.api import base


class Cluster(object):
    base_url = "/compute/cluster"

    def __init__(self, api):
        self.api = api

    def get(self):
        data = self.api.client.get(self.base_url)
        data.pop("early_access", None)
        return data

    def create_async(self, nodes, external_network=None, cpu_model=None,
                     force=None, enable_k8saas=None, enable_lbaas=None,
                     enable_metering=None, custom_params=None,
                     notification_forwarding=None,
                     external_address=None, pci_passthrough=None,
                     default_storage_policy=None, scheduler=None,
                     cpu_features=None):
        data = {'nodes': [base.get_id(v) for v in nodes]}
        if external_network is not None:
            data['external_network'] = external_network
        if cpu_model is not None:
            data['cpu_model'] = cpu_model
        if force is not None:
            data['force'] = force

        enable_features = []
        if enable_k8saas is not None:
            enable_features.append('k8saas')
        if enable_lbaas is not None:
            enable_features.append('lbaas')
        if enable_metering is not None:
            enable_features.append('metering')
        if enable_features:
            data['enable_features'] = enable_features

        if notification_forwarding is not None:
            data['notification_forwarding'] = dict(
                transport_url=notification_forwarding or None)

        if data.get('external_network', {}).get('network_id'):
            network = dict(data['external_network'])
            network['roles_set_id'] = network.pop('network_id')
            data['external_network'] = network

        if custom_params is not None:
            data['custom_params'] = custom_params

        if external_address is not None:
            data['external_address'] = external_address

        if pci_passthrough is not None:
            data['pci_passthrough'] = pci_passthrough

        if scheduler is not None:
            data['scheduler'] = scheduler

        if default_storage_policy is not None:
            default_storage_policy = dict(default_storage_policy)
            if 'redundancy' in default_storage_policy:
                default_storage_policy['redundancy'] = \
                    default_storage_policy['redundancy'].to_api_dict()
            data['default_storage_policy'] = default_storage_policy

        if cpu_features is not None:
            data['cpu_features'] = cpu_features

        # Creating compute cluster may lead to connection errors due to ovs
        # bridge building. Take it into account by setting a connect_retries
        # and a connect_retry_delay 'task_params' values:
        task_params = {
            'connect_retries': 8,
            'connect_retry_delay': 0.3,
        }
        return self.api.client.post_async(self.base_url, json=data,
                                          task_params=task_params)

    @base.async_wait
    def create(self, nodes, **params):
        return self.create_async(nodes, **params)

    def delete_async(self):
        # Deleting compute cluster may lead to connection errors due to
        # nginx is reloading. See #VSTOR-27813 for details.
        task_params = {
            'connect_retries': 2,
            'connect_retry_delay': 0.3
        }
        return self.api.client.delete_async(self.base_url,
                                            task_params=task_params)

    @base.async_wait
    def delete(self):
        return self.delete_async()

    def stat(self):
        return self.api.client.get("%s/stat" % self.base_url)

    def info(self):
        return self.api.client.get("%s/info" % self.base_url)

    def reconfigure_async(self, cpu_model=None, enable_k8saas=None,
                          enable_lbaas=None, enable_metering=None,
                          custom_params=None, notification_forwarding=None,
                          external_address=None, early_access=None,
                          force=None, pci_passthrough=None,
                          scheduler=None, cpu_features=None):
        data = {}
        if cpu_model is not None:
            data['cpu_model'] = cpu_model
        if early_access is not None:
            data['early_access'] = early_access

        enable_features = []
        if enable_k8saas is not None:
            enable_features.append('k8saas')
        if enable_lbaas is not None:
            enable_features.append('lbaas')
        if enable_metering is not None:
            enable_features.append('metering')
        if enable_features:
            data['enable_features'] = enable_features

        if custom_params is not None:
            data['custom_params'] = custom_params
        if notification_forwarding is not None:
            data['notification_forwarding'] = dict(
                transport_url=notification_forwarding or None)
        if force is not None:
            data['force'] = force
        if external_address is not None:
            data['external_address'] = external_address
        if pci_passthrough is not None:
            data['pci_passthrough'] = pci_passthrough
        if scheduler is not None:
            data['scheduler'] = scheduler
        if cpu_features is not None:
            data['cpu_features'] = cpu_features

        return self.api.client.patch_async(self.base_url, json=data)

    @base.async_wait
    def reconfigure(self, *args, **kwargs):
        return self.reconfigure_async(*args, **kwargs)

    def show_task(self, task_id=None):
        id_string = ('/' + task_id + '/') if task_id else '/'
        url = "{}/tasks{}".format(self.base_url, id_string)
        return self.api.client.get(url)

    def retry_task(self, task_id=None):
        id_string = ('/' + task_id + '/') if task_id else '/'
        url = "{}/tasks{}retry/".format(self.base_url, id_string)
        return self.api.client.post(url)

    def abort_task(self, task_id=None):
        id_string = ('/' + task_id + '/') if task_id else '/'
        url = "{}/tasks{}abort/".format(self.base_url, id_string)
        return self.api.client.post(url)
