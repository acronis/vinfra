from vinfra import exceptions
from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class VolumeCreateTask(base.PollTask):
    def __init__(self, resource):
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(VolumeCreateTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Volume (id={}) create waiting exceeded {} second(s) "
                   "timeout (status={})".format(base.get_id(self.resource),
                                                timeout, self.resource.status))
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.resource.get()
        if self.resource.status == 'creating':
            return None
        if self.resource.status == 'downloading':
            return None
        if self.resource.status != 'available':
            msg = "Volume status waiting failed (status={})".format(
                self.resource.status)
            raise exceptions.VinfraError(msg)

        return self.resource

    def get_info(self):
        return self.resource


class VolumeExtendTask(base.PollTask):
    def __init__(self, resource):
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(VolumeExtendTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Volume (id={}) extend waiting exceeded {} second(s) "
                   "timeout (status={})".format(base.get_id(self.resource),
                                                timeout, self.resource.status))
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.resource.get()
        if self.resource.status == 'extending':
            return None
        if self.resource.status == 'error_extending':
            msg = "Volume status extending failed (status={})".format(
                self.resource.status)
            raise exceptions.VinfraError(msg)

        return self.resource


class VolumeDeleteTask(base.PollTask):
    def __init__(self, manager, volume_id):
        self.manager = manager
        self.volume_id = volume_id

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(VolumeDeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Volume (id={}) delete waiting exceeded {} second(s) "
                   "timeout ".format(self.volume_id, timeout))
            raise exceptions.TimeoutError(msg)
        return None

    def poll(self):
        volumes = self.manager.list()
        for volume in volumes:
            if volume.id == self.volume_id:
                return None
        return {}

    def get_info(self):
        return None


class ResetStateTask(base.StatusTask):
    status = 'available'


class Volume(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def extend(self, *args, **params):
        return self.manager.extend(self, *args, **params)

    def extend_async(self, *args, **params):
        return self.manager.extend_async(self, *args, **params)

    def clone_async(self, *args, **params):
        return self.manager.clone_async(self, *args, **params)

    def upload_to_image_async(self, *args, **params):
        return self.manager.upload_to_image_async(self, *args, **params)

    def upload_to_image(self, *args, **params):
        return self.manager.upload_to_image(self, *args, **params)

    def reset_state_async(self):
        return self.manager.reset_state_async(self)


class VolumeManager(Manager):
    resource_class = Volume
    base_url = "/compute/volumes"

    def __init__(self, api, image_manager):
        super(VolumeManager, self).__init__(api)
        self.image_manager = image_manager

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, volume):
        volume_id = base.get_id(volume)
        return self._get("{}/{}".format(self.base_url, volume_id))

    def create_async(self, size, storage_policy_name, name=None,
                     description=None, network_install=None,
                     image=None, snapshot=None):
        json = dict(
            size=size,
            storage_policy_name=storage_policy_name,
        )
        json.update(flatten_args(
            name=name,
            description=description,
            network_install=network_install,
            image_id=image and base.get_id(image),
            snapshot_id=snapshot and base.get_id(snapshot)
            if snapshot else None,
        ))
        volume = self._post(self.base_url, json)
        return VolumeCreateTask(volume)

    @base.async_wait
    def create(self, size, storage_policy_name, **kwargs):
        return self.create_async(size, storage_policy_name, **kwargs)

    def delete_async(self, volume):
        volume_id = base.get_id(volume)
        self._delete("{}/{}".format(self.base_url, volume_id))
        return VolumeDeleteTask(self, volume_id)

    @base.async_wait
    def delete(self, volume):
        return self.delete_async(volume)

    def update(self, volume, name=None, storage_policy_name=None,
               description=None, network_install=None, bootable=None,
               no_placements=None):
        volume_id = base.get_id(volume)
        json = flatten_args(
            name=name,
            storage_policy_name=storage_policy_name,
            description=description,
            network_install=network_install,
            bootable=bootable,
            no_placements=no_placements
        )
        return self._patch("{}/{}".format(self.base_url, volume_id), json)

    @base.async_wait
    def extend(self, volume, size):
        return self.extend_async(volume, size)

    def extend_async(self, volume, size):
        json = dict(size=size)
        url = "{}/{}/extend".format(self.base_url, base.get_id(volume))
        self._post(url, json=json)
        return VolumeExtendTask(volume)

    def clone_async(self, volume, name, storage_policy_name=None, size=None):
        json = dict(name=name)
        json.update(flatten_args(
            storage_policy_name=storage_policy_name,
            size=size,
        ))

        url = "{}/{}/clone".format(self.base_url, base.get_id(volume))
        new_volume = self._post(url, json=json)
        return VolumeCreateTask(new_volume)

    def upload_to_image_async(self, volume, name=None):
        volume_id = base.get_id(volume)
        json = flatten_args(
            image_name=name,
        )

        data = self.client.post(
            '{}/{}/upload-to-image'.format(self.base_url, volume_id), json=json
        )

        image = self.image_manager.create_resource(data)
        return self.image_manager.make_upload_task(image)

    @base.async_wait
    def upload_to_image(self, volume, name=None):
        return self.upload_to_image_async(volume, name=name)

    def reset_state_async(self, volume):
        url = "{}/{}/reset-state".format(self.base_url, base.get_id(volume))
        self.client.post(url, json={})
        return ResetStateTask(self, volume)

    @base.async_wait
    def reset_state(self, *args, **kwargs):
        return self.reset_state_async(*args, **kwargs)
