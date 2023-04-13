import argparse
import logging
import collections
import getpass
import inspect
import json
import os
import re
import sys
import threading
import time
import uuid
import yaml

from vinfra.api.compute.flavors import FlavorManager
from vinfra.api.compute.nodes import NodeManager as ComputeNodeManager
from vinfra.api.domains import DomainManager
from vinfra.api.nodes import NodeManager
from vinfra.api.nodes.ifaces import InterfaceManager
from vinfra.api.settings import LocaleManager
from vinfraclient import compat
from vinfraclient import exceptions

LOG = logging.getLogger(__name__)
SYSTEM_TAG = 'hci.system'


def get_cluster(vinfra):
    clusters = vinfra.clusters.list()
    if not clusters:
        raise exceptions.CommandError("The cluster does not exist.")
    if len(clusters) > 1:
        raise exceptions.CommandError("More than one cluster exists.")
    return clusters.pop()


def is_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def flat_and_combine_arg_list(args_lst=None):
    """
    1. args_lst = [["a","b"],["c"],["d","e"]] -> ["a","b","c","d","e"]
    2. strip elements in list
    3. remove empty entries
    """
    if args_lst is None:
        return None
    ret = list()
    for entry in args_lst:
        ret += entry
    ret = [entry.strip() for entry in ret]
    ret = [entry for entry in ret if entry]
    return ret


def find_resource(manager, name_or_id, **kwargs):
    # get resource if it looks like uuid
    if is_uuid(name_or_id):
        try:
            return manager.get(name_or_id)
        except Exception:  # pylint: disable=broad-except
            pass

    # flavors ID can be int
    if isinstance(manager, FlavorManager):
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            try:
                return manager.get(int(name_or_id))
            except Exception:  # pylint: disable=broad-except
                pass

    # resources witch have a common string as ID:
    if isinstance(manager, (InterfaceManager, LocaleManager)):
        try:
            return manager.get(name_or_id)
        except Exception:  # pylint: disable=broad-except
            pass

    # There is only one domain with string ID - 'default' domain.
    # Handle it separately:
    if isinstance(manager, DomainManager) and name_or_id == 'default':
        try:
            return manager.get(name_or_id)
        except Exception:  # pylint: disable=broad-except
            pass

    resource_name = name_or_id
    # add 'vstoragedomain' suffix to node
    if (isinstance(manager, (ComputeNodeManager, NodeManager)) and
            not name_or_id.endswith('vstoragedomain')):
        resource_name += '.vstoragedomain'

    try:
        list_func_args = inspect.getargspec(manager.list).args
    except TypeError:
        list_func_args = []

    if 'filters' in list_func_args:
        kwargs.setdefault('filters', {
            manager.resource_class.NAME_ATTR: resource_name})
    if 'limit' in list_func_args:
        kwargs['limit'] = -1

    count = 0
    _resource = None
    for resource in manager.list(**kwargs):
        rname = getattr(resource, resource.NAME_ATTR, None)
        rid = getattr(resource, resource.ID_ATTR, None)
        if rname == resource_name or rid == resource_name:
            count += 1
            _resource = resource

    if count == 0:
        msg = "No {} with a {} or ID of '{}' exists.".format(
            manager.resource_class.get_display_name(),
            manager.resource_class.NAME_ATTR,
            name_or_id)
        raise exceptions.CommandError(msg)
    if count > 1:
        msg = "More than one {} exists with the {} '{}'.".format(
            manager.resource_class.get_display_name(),
            manager.resource_class.NAME_ATTR,
            name_or_id)
        raise exceptions.CommandError(msg)
    return _resource


def find_resources(manager, names_or_ids, **kwargs):
    if 'filters' in inspect.getargspec(manager.list).args:
        # Use 'find_resource' for each resource in the list
        resources = []
        for name_or_id in names_or_ids:
            resources.append(find_resource(manager, name_or_id))
        return resources

    # manager doesn't support filtering: list all resources and find matches
    if 'limit' in inspect.getargspec(manager.list).args:
        kwargs['limit'] = -1
    resources = manager.list(**kwargs)
    resources_by_id = collections.defaultdict(list)
    resources_by_name = collections.defaultdict(list)

    for resource in resources:
        resource_id = getattr(resource, resource.ID_ATTR, None)
        resources_by_id[resource_id].append(resource)

        resource_name = getattr(resource, resource.NAME_ATTR, None)
        resources_by_name[resource_name].append(resource)

    result = []
    for name_or_id in names_or_ids:
        if (not is_uuid(name_or_id) and
                isinstance(manager, (ComputeNodeManager, NodeManager)) and
                not name_or_id.endswith('vstoragedomain')):
            name_or_id += '.vstoragedomain'

        _resources = []
        _resources.extend(resources_by_id[name_or_id])
        _resources.extend(resources_by_name[name_or_id])

        if not _resources:
            msg = "No {} with a name or ID of '{}' exists.".format(
                manager.resource_class.get_display_name(), name_or_id)
            raise exceptions.CommandError(msg)

        if len(_resources) > 1:
            msg = "More than one {} exists with the name or ID '{}'.".format(
                manager.resource_class.get_display_name(), name_or_id)
            raise exceptions.CommandError(msg)

        result.append(_resources[0])

    return result


def ask_confirm(message=None):
    if not sys.stdin.isatty():
        return True
    if not message:
        message = 'Are you sure you want to confirm the action? [y/N]'
    LOG.info(message)
    prompt_response = sys.stdin.readline().strip()
    if prompt_response.lower().startswith('y'):
        return True
    return False


def get_password(prompt="Password: "):
    if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
        try:
            password = getpass.getpass(prompt=prompt)
        except (EOFError, IOError) as err:
            raise exceptions.ValidationError(
                'Failed to get the password from stdin: %s' % err)
    else:
        password = sys.stdin.readline().rstrip()

    if not password:
        raise exceptions.ValidationError('No password was entered.')

    return password


def get_stream(file_name):
    try:
        return open(file_name, mode='rb')
    except Exception as err:
        raise exceptions.ValidationError(
            'Failed to open "{}" ({}).'.format(file_name, err))


def get_yaml(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError('%s does not exist' % path)

    with open(path, 'r') as fp:
        try:
            data = yaml.safe_load(fp)
        except yaml.YAMLError as ex:
            raise argparse.ArgumentTypeError('Cannot parse YAML: %s' % ex)

    return data


def get_json(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError('%s does not exist' % path)

    with open(path, 'r') as fp:
        try:
            data = json.load(fp)
        except compat.JSONDecodeError as ex:
            raise argparse.ArgumentTypeError('Invalid data format: %s' % ex)

    return data


def progress_bar_context(app, pbar, timeout=None):
    if app.stderr.isatty() and app.options.verbose_level:
        return ProgressBarProcess(pbar, timeout=timeout)

    return FakeProgressBarProcess()


_MULTIPLIER = {
    "KiB": 1024,
    "MiB": 1024 ** 2,
    "GiB": 1024 ** 3,
    "TiB": 1024 ** 4,
    "PiB": 1024 ** 5
}
SIZE_PATTERN = re.compile(r'^(\d+)({})?$'.format('|'.join(_MULTIPLIER.keys())))


def get_size_in_bytes(input_value):
    """Returns an integer value that is equal to the
    amount of bytes that value defines as a string in
    a human-readable manner using IEC standard multipliers.

    Examples
    --------
    >>> get_size_in_bytes('10')
    10
    >>> get_size_in_bytes('256GiB')
    274877906944L"""

    if not isinstance(input_value, str):
        raise ValueError("{} cannot be converted".format(type(input_value)))

    m = SIZE_PATTERN.match(input_value.strip())
    if not m:
        raise ValueError("literal '{}' cannot be converted".format(input_value))
    val = int(m.group(1))
    mul = _MULTIPLIER.get(m.group(2), 1)
    return val * mul


class SizeValue(object):
    _mapping = {
        1: ['', 'b'],
        1000: ['kb'],
        1 << 10: ['k', 'kib'],
        1000**2: ['mb'],
        1 << 20: ['m', 'mib'],
        1000**3: ['gb'],
        1 << 30: ['g', 'gib'],
        1000**4: ['tb'],
        1 << 40: ['t', 'tib'],
        1000**5: ['pb'],
        1 << 50: ['p', 'pib'],
        1000**6: ['eb'],
        1 << 60: ['e', 'eib'],
    }

    def __init__(self, size):
        self.value = None
        if isinstance(size, (int, long, float)):
            self.value = size
        elif isinstance(size, (str, basestring)):
            for mul, suffix_list in self._mapping.items():
                for suffix in suffix_list:
                    m = re.search(r'^(\d+)%s$' % suffix, size.lower())
                    if m:
                        self.value = int(m.group(1)) * mul
                        break
                if self.value:
                    break
        if self.value is None:
            raise ValueError('Wrong size value: %s %s' % (size, type(size)))

    def humanize(self, suffix='B'):
        #if self.value == 0:
        #    return '0'

        num = self.value
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Ei', suffix)


class FakeProgressBarProcess(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class ProgressBarProcess(object):
    def __init__(self, pbar, timeout=None):
        self.pbar = pbar
        self.timeout = timeout
        self.running = None
        self.proc = None

    def run(self):
        val = 0
        stime = time.time()
        self.pbar.start()
        while self.running:
            time.sleep(0.2)
            if self.timeout:
                elapsed = time.time() - stime
                if elapsed > self.timeout:
                    break
            val += 1
            if val > self.pbar.maxval:
                val = 0
            self.pbar.update(val)
        self.pbar.finish()

    def __enter__(self):
        self.running = True
        self.proc = threading.Thread(target=self.run)
        self.proc.setDaemon(True)
        self.proc.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.running = False
        self.proc.join()


def join_options(options_list, unset_options=None):
    rv = {
        k: None
        for k in unset_options or []
    }

    rv.update({
        k: v or None
        for options in (options_list or [])
        for k, v in options.items()})

    return rv or None

def validate_resources_from_operator(manager, value):
    resources = []
    op = ''
    if ':' in value:
        op, vals = value.split(':', 1)
        op += ':'
        resources = vals.split(',')
    else:
        resources = [value]

    resources = find_resources(manager, resources)
    return '{}{}'.format(op, ','.join([r.id for r in resources]))
