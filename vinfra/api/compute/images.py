import base64
import hashlib
import json
import os

from vinfra import exceptions
from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.compat import md5
from vinfra.utils import flatten_args


def params_to_headers(**params):
    headers = {}
    for key, value in params.items():
        headers['x-hci-image-' + key.replace('_', '-')] = str(value)
    return headers


class ImageUploadTask(base.PollTask):
    def __init__(self, resource):
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(ImageUploadTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Image (id={}) upload waiting exceeded {} second(s) "
                   "timeout (status={})".format(base.get_id(self.resource),
                                                timeout, self.resource.status))
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.resource.get()
        status = self.resource.status

        if status in ['creating', 'queued', 'saving']:
            return None
        if status != 'active':
            raise exceptions.VinfraError(
                "Image status waiting failed (status={})".format(status))
        return self.resource

    def get_info(self):
        return self.resource


class ImageCreateTask(base.ResourceTask):
    def __init__(self, api, data, checksum, **kwargs):
        super(ImageCreateTask, self).__init__(api, data, **kwargs)
        self.checksum = checksum

    def wait(self, timeout=None):
        image = super(ImageCreateTask, self).wait(timeout=timeout)
        if self.checksum:
            # refetch image because the backend only returns the image ID
            image_obj = self.api.compute.images.get(image.id)
            if self.checksum != image_obj.checksum:
                raise exceptions.VinfraError(
                    "Checksum verification failed: the expected "
                    "checksum is {}, the actual checksum is {}"
                    .format(self.checksum, image_obj.checksum))
        return image


class Image(base.Resource):
    def __init__(self, manager, info):
        if 'visibility' in info:
            info['public'] = info.pop('visibility') == 'public'
        if 'traits' in info:
            info['placements'] = info.pop('traits')
        super(Image, self).__init__(manager, info)

    def delete(self):
        return self.manager.delete(self)

    def update(self, **params):
        return self.manager.update(self, **params)

    def download(self, fdst):
        return self.manager.download(self, fdst)


class ImageManager(Manager):
    resource_class = Image
    base_url = "/compute/images"

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, image):
        image_id = base.get_id(image)
        return self._get("{}/{}".format(self.base_url, image_id))

    def create_async(self, stream, name, disk_format, container_format,
                     min_disk=None, min_ram=None, os_distro=None,
                     protected=None, visibility=None, tags=None,
                     verify=False, hw_firmware_type=None):
        if not hasattr(stream, 'read'):
            # Looks like disk_data is not stream. Make stream.
            stream = open(stream, 'rb')

        checksum = None
        if verify:
            hash_md5 = hashlib.md5()  # nosec
            for chunk in iter(lambda: stream.read(4096), b""):
                hash_md5.update(chunk)
            checksum = hash_md5.hexdigest()
            stream.seek(0)

        params = dict(
            name=str(base64.b64encode(name.encode('utf-8')).decode('utf-8')),
            container_format=container_format,
            disk_format=disk_format,
        )
        params.update(flatten_args(
            min_disk=min_disk,
            min_ram=min_ram,
            os_distro=os_distro,
            protected=protected,
            visibility=visibility,
            tags=(
                base64.b64encode(json.dumps(tags))
                if tags is not None else None
            ),
            hw_firmware_type=hw_firmware_type,
        ))

        headers = params_to_headers(**params)
        data = self.client.post(self.base_url, headers=headers, data=stream)
        return ImageCreateTask(self, data, checksum=checksum)

    @base.async_wait
    def create(self, *args, **kwargs):
        return self.create_async(*args, **kwargs)

    def delete(self, image):
        image_id = base.get_id(image)
        return self._delete("{}/{}".format(self.base_url, image_id))

    def update(self, image, name=None, min_disk=None, min_ram=None,
               os_distro=None, protected=None, visibility=None):
        image_id = base.get_id(image)
        json = flatten_args(
            name=name,
            min_disk=min_disk,
            min_ram=min_ram,
            os_distro=os_distro,
            protected=protected,
            visibility=visibility,
        )
        return self._patch("{}/{}".format(self.base_url, image_id), json)

    def download(self, image, fdst):
        image_id = base.get_id(image)
        resp = self.client.send_request_raw(
            "get",
            "{}/{}/file".format(self.base_url, image_id),
            stream=True
        )

        close_fd = None
        if not hasattr(fdst, 'write'):
            # Looks like fdst is not stream. Make stream.
            if not isinstance(fdst, basestring):
                raise ValueError("fdst must be filepath or file-like object, "
                                 "got {}".format(fdst.__class__.__name__))
            if os.path.exists(fdst):
                raise ValueError("File exists: {}".format(fdst))
            fdst = open(fdst, 'wb')
            close_fd = fdst

        len_expected = int(resp.headers['Content-Length'])
        md5_expected = resp.headers['Content-Md5']

        md5ob = md5()
        while True:
            buf = resp.raw.read(16 * 1024)
            if not buf:
                break
            fdst.write(buf)
            md5ob.update(buf)

        if fdst.tell() != len_expected:
            msg = 'File length mismatch (epxect {}, got {})'.format(
                len_expected, fdst.tell())
            raise exceptions.VinfraError(msg)

        if md5_expected != md5ob.hexdigest():
            msg = 'Md5 sum mismatch: expected={}, gotten{}'.format(
                md5ob.hexdigest(), md5_expected)
            raise exceptions.VinfraError(msg)

        if close_fd:
            close_fd.close()

    @staticmethod
    def make_upload_task(resource):
        return ImageUploadTask(resource)
