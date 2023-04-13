import os
from vinfra.client import ApiV2, ApiV3

__all__ = ['api_version', 'available_failure_domains']


def use_new_api():
    return not os.environ.get("VINFRA_USE_FAILURE_DOMAIN_API_V2")


def api_version(client):
    return ApiV3(client) if use_new_api() else ApiV2(client)


def available_failure_domains():
    return ['0', '1', '2', '3', '4'] if use_new_api() else ['disk', 'host', 'rack', 'row', 'room']
