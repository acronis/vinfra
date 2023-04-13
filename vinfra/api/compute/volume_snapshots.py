from vinfra import exceptions
from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class VolumeSnapshotCreateTask(base.PollTask):
    def __init__(self, resource):
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(VolumeSnapshotCreateTask, self).wait(
                timeout=timeout)
        except exceptions.TimeoutError:
            msg = (
                "Failed to create volume snapshot (id={}). Timeout of {} "
                "seconds exceeded (status={}).".format(
                    base.get_id(self.resource), timeout, self.resource.status)
            )
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.resource.get()
        if self.resource.status == 'creating':
            return None
        if self.resource.status != 'available':
            msg = (
                "Failed to get volume snapshot status (status={}).".format(
                    self.resource.status)
            )
            raise exceptions.VinfraError(msg)

        return self.resource

    def get_info(self):
        return self.resource


class VolumeSnapshotDeleteTask(base.PollTask):
    def __init__(self, manager, volume_id, resource):
        self.manager = manager
        self.volume_id = volume_id
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(VolumeSnapshotDeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = (
                "Failed to delete volume snapshot (id={}). Timeout of {} "
                "seconds exceeded (status={})".format
                (self.volume_id, timeout, self.resource.get().status)
            )
            raise exceptions.TimeoutError(msg)

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


class RevertToSnapshot(base.StatusTask):
    status = 'available'


class VolumeSnapshot(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def upload_to_image_async(self, *args, **params):
        return self.manager.upload_to_image_async(self, *args, **params)

    def upload_to_image(self, *args, **params):
        return self.manager.upload_to_image(self, *args, **params)

    def reset_state_async(self):
        return self.manager.reset_state_async(self)

    def revert_to_snapshot(self):
        return self.manager.revert_to_snapshot(self)


class VolumeSnapshotManager(Manager):
    resource_class = VolumeSnapshot
    base_url = "/compute/volume_snapshots"

    def __init__(self, api, image_manager):
        super(VolumeSnapshotManager, self).__init__(api)
        self.image_manager = image_manager

    def list(self, volume=None):
        if volume:
            payload = {'volume_id': volume}
            return self._list(self.base_url, params=payload)
        return self._list(self.base_url)

    def get(self, volume_snapshot):
        snapshot_id = base.get_id(volume_snapshot)
        return self._get("{}/{}".format(self.base_url, snapshot_id))

    def create_async(self, volume_id, name=None, description=None):
        payload = dict(
            volume_id=volume_id,
        )
        payload.update(flatten_args(
            name=name,
            description=description,
        ))
        volume_snapshot = self._post(self.base_url, payload)
        return VolumeSnapshotCreateTask(volume_snapshot)

    @base.async_wait
    def create(self, volume_id, **kwargs):
        return self.create_async(volume_id, **kwargs)

    def delete_async(self, volume_snapshot):
        snapshot_id = base.get_id(volume_snapshot)
        self._delete("{}/{}".format(self.base_url, snapshot_id))
        return VolumeSnapshotDeleteTask(self, snapshot_id, volume_snapshot)

    @base.async_wait
    def delete(self, volume_snapshot):
        return self.delete_async(volume_snapshot)

    def update(self, volume_snapshot, name=None, description=None):
        snapshot_id = base.get_id(volume_snapshot)
        payload = flatten_args(
            name=name,
            description=description,
        )
        return self._patch("{}/{}".format(self.base_url, snapshot_id), payload)

    def upload_to_image_async(self, volume_snapshot, name=None):
        snapshot_id = base.get_id(volume_snapshot)
        payload = flatten_args(
            image_name=name,
        )

        data = self.client.post(
            '{}/{}/upload-to-image'.format(self.base_url, snapshot_id),
            json=payload
        )

        image = self.image_manager.create_resource(data)
        return self.image_manager.make_upload_task(image)

    @base.async_wait
    def upload_to_image(self, volume_snapshot, name=None):
        return self.upload_to_image_async(volume_snapshot, name=name)

    def reset_state_async(self, volume_snapshot):
        url = "{}/{}/reset-state".format(
            self.base_url, base.get_id(volume_snapshot)
        )
        self.client.post(url)
        return ResetStateTask(self, volume_snapshot)

    @base.async_wait
    def reset_state(self, *args, **kwargs):
        return self.reset_state_async(*args, **kwargs)

    def revert_to_snapshot(self, volume_snapshot):
        url = "{}/{}/revert".format(
            self.base_url, base.get_id(volume_snapshot)
        )
        self.client.post(url)
        return RevertToSnapshot(self, volume_snapshot)
