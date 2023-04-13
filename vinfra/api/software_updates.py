from vinfra.api import base
from vinfra.api_versions import APIVersion
from vinfra.client import ApiV3
from vinfra.utils import flatten_args


V3_BACKEND_VERSION = APIVersion('6.0.19')
V3_MAINTENANCE_BACKEND_VERSION = APIVersion('6.1.17')
V3_CONTROL_PLANE_BACKEND_VERSION = APIVersion('7.0.50')


def maintenance_to_mode(maintenance):
    if not maintenance['enabled']:
        return 'no_maintenance'
    elif maintenance['on_fail'] == 'force':
        return 'force'
    elif maintenance['on_fail'] == 'skip':
        return 'skip'
    return 'stop'


class SoftwareUpdatesManager(object):

    def __init__(self, api):
        self.api = api

    def get(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.get('/software_updates')
        else:
            return self.api.client.get('/software_updates')

    def start_async(self, req):
        params = {
            'accept_eula': req.get('accept_eula', False)
        }
        if self.api.backend_version >= V3_CONTROL_PLANE_BACKEND_VERSION:
            nodes = req.get('nodes')
            if nodes is not None:
                params['nodes'] = [base.get_id(v) for v in nodes]
                params['control_plane'] = False
            else:
                params['control_plane'] = not req['skip_control_plane']
        elif self.api.backend_version >= V3_BACKEND_VERSION:
            nodes = req.get('nodes')
            if nodes is not None:
                params['nodes'] = [base.get_id(v) for v in nodes]
                params['services'] = {
                    'compute': {
                        'update': not nodes,
                    },
                }

        maintenance = req['maintenance']
        if self.api.backend_version >= V3_MAINTENANCE_BACKEND_VERSION:
            params['maintenance'] = {
                'enabled': maintenance['enabled']
            }
            if maintenance['enabled']:
                params['maintenance']['params'] = {
                    'on_fail': maintenance['on_fail'],
                    'compute': {
                        'mode': maintenance['compute_mode'],
                    }
                }
        else:
            params['mode'] = maintenance_to_mode(maintenance)

        data = flatten_args(**params)
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/start', json=data)
        else:
            return self.api.client.post_async('/software_updates/start', json=data)

    @base.async_wait
    def start(self, **kwargs):
        return self.start_async(**kwargs)

    def resume_async(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/resume')
        else:
            return self.api.client.post_async('/software_updates/resume')

    @base.async_wait
    def resume(self):
        return self.resume_async()

    def check_for_update_async(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/check_for_update')
        else:
            return self.api.client.post_async('/software_updates/check_for_update')

    @base.async_wait
    def check_for_update(self):
        return self.check_for_update_async()

    def download_async(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/download')
        else:
            return self.api.client.post_async('/software_updates/download')

    @base.async_wait
    def download(self):
        return self.download_async()

    def eligibility_check_async(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/eligibility_check')
        else:
            return self.api.client.post_async('/software_updates/eligibility_check')

    @base.async_wait
    def eligibility_check(self):
        return self.eligibility_check_async()

    def pause_async(self):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            with ApiV3(self.api.client):
                return self.api.client.post_async('/software_updates/pause')
        else:
            return self.api.client.post_async('/software_updates/pause')

    @base.async_wait
    def pause(self):
        return self.pause_async()

    def cancel_async(self, maintenance_mode):
        if self.api.backend_version >= V3_BACKEND_VERSION:
            params = {
                'maintenance_mode': maintenance_mode,
            }
            data = flatten_args(**params)
            with ApiV3(self.api.client):
                return self.api.client.delete_async('/software_updates/start', json=data)
        else:
            return self.api.client.delete_async('/software_updates/start')

    @base.async_wait
    def cancel(self, **kwargs):
        return self.cancel_async(**kwargs)
