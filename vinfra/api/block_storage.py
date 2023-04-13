from vinfra.api import base
from vinfra.api.compute.storage_policies import get_api_redundancy
from vinfra.utils import flatten_args


class BlockStorageApi(base.VinfraApi):
    def __init__(self, cluster):
        self.cluster = cluster
        self.target_groups = TargetGroupManager(cluster)
        self.volumes = VolumeManager(cluster)
        self.users = UserManager(cluster)
        super(BlockStorageApi, self).__init__(cluster.manager.api)

    @property
    def base_url(self):
        return "/{}/iscsi-alua/".format(base.get_id(self.cluster))


class ACL(base.Resource):
    ID_ATTR = 'wwn'


class User(base.Resource):
    ID_ATTR = 'name'

    def delete_async(self):
        return self.manager.delete_async(self)


class Target(base.Resource):
    ID_ATTR = 'iqn'
    NAME_ATTR = 'iqn'

    def __init__(self, manager, info):
        super(Target, self).__init__(manager, info)
        self.connections = TargetConnectionManager(
            self.manager.cluster, self)

    def delete_async(self, force=None):
        return self.manager.delete_async(self, force=force)


class TargetConnection(base.Resource):
    pass


class TargetGroup(base.Resource):
    def __init__(self, manager, info):
        super(TargetGroup, self).__init__(manager, info)
        self.targets = TargetManager(self.manager.cluster, self)
        self.volumes = TargetGroupVolumeManager(self.manager.cluster, self)
        self.acls = ACLManager(self.manager.cluster, self)

    def delete_async(self, force=None):
        return self.manager.delete_async(self, force=force)

    def start_async(self):
        return self.manager.start_async(self)

    def stop_async(self):
        return self.manager.stop_async(self)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)


class Volume(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def update_async(self, **kwargs):
        return self.manager.update_async(self, **kwargs)


class TargetGroupVolume(base.Resource):
    def detach_async(self):
        return self.manager.detach_async(self)


class TargetManager(base.Manager):
    resource_class = Target

    def __init__(self, cluster, target_group):
        super(TargetManager, self).__init__(cluster.manager.api)
        self.cluster = cluster
        self.target_group = target_group

    @property
    def base_url(self):
        return "/{}/iscsi-alua/target-groups/{}/targets/".format(
            base.get_id(self.cluster),
            base.get_id(self.target_group))

    def list(self):
        return self._list(self.base_url)

    def create_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def delete_async(self, target, force=None):
        target_id = base.get_id(target)
        url = "{}{}/".format(self.base_url, target_id)
        return self.client.delete_async(url, json=flatten_args(force=force))


class TargetConnectionManager(base.Manager):
    resource_class = TargetConnection

    def __init__(self, cluster, target):
        super(TargetConnectionManager, self).__init__(cluster.manager.api)
        self.cluster = cluster
        self.target = target

    @property
    def base_url(self):
        return "/{}/iscsi-alua/connections/{}/".format(
            base.get_id(self.cluster),
            base.get_id(self.target.iqn))

    def list(self):
        return self._list(self.base_url)


class TargetGroupManager(base.Manager):
    resource_class = TargetGroup

    def __init__(self, cluster):
        super(TargetGroupManager, self).__init__(cluster.manager.api)
        self.cluster = cluster

    @property
    def base_url(self):
        return "/{}/iscsi-alua/target-groups/".format(
            base.get_id(self.cluster))

    def list(self):
        return self._list(self.base_url)

    def get(self, target_group):
        target_group_id = base.get_id(target_group)
        return self._get("{}{}/".format(self.base_url, target_group_id))

    def create_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def delete_async(self, target_group, force=None):
        target_group_id = base.get_id(target_group)
        url = "{}{}/".format(self.base_url, target_group_id)
        return self.client.delete_async(url, json=flatten_args(force=force))

    def start_async(self, target_group):
        target_group_id = base.get_id(target_group)
        url = "{}{}/start/".format(self.base_url, target_group_id)
        return self.client.post_async(url)

    def stop_async(self, target_group):
        target_group_id = base.get_id(target_group)
        url = "{}{}/stop/".format(self.base_url, target_group_id)
        return self.client.post_async(url)

    def update_async(self, target_group, **kwargs):
        target_group_id = base.get_id(target_group)
        json = flatten_args(**kwargs)
        if json.get('chap_enabled') is False:
            json['chap_user'] = None
        url = "{}{}/".format(self.base_url, target_group_id)
        return self.client.put_async(url, json=json)


class VolumeManager(base.Manager):
    resource_class = Volume

    def __init__(self, cluster):
        super(VolumeManager, self).__init__(cluster.manager.api)
        self.cluster = cluster

    @property
    def base_url(self):
        return "/{}/iscsi-alua/volumes/".format(
            base.get_id(self.cluster))

    def list(self):
        return self._list(self.base_url)

    def get(self, target_group):
        target_group_id = base.get_id(target_group)
        return self._get("{}{}/".format(self.base_url, target_group_id))

    def create_async(self, **kwargs):
        redundancy = kwargs.pop('redundancy', None)
        if redundancy:
            kwargs['redundancy'] = get_api_redundancy(redundancy)

        kwargs['volume_params'] = {
            param: kwargs.pop(param, None)
            for param in ['tier', 'failure_domain', 'redundancy']
        }

        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def delete_async(self, volume):
        volume_id = base.get_id(volume)
        url = "{}{}/".format(self.base_url, volume_id)
        return self.client.delete_async(url)

    def update_async(self, volume, **kwargs):
        volume_id = base.get_id(volume)
        url = "{}{}/".format(self.base_url, volume_id)
        return self.client.put_async(url, json=flatten_args(**kwargs))


class TargetGroupVolumeManager(base.Manager):
    resource_class = TargetGroupVolume

    def __init__(self, cluster, target_group):
        super(TargetGroupVolumeManager, self).__init__(cluster.manager.api)
        self.cluster = cluster
        self.target_group = target_group

    @property
    def base_url(self):
        return "/{}/iscsi-alua/target-groups/{}/volumes/".format(
            base.get_id(self.cluster),
            base.get_id(self.target_group))

    def list(self):
        return self._list(self.base_url)

    def get(self, volume):
        volume_id = base.get_id(volume)
        return self._get("{}{}/".format(self.base_url, volume_id))

    def attach_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def create(self, **kwargs):
        volume = kwargs.pop('volume', None)
        if volume:
            kwargs['volume_id'] = base.get_id(volume)
        return self._post(self.base_url, flatten_args(**kwargs))

    def detach_async(self, volume):
        volume_id = base.get_id(volume)
        url = "{}{}/".format(self.base_url, volume_id)
        return self.client.delete_async(url)


class UserManager(base.Manager):
    resource_class = User

    def __init__(self, cluster):
        super(UserManager, self).__init__(cluster.manager.api)
        self.cluster = cluster

    @property
    def base_url(self):
        return "/{}/iscsi-alua/users/".format(
            base.get_id(self.cluster))

    def list(self):
        return self._list(self.base_url)

    def create_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))

    def delete_async(self, user):
        user_id = base.get_id(user)
        url = "{}{}/".format(self.base_url, user_id)
        return self.client.delete_async(url)

    def update_async(self, user, **kwargs):
        user_id = base.get_id(user)
        url = "{}{}/".format(self.base_url, user_id)
        return self.client.put_async(url, json=flatten_args(**kwargs))


class ACLManager(base.Manager):
    resource_class = ACL

    def __init__(self, cluster, target_group):
        super(ACLManager, self).__init__(cluster.manager.api)
        self.cluster = cluster
        self.target_group = target_group

    @property
    def base_url(self):
        return "/{}/iscsi-alua/target-groups/{}/acl/".format(
            base.get_id(self.cluster),
            base.get_id(self.target_group))

    def list(self):
        return [self.resource_class(self, acl) for acl in  self.target_group.acl]

    def delete_async(self, acl):
        wwn = base.get_id(acl)
        url = "{}{}/".format(self.base_url, wwn)
        return self.client.delete_async(url)

    def update_async(self, acl, **kwargs):
        wwn = base.get_id(acl)
        url = "{}{}/".format(self.base_url, wwn)
        return self.client.put_async(url, json=flatten_args(**kwargs))

    def create_async(self, **kwargs):
        return self.client.post_async(
            self.base_url, json=flatten_args(**kwargs))
