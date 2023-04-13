from vinfra import exceptions, api_versions
from vinfra.api import base


NETWORK_TASK_TIMEOUT = 3600  # 1 hour


class _NetworkPoolTaskBase(base.PollTask):
    poll_interval = 15

    good_states = []
    error_states = []

    def __init__(self, manager, initial_data):
        super(_NetworkPoolTaskBase, self).__init__()
        self.manager = manager
        self.initial_data = initial_data

    def wait(self, timeout=None):
        timeout = timeout or NETWORK_TASK_TIMEOUT
        try:
            data = super(_NetworkPoolTaskBase, self).wait(timeout=timeout)
        except exceptions.PollTimeoutError as exc:
            msg = ("{} (task_id={}) exceeded {}-second "
                   "wait timeout (state: {}, expected: {})"
                   .format(self.manager.operation_name, self.initial_data['task_id'], timeout,
                           exc.last_result and exc.last_result['state'],
                           ', '.join(self.good_states)))
            raise exceptions.PollTimeoutError(msg, exc.last_result)
        return data

    def poll(self):
        task = self.manager.get_resource(self.initial_data['task_id'])
        current_data = task.to_dict()
        if int(current_data['transitions']) > int(self.initial_data['transitions']):
            if current_data['state'] in self.good_states:
                return current_data
            if current_data['state'] in self.error_states:
                raise exceptions.VinfraError(
                    '{} failed with state "{}".'
                    .format(self.manager.operation_name, task.state))
        # no transitions (maybe the task did not start yet)
        # or the task is in intermediate status -> continue polling
        return None

    def get_info(self):
        return self.initial_data


class _AssignmentStartTask(_NetworkPoolTaskBase):
    good_states = ['done', 'test-passed']
    error_states = ['halted', 'interrupted', 'test-failed']


class _AssignmentApplyTask(_NetworkPoolTaskBase):
    good_states = ['done']
    error_states = ['failed-to-apply']


class _AssignmentRevertTask(_NetworkPoolTaskBase):
    good_states = ['interrupted']
    error_states = ['failed-to-revert']


class _AssignmentRetryTask(_NetworkPoolTaskBase):
    good_states = ['test-passed', 'interrupted', 'done']
    error_states = ['test-failed', 'failed-to-revert', 'failed-to-apply']


class _NetworkMigrationStartTask(_NetworkPoolTaskBase):
    good_states = [
        'test-passed',                 # If shutdown not required.
        'waiting-for-shutdown',        # Otherwise.
    ]
    error_states = [
        'halted',
        'interrupted',
        'test-failed',                 # If shutdown not required.
        'failed-to-store',             # Otherwise.
    ]


class _NetworkMigrationApplyTask(_NetworkPoolTaskBase):
    good_states = ['applied', 'done']
    error_states = ['failed-to-apply']


class _NetworkMigrationRevertTask(_NetworkPoolTaskBase):
    good_states = [
        'interrupted',
        'test-passed',           # When revert gets to irreversible state due to
        'test-failed',           # temporary network issues, the process is stopped,
        'waiting-for-shutdown',  # and it should be tried later again.
    ]
    error_states = ['failed-to-revert']


class _NetworkMigrationRetryTask(_NetworkPoolTaskBase):
    good_states = [
        'waiting-for-shutdown',  # Datacenter 1
        'test-passed',           # Datacenter 1 or 2 ...
        'interrupted',
        'applied',
        'done',
    ]
    error_states = [
        'failed-to-store',       # Datacenter 1
        'test-failed',           # Datacenter 1 or 2 ...
        'failed-to-revert',
        'failed-to-apply',
    ]


class _NetworkMigrationResumeTask(_NetworkPoolTaskBase):
    good_states = ['test-passed']
    error_states = ['test-failed']


class SetBulkTask(base.BackendTask):
    def __init__(self, manager, data):
        super(SetBulkTask, self).__init__(manager.api, data)
        self.manager = manager

    def wait(self, timeout=None):
        networks = super(SetBulkTask, self).wait(timeout=timeout)
        if networks is None:
            return None
        return [self.manager.create_resource(network) for network in networks]


class Network(base.Resource):
    def __init__(self, manager, info):
        if 'roles' in info:
            info = dict(info)
            info['traffic_types'] = info.pop('roles')
        super(Network, self).__init__(manager, info)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def delete(self):
        return self.manager.delete(self)


class NetworkManager(base.Manager):
    resource_class = Network
    base_url = "/network/interface/roles_sets"

    def list(self):
        return self._list(self.base_url)

    def get(self, network):
        network_id = base.get_id(network)
        return self._get("{}/{}".format(self.base_url, network_id))

    def create(self, name, traffic_types=None,
               inbound_allow_list=None, inbound_deny_list=None,
               outbound_allow_list=None):
        data = {'name': name}
        if traffic_types is not None:
            data['roles'] = traffic_types
        if inbound_allow_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_allow_list'] = inbound_allow_list
            else:
                data['allow_list'] = inbound_allow_list
        if inbound_deny_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_deny_list'] = inbound_deny_list
            else:
                data['deny_list'] = inbound_deny_list
        if outbound_allow_list is not None:
            data['outbound_allow_list'] = outbound_allow_list

        return self._post(self.base_url, json=data)

    def update_async(self, network, name=None, traffic_types=None,
                     inbound_allow_list=None, inbound_deny_list=None,
                     outbound_allow_list=None):
        data = {}
        if name is not None:
            data['name'] = name
        if traffic_types is not None:
            data['roles'] = traffic_types
        if inbound_allow_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_allow_list'] = inbound_allow_list
            else:
                data['allow_list'] = inbound_allow_list
        if inbound_deny_list is not None:
            if self.api.api_version >= api_versions.HCI_VER_46:
                data['inbound_deny_list'] = inbound_deny_list
            else:
                data['deny_list'] = inbound_deny_list
        if outbound_allow_list is not None:
            data['outbound_allow_list'] = outbound_allow_list

        url = "{}/{}".format(self.base_url, base.get_id(network))
        return self._put_async(url, json=data)

    @base.async_wait
    def update(self, network, **kwargs):
        return self.update_async(network, **kwargs)

    def update_bulk_async(self, network_traffic_type_list):
        data = {'roles_sets': []}
        for network, traffic_types in network_traffic_type_list:
            data['roles_sets'].append({
                'id': network,
                'roles': traffic_types
            })
        data = self.client.put(self.base_url, json=data)
        return SetBulkTask(self, data)

    @base.async_wait
    def update_bulk(self, network_traffic_type_list):
        return self.update_bulk_async(network_traffic_type_list)

    def delete(self, network):
        network_id = base.get_id(network)
        return self._delete("{}/{}".format(self.base_url, network_id))

    @property
    def ipsec(self):
        return IPsecManager(self.api)

    @property
    def ipv6_prefix(self):
        return IPv6PrefixManager(self.api)


class NetworkReconfiguration(base.VinfraApi):
    def get_reconfiguration(self):
        return self.client.get('/network/reconfiguration')


class TrafficTypeAssignment(base.Resource):
    def apply(self):
        return self.manager.apply(assignment=self)

    def revert(self):
        return self.manager.revert(assignment=self)

    def retry(self):
        return self.manager.retry(assignment=self)


class TrafficTypeAssignmentManager(base.Manager):
    resource_class = TrafficTypeAssignment
    base_url = '/network/traffic-type-assignment'
    operation_name = 'Traffic type assignment'

    def get_resource(self, task_id, full=False, stat=False):
        url = '{}/{}'.format(self.base_url, task_id)
        if stat:
            url += '?stat'
        data = self.client.get(url)
        if not full:
            data.pop('configuration', None)
        return self.resource_class(self, data)

    def start(self, traffic_type, target_network):
        data = self.client.post(
            self.base_url,
            json={'traffic_type': traffic_type,
                  'target_network': target_network}
        )
        return _AssignmentStartTask(self, data)

    def apply(self, assignment):
        data = self.client.post('{}/{}/apply'.format(self.base_url, assignment.task_id))
        return _AssignmentApplyTask(self, data)

    def revert(self, assignment):
        data = self.client.post('{}/{}/revert'.format(self.base_url, assignment.task_id))
        return _AssignmentRevertTask(self, data)

    def retry(self, assignment):
        data = self.client.post('{}/{}/retry'.format(self.base_url, assignment.task_id))
        return _AssignmentRetryTask(self, data)


class NetworkMigration(base.Resource):
    def apply(self):
        return self.manager.apply(migration=self)

    def revert(self):
        return self.manager.revert(migration=self)

    def retry(self, subnet, netmask, nodes):
        return self.manager.retry(migration=self,
                                  subnet=subnet,
                                  netmask=netmask,
                                  nodes=nodes)

    def resume(self):
        return self.manager.resume(migration=self)


class NetworkMigrationManager(base.Manager):
    resource_class = NetworkMigration
    base_url = '/network/migration'
    operation_name = 'Network migration'

    def get_resource(self, task_id, full=False, stat=False):
        url = '{}/{}'.format(self.base_url, task_id)
        if stat:
            url += '?stat'
        data = self.client.get(url)
        if not full:
            data.pop('configuration', None)
        return self.resource_class(self, data)

    def start(self, network_id, subnet, netmask, gateway, shutdown, nodes):
        params = {'network_id': network_id}
        if subnet:
            params['subnet'] = subnet
        if netmask:
            params['netmask'] = netmask
        if gateway:
            params['gateway'] = gateway
        if shutdown:
            params['shutdown_required'] = shutdown
        if nodes:
            nodes_params = []
            for nd in nodes:
                node = {'node_id': nd['node_id'],
                        'new_ip_address': nd['address']}
                if subnet:
                    node['subnet'] = subnet
                nodes_params.append(node)
            params['nodes'] = nodes_params

        data = self.client.post(
            self.base_url,
            json=params
        )
        return _NetworkMigrationStartTask(self, data)

    def apply(self, migration):
        data = self.client.post('{}/{}/apply'.format(self.base_url, migration.task_id))
        return _NetworkMigrationApplyTask(self, data)

    def revert(self, migration):
        data = self.client.post('{}/{}/revert'.format(self.base_url, migration.task_id))
        return _NetworkMigrationRevertTask(self, data)

    def retry(self, migration, subnet, netmask, nodes):
        params = {}
        if subnet:
            params['subnet'] = subnet
        if netmask:
            params['netmask'] = netmask
        if nodes:
            nodes_params = []
            for nd in nodes:
                node = {'node_id': nd['node_id'],
                        'new_ip_address': nd['address']}
                if subnet:
                    node['subnet'] = subnet
                nodes_params.append(node)
            params['nodes'] = nodes_params

        self.client.post(
            '{}/{}/retry'.format(self.base_url, migration.task_id),
            json=params
        )
        return _NetworkMigrationRetryTask(self, migration.to_dict())

    def resume(self, migration):
        data = self.client.post('{}/{}/resume'.format(self.base_url, migration.task_id))
        return _NetworkMigrationResumeTask(self, data)


class NetworkConversionTask(base.ResourceTask):
    def wait(self, timeout=None):
        super(NetworkConversionTask, self).wait(timeout)
        return self.resource_manager.get_raw_status(self.data['task_id'])


class NetworkConversionManager(base.Manager):
    base_url = '/network/interface/roles_sets/convert2ovs'

    def start(self, network, name):
        network_id = base.get_id(network)
        data = {'id': network_id}
        if name is not None:
            data['name'] = name
        return NetworkConversionTask(
            self, self.client.post(self.base_url, json=data), connect_retries=10)

    def precheck(self, network, name):
        network_id = base.get_id(network)
        data = {'id': network_id}
        if name is not None:
            data['name'] = name
        rv = self._post(self.base_url + '-precheck', json=data)
        return rv

    def get_raw_status(self, task_id):
        return self.client.get('{}/{}'.format(self.base_url, task_id))

    def get_status(self, task_id):
        rv = self.get_raw_status(task_id)
        return NetworkConversionTask(self, rv)


class IPsecManager(base.VinfraApi):
    base_url = '/network/ipsec'

    def action(self, verb, networks, switch_storage_ipv6=None):
        network_ids = [base.get_id(net) for net in networks]
        data = {'roles_sets': network_ids}
        if switch_storage_ipv6 is not None:
            data['switch_storage_ipv6'] = switch_storage_ipv6
        return self.client.post_async('{}/{}'.format(self.base_url, verb), json=data)

    def enable(self, networks, switch_storage_ipv6):
        return self.action('enable', networks, switch_storage_ipv6)

    def disable(self, networks):
        return self.action('disable', networks)

    def cancel(self):
        return self.client.post('{}/cancel'.format(self.base_url))

    def add_bypass(self, subnets, ports):
        data = {'subnets': subnets, 'ports': ports}
        return self.client.put('{}/bypass'.format(self.base_url), json=data)

    def del_bypass(self, subnets, ports):
        data = {'subnets': subnets, 'ports': ports}
        return self.client.delete('{}/bypass'.format(self.base_url), json=data)

    def get_bypass(self):
        return self.client.get('{}/bypass'.format(self.base_url))


class IPv6PrefixManager(base.VinfraApi):
    base_url = '/network/ipv6-prefix/'

    def assign(self, prefix, force):
        data = {'prefix': prefix, 'force': force}
        return self.client.post_async(self.base_url, json=data)

    def remove(self, force):
        data = {'force': force}
        return self.client.delete_async(self.base_url, json=data)

    def get_prefix(self):
        return self.client.get(self.base_url)
