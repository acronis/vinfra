from vinfra import api_versions
from vinfra import exceptions
from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class K8saasClusterCreateTask(base.PollTask):
    def __init__(self, resource, workers):
        self.resource = resource
        self.workers = workers

    def wait(self, timeout=None):
        # set default timeout to 30 minutes
        # +5 minutes extra for additional worker
        # Fix TaskCommand.task_wait() without default timeout 600 sec
        # This workaround uses a default progress bar of 10 minutes.
        # If the task runs longer,
        # the progress bar will stop counting after 10 minutes,
        # but the task will continue to run until the correct timeout period
        # has expired (1800 seconds or more).
        extended_timeout = 1500 + (self.workers * 300)
        timeout = timeout if timeout > extended_timeout else extended_timeout
        try:
            resource = super(K8saasClusterCreateTask, self).wait(
                timeout=timeout
            )
        except exceptions.TimeoutError:
            msg = ("Creation of a Kubernetes cluster (id={}) exceeded the "
                   "{}-second timeout (status={}).".format(
                       base.get_id(self.resource), timeout,
                       self.resource.status))
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.resource.get()
        if self.resource.status == 'CREATING' or \
                self.resource.status == 'NOT_READY':
            return None
        if self.resource.status != 'ACTIVE':
            msg = ("Failed to create a Kubernetes cluster "
                   "(status={})".format(self.resource.status))
            raise exceptions.VinfraError(msg)

        return self.resource

    def get_info(self):
        return self.resource


class K8saasClusterDeleteTask(base.PollTask):
    def __init__(self, manager, cluster_id):
        super(K8saasClusterDeleteTask, self).__init__()
        self.manager = manager
        self.cluster_id = cluster_id

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(K8saasClusterDeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Deletion of a Kubernetes cluster (id={}) exceeded the "
                   "{}-second timeout.".format(self.cluster_id, timeout))
            raise exceptions.TimeoutError(msg)
        return None

    def poll(self):
        clusters = self.manager.list()
        for cluster in clusters:
            if cluster.id == self.cluster_id:
                return None
        return {}

    def get_info(self):
        return None


class K8saasClusterStartUpdateTask(base.PollTask):
    def __init__(self, manager, resource):
        super(K8saasClusterStartUpdateTask, self).__init__()
        self.manager = manager
        self.resource = resource
        self.updated_at = resource.updated_at

    def poll(self):
        self.resource = self.manager.get(self.resource)
        # We can't guarantee that changing 'updated_at'
        # field indicates an action was started: this field may be changed
        # by magnum sync_cluster_health_status periodic task that can be run
        # in parallel with a user action (see #VSTOR-40637 and #VSTOR-40656)
        if self.resource.updated_at != self.updated_at:
            return self.resource
        return None

    def get_info(self):
        return self.resource


class K8saasClusterUpdateTask(base.StatusTask):
    status = 'ACTIVE'


class K8saasClusterRotateCATask(base.StatusTask):
    status = 'ACTIVE'


class K8saasClusterUpgradeTask(base.StatusTask):
    status = 'ACTIVE'


class K8saasCluster(base.Resource):
    @property
    def nodegroups_manager(self):
        return K8saasNodeGroupManager(self.manager.api, self)

    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def update_async(self, **params):
        return self.manager.update_async(self, **params)

    def rotate_ca_async(self):
        return self.manager.rotate_ca_async(self)

    def upgrade_async(self, **params):
        return self.manager.upgrade_async(self, **params)

    def healthcheck(self):
        return self.manager.healthcheck(self)


class K8saasClusterManager(Manager):
    resource_class = K8saasCluster
    base_url = "/compute/k8saas"

    def list(self):
        return self._list(self.base_url)

    def get(self, cluster):
        cluster_id = base.get_id(cluster)
        return self._get("{}/{}".format(self.base_url, cluster_id))

    def get_config(self, cluster):
        cluster_id = base.get_id(cluster)
        return self.client.get("{}/{}/config".format(self.base_url,
                                                     cluster_id))

    def create_async(self, **kwargs):
        json = dict()
        json.update(flatten_args(**kwargs))
        cluster = self._post(self.base_url, json)
        workers = 1
        if 'node_count' in json['worker_pools'][0]:
            workers = json['worker_pools'][0]['node_count']
        return K8saasClusterCreateTask(cluster, workers)

    @base.async_wait
    def create(self, **kwargs):
        return self.create_async(**kwargs)

    def delete_async(self, cluster):
        cluster_id = base.get_id(cluster)
        self._delete("{}/{}".format(self.base_url, cluster_id))
        return K8saasClusterDeleteTask(self, cluster_id)

    @base.async_wait
    def delete(self, cluster):
        return self.delete_async(cluster)

    def update_async(self, cluster, **kwargs):
        cluster_id = base.get_id(cluster)
        json = flatten_args(**kwargs)
        self._patch("{}/{}".format(self.base_url, cluster_id), json)
        return base.ChainedTask(cluster,
                                K8saasClusterStartUpdateTask(self, cluster),
                                K8saasClusterUpdateTask(self, cluster))

    @base.async_wait
    def update(self, **kwargs):
        return self.update_async(**kwargs)

    def rotate_ca_async(self, cluster):
        cluster_id = base.get_id(cluster)
        self._post("{}/{}/rotate-ca".format(self.base_url, cluster_id))
        return K8saasClusterRotateCATask(self, cluster)

    def upgrade_async(self, cluster, **kwargs):
        cluster_id = base.get_id(cluster)
        json = flatten_args(**kwargs)
        self._post("{}/{}/upgrade".format(self.base_url, cluster_id), json)
        return K8saasClusterUpgradeTask(self, cluster)

    @base.async_wait
    def upgrade(self, **kwargs):
        return self.update_async(**kwargs)

    def healthcheck(self, cluster):
        if self.api.api_version < api_versions.HCI_VER_47:
            return

        cluster_id = base.get_id(cluster)
        return self._get("{}/{}/health".format(self.base_url, cluster_id))

    def get_defaults(self, version=None):
        url = '{}/defaults/{}'.format(
            self.base_url, version if version else '')
        return self.client.get(url)

    def set_defaults(self, version, **kwargs):
        params = flatten_args(**kwargs)
        labels = kwargs.get('labels')
        if labels:
            for key in ('auto_scaling_enabled', 'monitoring_enabled'):
                value = str(labels.get(key, '')).lower()
                if value == 'true':
                    labels[key] = True
                elif value == 'false':
                    labels[key] = False
        url = "{}/defaults/{}".format(self.base_url, version)
        return self.client.patch(url, json=params)


class K8saasNodeGroupCreateTask(base.PollTask):
    def __init__(self, resource):
        self.resource = resource

    def poll(self):
        self.resource = self.resource.get()
        if self.resource.status == 'CREATING' or \
                self.resource.status == 'NOT_READY':
            return None
        if self.resource.status != 'ACTIVE':
            msg = ("Failed to create a Kubernetes worker group "
                   "(status={})".format(self.resource.status))
            raise exceptions.VinfraError(msg)

        return self.resource

    def get_info(self):
        return self.resource


class K8saasNodeGroupDeleteTask(base.PollTask):
    def __init__(self, manager, nodegroup_id):
        super(K8saasNodeGroupDeleteTask, self).__init__()
        self.manager = manager
        self.nodegroup_id = nodegroup_id

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(K8saasNodeGroupDeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Deletion of a Kubernetes worker group (id={}) exceeded the "
                   "{}-second timeout.".format(self.nodegroup_id, timeout))
            raise exceptions.TimeoutError(msg)
        return None

    def poll(self):
        nodegroups = self.manager.list()
        for ng in nodegroups:
            if ng.id == self.nodegroup_id:
                return None
        return {}

    def get_info(self):
        return None


class K8saasNodeGroupUpdateTask(base.StatusTask):
    status = 'ACTIVE'


class K8saasNodeGroupUpgradeTask(base.StatusTask):
    status = 'ACTIVE'


class K8saasNodeGroup(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def update_async(self, **params):
        return self.manager.update_async(self, **params)

    def upgrade_async(self, **params):
        return self.manager.upgrade_async(self, **params)


class K8saasNodeGroupManager(Manager):
    resource_class = K8saasNodeGroup
    _base_url = "/compute/k8saas/{}/nodegroups"

    def __init__(self, api, cluster):
        super(K8saasNodeGroupManager, self).__init__(api)
        self.cluster = cluster
        self.base_url = self._base_url.format(cluster.id)

    def list(self):
        return self._list(self.base_url)

    def get(self, nodegroup):
        nodegroup_id = base.get_id(nodegroup)
        return self._get("{}/{}".format(self.base_url, nodegroup_id))

    def create_async(self, **kwargs):
        json = dict()
        json.update(flatten_args(**kwargs))
        nodegroup = self._post(self.base_url, json)
        return K8saasNodeGroupCreateTask(nodegroup)

    @base.async_wait
    def create(self, **kwargs):
        return self.create_async(**kwargs)

    def delete_async(self, nodegroup):
        nodegroup_id = base.get_id(nodegroup)
        self._delete("{}/{}".format(self.base_url, nodegroup_id))
        return K8saasNodeGroupDeleteTask(self, nodegroup_id)

    @base.async_wait
    def delete(self, nodegroup):
        return self.delete_async(nodegroup)

    def update_async(self, nodegroup, **kwargs):
        nodegroup_id = base.get_id(nodegroup)
        json = flatten_args(**kwargs)
        self._patch("{}/{}".format(self.base_url, nodegroup_id), json)
        return base.ChainedTask(
            nodegroup,
            # nodegroup doesn't provide updated_at so
            # we use K8saasClusterStartUpdateTask
            K8saasClusterStartUpdateTask(self.cluster.manager, self.cluster),
            K8saasNodeGroupUpdateTask(self, nodegroup_id))

    @base.async_wait
    def update(self, **kwargs):
        return self.update_async(**kwargs)

    def upgrade_async(self, nodegroup, **kwargs):
        nodegroup_id = base.get_id(nodegroup)
        json = flatten_args(**kwargs)
        self._post("{}/{}/upgrade".format(self.base_url, nodegroup_id), json)
        return base.ChainedTask(
            nodegroup,
            # nodegroup doesn't provide updated_at so
            # we use K8saasClusterStartUpdateTask
            K8saasClusterStartUpdateTask(self.cluster.manager, self.cluster),
            K8saasNodeGroupUpgradeTask(self, nodegroup_id))

    @base.async_wait
    def upgrade(self, **kwargs):
        return self.update_async(**kwargs)
