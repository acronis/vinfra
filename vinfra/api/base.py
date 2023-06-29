import copy
import logging
import re
import time

from vinfra import compat, exceptions

LOG = logging.getLogger(__name__)
CAMELCASE_REGEX = re.compile(r'[A-Z](?:[a-z0-9]+|[A-Z]*(?=[A-Z]|$))')


def get_id(resource):
    try:
        return getattr(resource, resource.ID_ATTR)
    except AttributeError:
        return resource


def async_wait(func):
    def wrapper(*args, **kwargs):
        timeout = kwargs.pop('timeout', None)
        task = func(*args, **kwargs)
        return task.wait(timeout=timeout)

    return wrapper


class Task(object):
    default_timeout = 600  # default timeout in seconds

    def wait(self, timeout=None):
        raise NotImplementedError

    @staticmethod
    def get_info():
        return None


class PollTask(Task):
    poll_interval = 1  # default poll interval: 1 sec

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        result = None
        stime = time.time()
        while time.time() - stime < timeout:
            result = self.poll()
            if result is not None:
                return result
            time.sleep(self.poll_interval)
            continue

        raise exceptions.PollTimeoutError(
            "Task waiting exceeded {} second(s) timeout".format(timeout), result)

    def poll(self):
        raise NotImplementedError


class BackendTask(Task):
    def __init__(self, api, data, **kwargs):
        super(BackendTask, self).__init__()
        self.api = api
        self.data = data
        self.kwargs = kwargs

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        task_id = self.data['task_id']
        task = self.api.tasks.wait(task_id, timeout=timeout, **self.kwargs)
        return task.result

    def get_info(self):
        return self.data

    # Note(akurbatov): Do not use poll method: it's deprecated and used only
    # in DCO scripts.
    def poll(self):
        LOG.warning("BackendTask.poll is deprecated and will be removed in "
                    "further releases")
        return self.wait()


class ResourceTask(BackendTask):
    def __init__(self, resource_manager, data, **kwargs):
        super(ResourceTask, self).__init__(resource_manager.api, data,
                                           **kwargs)
        self.resource_manager = resource_manager

    def wait(self, timeout=None):
        data = super(ResourceTask, self).wait(timeout=timeout)
        return self.resource_manager.create_resource(data)


class StatusTask(PollTask):
    status = None

    def __init__(self, manager, resource):
        super(StatusTask, self).__init__()
        self.manager = manager
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(StatusTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Resource (id={}) status {!r} waiting exceeded {} second(s) "
                   "timeout (status={})".format(get_id(self.resource),
                                                self.status, timeout,
                                                self.resource.status))
            raise exceptions.TimeoutError(msg)
        return resource

    def poll(self):
        self.resource = self.manager.get(self.resource)
        if self.resource.status == self.status:
            return self.resource
        if self.resource.status.lower().startswith('error'):
            raise exceptions.VinfraError(
                'Resource "{}" has ERROR status.'
                .format(self.resource.name.encode('utf8')))
        return None

    def get_info(self):
        return self.resource


class DeleteTask(PollTask):
    def __init__(self, manager, resource):
        super(DeleteTask, self).__init__()
        self.manager = manager
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(DeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Resource (id={}) delete waiting exceeded {} second(s) "
                   "timeout".format(get_id(self.resource), timeout))
            raise exceptions.TimeoutError(msg)
        return None

    def poll(self):
        ids = [get_id(s) for s in self.manager.list()]
        if get_id(self.resource) not in ids:
            return {}
        return None

    def get_info(self):
        return None


class ChainedTask(Task):
    def __init__(self, resource, *tasks):
        self._tasks = tasks
        self._resource = resource
        self._task_results = []

    def wait(self, timeout=None):
        stime = time.time()
        timeout = timeout or self.default_timeout
        remained_timeout = timeout
        for task in self._tasks:
            res = task.wait(timeout=remained_timeout)
            self._task_results.append(res)
            remained_timeout = timeout - (time.time() - stime)

        return self._resource

    def get_info(self):
        return self._resource

    @property
    def task_results(self):
        return self._task_results


class VinfraApi(object):
    def __init__(self, api):
        self.api = api

    @property
    def client(self):
        return self.api.client


class Resource(object):
    ID_ATTR = 'id'
    NAME_ATTR = 'name'

    def __init__(self, manager, info):
        self.manager = manager
        self._info = info
        self.set_info(info)

    def __repr__(self):
        attrs = ", ".join("%s=%s" % (k, self._info[k])
                          for k in sorted(self._info.keys()))
        return "<{} {}>".format(self.__class__.__name__, attrs)

    @classmethod
    def get_display_name(cls):
        return ' '.join(re.findall(CAMELCASE_REGEX, cls.__name__)).lower()

    def set_info(self, info):
        if not info:
            return

        for k, v in info.items():
            setattr(self, k, v)
            self._info[k] = v

    def _update_info(self, info):
        for k in self._info:
            delattr(self, k)
        self.set_info(info)

    def get(self):
        new = self.manager.get(getattr(self, self.ID_ATTR))
        self._update_info(new.to_dict())
        return self

    def to_dict(self):
        return copy.deepcopy(self._info)


class Manager(VinfraApi):
    resource_class = Resource

    def create_resource(self, data):
        return self.resource_class(self, data)

    @staticmethod
    def _format_sort_param(sort):
        if isinstance(sort, (str, compat.basestring)):
            sort = [sort]

        sort_array = []
        for sort_item in sort:
            if isinstance(sort_item, tuple):
                sort_key = sort_item[0]
                sort_dir = sort_item[1]
            else:
                sort_key, _sep, sort_dir = sort_item.partition(':')
            sort_key = sort_key.strip()
            if sort_dir:
                sort_dir = sort_dir.strip()
                if sort_dir not in ('asc', 'desc'):
                    raise ValueError("sort_dir must be 'asc' or 'desc'.")
                sort_array.append('%s:%s' % (sort_key, sort_dir))
            else:
                sort_array.append(sort_key)
        return ','.join(sort_array)

    def _list(self, url, limit=None, marker=None, filters=None, sort=None,
              **kwargs):
        data = []
        query_params = {}
        if filters:
            query_params.update(filters)

        if sort:
            query_params['sort'] = self._format_sort_param(sort)

        while True:
            if marker:
                query_params['marker'] = marker

            if limit and limit != -1:
                query_params['limit'] = limit

            iter_data = self.client.get(url, query_params=query_params, **kwargs)
            if isinstance(iter_data, dict):
                iter_data = iter_data.get("data")
            data.extend(iter_data)

            if not iter_data or limit != -1:
                break

            marker = data[-1].get(self.resource_class.ID_ATTR)
            if not marker:
                LOG.warning('Cannot find resource ID attribute.')
                break

        items = [self.resource_class(self, res) for res in data or []]
        return items

    def _get(self, url, **kwargs):
        data = self.client.get(url, **kwargs)
        return self.resource_class(self, data)

    def _post(self, url, json=None, **kwargs):
        data = self.client.post(url, json=json, **kwargs)
        return self.resource_class(self, data)

    def _put(self, url, json=None, **kwargs):
        data = self.client.put(url, json=json, **kwargs)
        return self.resource_class(self, data)

    def _patch(self, url, json=None, **kwargs):
        data = self.client.patch(url, json=json, **kwargs)
        return self.resource_class(self, data)

    def _delete(self, url, json=None):
        # NOTE(Anton.Kurbatov): looks like 'delete' always returns NO_CONTENT
        return self.client.delete(url, json=json)

    # async
    def _send_task(self, method, url, task_params=None, **kwargs):
        resp = self.client.send_request(method, url, **kwargs)

        task_params = task_params or {}
        task_params['request_id'] = resp.request_id
        return ResourceTask(self, resp.data, **task_params)

    def _post_async(self, url, **kwargs):
        return self._send_task('post', url, **kwargs)

    def _put_async(self, url, **kwargs):
        return self._send_task('put', url, **kwargs)

    def _patch_async(self, url, **kwargs):
        return self._send_task('patch', url, **kwargs)

    def _delete_async(self, url, **kwargs):
        # NOTE(Anton.Kurbatov): looks like 'delete' always returns NO_CONTENT
        return self.client.delete_async(url, **kwargs)
