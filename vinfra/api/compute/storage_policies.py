from vinfra import api_versions
from vinfra import exceptions
from vinfra.api import base
from vinfra.client import ApiV3
from vinfra.utils import flatten_args

_hidden = object()


def get_api_redundancy(redundancy):
    if redundancy is None:
        return redundancy

    if isinstance(redundancy, Redundancy):
        return redundancy.to_api_dict()

    if not isinstance(redundancy, dict):
        raise TypeError('expecting dict object')

    return redundancy


def get_vinfra_redundancy(redundancy):
    if isinstance(redundancy, Redundancy):
        return redundancy

    if not isinstance(redundancy, dict):
        raise TypeError('expecting dict object')

    rtype = redundancy['type']
    m = redundancy.get('m', _hidden)
    n = redundancy.get('n')
    if rtype == 'raid1':
        return Replicas(m, minimum=n)
    elif rtype == 'raid6':
        return Encoding(m, n)

    raise exceptions.VinfraError(
        "Unsupported redundancy type '{}'".format(rtype))


# pylint: disable=invalid-name
def convert_vinfra_to_api_redundancy(redundancy):
    if isinstance(redundancy, Redundancy):
        return redundancy.to_api_dict()

    if not isinstance(redundancy, dict):
        raise TypeError('expecting dict object')

    rtype = redundancy['type']
    rparams = redundancy['params'] or {}
    if rtype == 'replicas':
        rv = Replicas(
            rparams.get('norm'),
            minimum=rparams.get('min')
        )
    elif rtype == 'encoding':
        rv = Encoding(
            rparams.get('M'),
            rparams.get('N')
        )
    else:
        raise exceptions.VinfraError(
            "Unsupported redundancy type '{}'".format(rtype))

    return rv.to_api_dict()


class Redundancy(object):
    def to_dict(self):
        raise NotImplementedError

    def to_api_dict(self):
        raise NotImplementedError


class Replicas(Redundancy):
    def __init__(self, norm, minimum=None):
        self.norm = norm
        self.minimum = minimum

    def to_dict(self):
        rv = {'type': 'replicas', 'params': None}
        if self.norm != _hidden:
            rv['params'] = {
                'norm': self.norm,
                'min': self.minimum
            }
        return rv

    def to_api_dict(self):
        if self.norm is _hidden:
            raise exceptions.VinfraError('Cannot convert to API dict')
        # Native API confuses usual meaning for replicas:
        # m -> normal, n -> minimum
        rdict = {'type': 'raid1', 'm': self.norm}
        if self.minimum is not None:
            rdict['n'] = self.minimum
        return rdict


class Encoding(Redundancy):
    def __init__(self, data_blocks, parity_blocks):
        self.data_blocks = data_blocks
        self.parity_blocks = parity_blocks

    def to_dict(self):
        rv = {'type': 'encoding', 'params': None}
        if self.data_blocks != _hidden:
            rv['params'] = {
                'M': self.data_blocks,
                'N': self.parity_blocks,
            }
        return rv

    def to_api_dict(self):
        if self.data_blocks is _hidden:
            raise exceptions.VinfraError('Cannot convert to API dict')
        return {
            'type': 'raid6',
            'm': self.data_blocks,
            'n': self.parity_blocks,
        }


class StoragePolicy(base.Resource):
    def __init__(self, manager, info):
        # info['redundancy'] can be None, cinder extra_specs available only for
        # admin, another user have None (need to fix kolla ansible spec)
        if info['redundancy'] is not None:
            redundancy = get_vinfra_redundancy(info['redundancy'])
            info['redundancy'] = redundancy.to_dict()
        super(StoragePolicy, self).__init__(manager, info)

    def update(self, *args, **params):
        return self.manager.update(self, *args, **params)

    def delete(self):
        return self.manager.delete(self)


class StoragePolicyManager(base.Manager):
    resource_class = StoragePolicy
    base_url = "/storage_policies"

    def list(self):
        if self.api.api_version < api_versions.HCI_VER_40:
            return self._list(self.base_url)
        with ApiV3(self.api.client):
            return self._list(self.base_url)

    def get(self, storage_policy):
        storage_policy_id = base.get_id(storage_policy)

        if self.api.api_version < api_versions.HCI_VER_40:
            return self._get("{}/{}".format(self.base_url, storage_policy_id))
        with ApiV3(self.api.client):
            return self._get("{}/{}".format(self.base_url, storage_policy_id))

    def create(self, name, tier, redundancy, failure_domain, qos=None,
               storage=None, params=None):
        redundancy = get_api_redundancy(redundancy)
        data = {
            'name': name,
            'tier': tier,
            'redundancy': redundancy,
            'failure_domain': failure_domain,
        }
        data = flatten_args(**data)

        if qos:
            data['qos'] = qos
        if storage:
            data['storage'] = storage
        if params:
            data['params'] = params

        if self.api.api_version < api_versions.HCI_VER_40:
            return self._post(self.base_url, json=data)
        with ApiV3(self.api.client):
            return self._post(self.base_url, json=data)

    def update(self, storage_policy, name, tier, redundancy, failure_domain, qos=None,
               storage=None, params=None):
        if redundancy:
            redundancy = convert_vinfra_to_api_redundancy(redundancy)
        data = {
            'name': name,
            'tier': tier,
            'redundancy': redundancy,
            'failure_domain': failure_domain,
        }
        data = flatten_args(**data)
        url = "{}/{}".format(self.base_url, base.get_id(storage_policy))

        if qos:
            data['qos'] = qos
        if storage:
            data['storage'] = storage
        if params:
            data['params'] = params

        if self.api.api_version < api_versions.HCI_VER_40:
            return self._patch(url, json=data)
        with ApiV3(self.api.client):
            return self._patch(url, json=data)

    def delete(self, storage_policy):
        storage_policy_id = base.get_id(storage_policy)
        return self._delete("{}/{}".format(self.base_url, storage_policy_id))
