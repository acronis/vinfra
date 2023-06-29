import time

from vinfra import api_versions
from vinfra import exceptions
from vinfra.api import base
from vinfra.api.compute.base import Manager


class StartTask(base.StatusTask):
    status = 'ACTIVE'


class CreateTask(base.StatusTask):
    status = 'ACTIVE'


class StopTask(base.StatusTask):
    status = 'SHUTOFF'


class RebootTask(base.StatusTask):
    status = 'ACTIVE'


class PauseTask(base.StatusTask):
    status = 'PAUSED'


class UnpauseTask(base.StatusTask):
    status = 'ACTIVE'


class SuspendTask(base.StatusTask):
    status = 'SUSPENDED'


class ResumeTask(base.StatusTask):
    status = 'ACTIVE'


class ShelveTask(base.StatusTask):
    status = 'SHELVED_OFFLOADED'


class UnshelveTask(base.StatusTask):
    status = 'ACTIVE'


class RescueTask(base.StatusTask):
    status = 'RESCUE'


class UnrescueTask(base.StatusTask):
    status = 'ACTIVE'


class EvacuateTask(base.PollTask):
    def __init__(self, manager, resource):
        super(EvacuateTask, self).__init__()
        self.manager = manager
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(EvacuateTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            raise exceptions.TimeoutError(
                "Evacuation task wait timed out. Expected server status "
                "ACTIVE or SHUTOFF, got {}".format(self.resource.status))
        return resource

    def poll(self):
        self.resource = self.manager.get(self.resource)
        if not self.resource.task_state:
            if self.resource.status in ['ACTIVE', 'SHUTOFF']:
                return self.resource

            if self.resource.status == 'ERROR':
                raise exceptions.VinfraError(
                    'Resource "{}" has ERROR status.'
                    .format(self.resource.name.encode('utf8')))
        return None

    def get_info(self):
        return self.resource


class ResetStateTask(base.StatusTask):
    def __init__(self, manager, resource, state=None):
        super(ResetStateTask, self).__init__(manager, resource)

        self.status = 'ACTIVE' if state is None else state

    def poll(self):
        self.resource = self.manager.get(self.resource)
        ready = (self.status == 'ERROR') == (self.resource.status == 'ERROR')
        return self.resource if ready else None


class ResizeTask(base.PollTask):
    def __init__(self, manager, resource):
        super(ResizeTask, self).__init__()
        self.manager = manager
        self.resource = resource

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            resource = super(ResizeTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            raise exceptions.TimeoutError(
                "Resize task wait timed out. Expected server status is "
                "ACTIVE or SHUTOFF, got {}".format(self.resource.status))
        return resource

    def poll(self):
        self.resource = self.manager.get(self.resource)
        if not self.resource.task_state:
            if self.resource.status in ['ACTIVE', 'SHUTOFF']:
                return self.resource

            if self.resource.status == 'ERROR':
                raise exceptions.VinfraError(
                    'Resource "{}" has ERROR status.'
                    .format(self.resource.name.encode('utf8')))
        return None


class DeleteTask(base.PollTask):
    def __init__(self, manager, server):
        self.manager = manager
        self.server = server
        self.initial_status = server.status
        self._error_found = False

    def wait(self, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            super(DeleteTask, self).wait(timeout=timeout)
        except exceptions.TimeoutError:
            msg = ("Server (id={}) delete waiting exceeded {} second(s) "
                   "timeout".format(base.get_id(self.server), timeout))
            raise exceptions.TimeoutError(msg)
        return None

    def poll(self):
        servers_by_id = {srv.id: srv for srv in self.manager.list()}
        server = servers_by_id.get(self.server.id)
        if not server:
            return {}
        elif server.status == 'ERROR' and self.initial_status != 'ERROR':
            if not self._error_found:
                self._error_found = True
                time.sleep(10)
            else:
                raise exceptions.VinfraError(
                    'Server {} has ERROR status.'.format(self.server.id))
        return None

    def get_info(self):
        return None


class Server(base.Resource):
    def __init__(self, manager, info):
        info['placements'] = info.pop('traits')
        super(Server, self).__init__(manager, info)
        self.networks_manager = ServerNetworkManager(manager.api, self)
        self.volumes_manager = ServerVolumeManager(manager.api, self)
        self.metadata_manager = ServerMetadataManager(manager.api, self)
        self.events_manager = ServerEventManager(manager.api, self)

    def start_async(self):
        return self.manager.start_async(self)

    def start(self, *args, **kwargs):
        return self.manager.start(self, *args, **kwargs)

    def stop_async(self, hard=None, timeout=None):
        return self.manager.stop_async(self, hard=hard, timeout=timeout)

    def stop(self, *args, **kwargs):
        return self.manager.stop(self, *args, **kwargs)

    def cancel_stop(self, *args, **kwargs):
        return self.manager.cancel_stop(self, *args, **kwargs)

    def reboot_async(self, hard=None):
        return self.manager.reboot_async(self, hard=hard)

    def reboot(self, *args, **kwargs):
        return self.manager.reboot(self, *args, **kwargs)

    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self, *args, **kwargs):
        return self.manager.delete(self, *args, **kwargs)

    def pause_async(self):
        return self.manager.pause_async(self)

    def pause(self, *args, **kwargs):
        return self.manager.pause(self, *args, **kwargs)

    def unpause_async(self):
        return self.manager.unpause_async(self)

    def unpause(self, *args, **kwargs):
        return self.manager.unpause(self, *args, **kwargs)

    def suspend_async(self):
        return self.manager.suspend_async(self)

    def suspend(self, *args, **kwargs):
        return self.manager.suspend(self, *args, **kwargs)

    def resume_async(self):
        return self.manager.resume_async(self)

    def resume(self, *args, **kwargs):
        return self.manager.resume(self, *args, **kwargs)

    def resize_async(self, flavor):
        return self.manager.resize_async(self, flavor)

    def resize(self, *args, **kwargs):
        return self.manager.resize(self, *args, **kwargs)

    def console(self):
        return self.manager.console(self)

    def stat(self):
        return self.manager.stat(self)

    def log(self):
        return self.manager.log(self)

    def reset_state_async(self, state=None):
        return self.manager.reset_state_async(self, state=state)

    def reset_state(self, *args, **kwargs):
        return self.manager.reset_state(self, *args, **kwargs)

    def migrate(self, **kwargs):
        return self.manager.migrate(self, **kwargs)

    def evacuate_async(self):
        return self.manager.evacuate_async(self)

    def evacuate(self):
        return self.manager.evacuate(self)

    def shelve_async(self):
        return self.manager.shelve_async(self)

    def shelve(self, *args, **kwargs):
        return self.manager.shelve(self, *args, **kwargs)

    def unshelve_async(self):
        return self.manager.unshelve_async(self)

    def unshelve(self, *args, **kwargs):
        return self.manager.unshelve(self, *args, **kwargs)

    def update(self, **kwargs):
        return self.manager.update(self, **kwargs)

    def rescue_async(self, *args, **kwargs):
        return self.manager.rescue_async(self, *args, **kwargs)

    def rescue(self, *args, **kwargs):
        return self.manager.rescue(self, *args, **kwargs)

    def unrescue_async(self, *args):
        return self.manager.unrescue_async(self, *args)

    def unrescue(self, *args):
        return self.manager.unrescue(self, *args)

    def add_tag(self, *args):
        return self.manager.add_tag(self, *args)

    def delete_tag(self, *args):
        return self.manager.delete_tag(self, *args)

    def list_tags(self):
        return self.manager.list_tags(self)

    def set_password(self, *args):
        return self.manager.set_password(self, *args)


class ServerManager(Manager):
    resource_class = Server
    base_url = "/compute/servers"

    def _action(self, server, action, **kwargs):
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        url = "{}/{}/{}".format(self.base_url, base.get_id(server), action)
        return self.client.post(url, json=data)

    def list(self, limit=None, marker=None, filters=None, sort=None):
        return self._list(self.base_url, limit=limit, marker=marker,
                          filters=filters, sort=sort)

    def get(self, server):
        server_id = base.get_id(server)
        return self._get("{}/{}".format(self.base_url, server_id))

    # pylint: disable=too-many-arguments
    def create_async(self, name, flavor, networks, volumes, description=None,
                     metadata=None, user_data=None, key_name=None,
                     config_drive=None, storage_policy=None, count=None,
                     ha_enabled=None, placements=None, allow_live_resize=None,
                     uefi=None):
        for net in networks:
            if ('fixed_ips' in net and
                    self.api.api_version < api_versions.HCI_VER_46):
                fixed_ips = net.pop('fixed_ips')
                net['fixed_ip'] = ServerNetworkManager.check_one_ip(fixed_ips)

        data = {
            'name': name,
            'flavor': flavor,
            'networks': networks,
            'volumes': volumes,
        }
        if description:
            data['description'] = description
        if metadata:
            data['metadata'] = metadata
        if user_data:
            data['user_data'] = user_data
        if key_name:
            data['key_name'] = key_name
        if config_drive:
            data['config_drive'] = config_drive
        if storage_policy:
            data['storage_policy'] = storage_policy
        if count:
            data['count'] = count
        if ha_enabled:
            data['ha_enabled'] = ha_enabled
        if placements:
            data['traits'] = placements
        if allow_live_resize:
            data['allow_live_resize'] = allow_live_resize
        if uefi:
            data['uefi'] = uefi
        server = self._post(self.base_url, json=data)
        return CreateTask(self, server)

    @base.async_wait
    def create(self, *args, **kwargs):
        return self.create_async(*args, **kwargs)

    def update(self, server, name=None, description=None, ha_enabled=None,
               traits=None, allow_live_resize=None):
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if ha_enabled:
            data['ha_enabled'] = ha_enabled
        if traits is not None:
            data['traits'] = [base.get_id(trait) for trait in traits]
        if allow_live_resize is not None:
            data['allow_live_resize'] = allow_live_resize

        url = "{}/{}".format(self.base_url, base.get_id(server))
        return self._patch(url, json=data)

    def delete_async(self, server):
        if not isinstance(server, Server):
            server = self.get(server)
        self._delete("{}/{}".format(self.base_url, server.id))
        return DeleteTask(self, server)

    @base.async_wait
    def delete(self, server):
        return self.delete_async(server)

    def start_async(self, server):
        self._action(server, "start")
        return StartTask(self, server)

    @base.async_wait
    def start(self, server):
        return self.start_async(server)

    def stop_async(self, server, hard=None, timeout=None):
        self._action(server, "stop", hard=hard, timeout=timeout)
        return StopTask(self, server)

    @base.async_wait
    def stop(self, server, hard=None, timeout=None):
        return self.stop_async(server, hard=hard, timeout=timeout)

    def cancel_stop(self, server):
        url = "{}/{}/cancel-stop".format(self.base_url, base.get_id(server))
        return self.client.post(url, json={})

    def reboot_async(self, server, hard=None):
        self._action(server, "reboot", hard=hard)
        return RebootTask(self, server)

    @base.async_wait
    def reboot(self, *args, **kwargs):
        return self.reboot_async(*args, **kwargs)

    def pause_async(self, server):
        self._action(server, "pause")
        return PauseTask(self, server)

    @base.async_wait
    def pause(self, *args, **kwargs):
        return self.pause_async(*args, **kwargs)

    def unpause_async(self, server):
        self._action(server, "unpause")
        return UnpauseTask(self, server)

    @base.async_wait
    def unpause(self, *args, **kwargs):
        return self.unpause_async(*args, **kwargs)

    def suspend_async(self, server):
        self._action(server, "suspend")
        return SuspendTask(self, server)

    @base.async_wait
    def suspend(self, *args, **kwargs):
        return self.suspend_async(*args, **kwargs)

    def resume_async(self, server):
        self._action(server, "resume")
        return ResumeTask(self, server)

    @base.async_wait
    def resume(self, *args, **kwargs):
        return self.resume_async(*args, **kwargs)

    def resize_async(self, server, flavor):
        self._action(server, "resize", flavor=flavor)
        return ResizeTask(self, server)

    @base.async_wait
    def resize(self, *args, **kwargs):
        return self.resize_async(*args, **kwargs)

    def console(self, server):
        url = "{}/{}/console".format(self.base_url, base.get_id(server))
        return self.client.get(url)

    def stat(self, server):
        url = "{}/{}/stat".format(self.base_url, base.get_id(server))
        return self.client.get(url)

    def log(self, server):
        url = "{}/{}/log".format(self.base_url, base.get_id(server))
        return self.client.get(url)

    def reset_state_async(self, server, state=None):
        self._action(server, "reset", state=state)
        return ResetStateTask(self, server, state=state)

    @base.async_wait
    def reset_state(self, *args, **kwargs):
        return self.reset_state_async(*args, **kwargs)

    def migrate(self, server, node=None, cold=None):
        data = {}
        if cold is not None:
            data['cold'] = cold
        if node:
            data['node_id'] = base.get_id(node)

        url = "{}/{}/migrate".format(self.base_url, base.get_id(server))
        return self.client.post(url, json=data)

    def evacuate_async(self, server):
        self._action(server, "evacuate")
        return EvacuateTask(self, server)

    @base.async_wait
    def evacuate(self, server):
        return self.evacuate_async(server)

    def shelve_async(self, server):
        self._action(server, "shelve")
        return ShelveTask(self, server)

    @base.async_wait
    def shelve(self, server):
        return self.shelve_async(server)

    def unshelve_async(self, server):
        self._action(server, "unshelve")
        return UnshelveTask(self, server)

    @base.async_wait
    def unshelve(self, server):
        return self.unshelve_async(server)

    def rescue_async(self, server, image=None):
        image_id = base.get_id(image) if image else None
        self._action(server, 'rescue', image_id=image_id)
        return RescueTask(self, server)

    @base.async_wait
    def rescue(self, server, image=None):
        return self.rescue_async(server, image=image)

    def unrescue_async(self, server):
        self._action(server, "unrescue")
        return UnrescueTask(self, server)

    @base.async_wait
    def unrescue(self, server):
        return self.unrescue_async(server)

    def add_tag(self, server, tag):
        url = "{}/{}/tags/{}".format(self.base_url, base.get_id(server), tag)
        return self.client.put(url)

    def delete_tag(self, server, tag):
        url = "{}/{}/tags/{}".format(self.base_url, base.get_id(server), tag)
        return self.client.delete(url)

    def list_tags(self, server):
        url = "{}/{}/tags".format(self.base_url, base.get_id(server))
        return self.client.get(url)['data']

    def set_password(self, server, password):
        url = "{}/{}/password_set".format(self.base_url, base.get_id(server))
        data = {'password': password}
        return self.client.post(url, json=data, log=False)

class ServerNetwork(base.Resource):
    pass


class ServerNetworkManager(Manager):
    resource_class = ServerNetwork

    def __init__(self, api, server):
        super(ServerNetworkManager, self).__init__(api)
        self.server_id = base.get_id(server)
        self.base_url = "/compute/servers/{}/interfaces".format(self.server_id)

    def list(self):
        return self._list(self.base_url)

    @staticmethod
    def check_one_ip(fixed_ips):
        if len(fixed_ips) > 1:
            raise exceptions.VinfraError('Only one IP address is supported.')
        return fixed_ips[0]

    def attach(self, network, fixed_ips=None, mac_addr=None,
               spoofing_protection=None, security_groups=None):
        data = {'network_id': base.get_id(network)}

        if fixed_ips is not None:
            if self.api.api_version < api_versions.HCI_VER_46:
                fixed_ips = data.pop('fixed_ips')
                data['fixed_ip'] = self.check_one_ip(fixed_ips)
            else:
                data['fixed_ips'] = fixed_ips
        if mac_addr is not None:
            data['mac_addr'] = mac_addr
        if spoofing_protection is not None:
            data['spoofing_protection'] = spoofing_protection
        if security_groups is not None:
            data['security_groups'] = security_groups

        return self._post(self.base_url, json=data)

    def detach(self, port_id):
        url = "{}/{}".format(self.base_url, base.get_id(port_id))
        return self._delete(url)

    def update(self, port_id, fixed_ips=None, mac_addr=None,
               spoofing_protection=None, security_groups=None):
        data = {}
        if fixed_ips is not None:
            if self.api.api_version < api_versions.HCI_VER_46:
                fixed_ips = data.pop('fixed_ips')
                data['fixed_ip'] = self.check_one_ip(fixed_ips)
            else:
                data['fixed_ips'] = fixed_ips
        if mac_addr is not None:
            data['mac_addr'] = mac_addr
        if spoofing_protection is not None:
            data['spoofing_protection'] = spoofing_protection
        if security_groups is not None:
            data['security_groups'] = security_groups
        url = "{}/{}".format(self.base_url, base.get_id(port_id))
        return self._patch(url, json=data)


class ServerVolume(base.Resource):
    pass


class ServerVolumeManager(Manager):
    resource_class = ServerVolume

    def __init__(self, api, server, force_detach=False):
        super(ServerVolumeManager, self).__init__(api)
        self.force_detach = force_detach
        self.server_id = server if self.force_detach else base.get_id(server)
        self.base_url = "/compute/servers/{}/volumes".format(self.server_id)

    def get(self, volume):
        volume_id = base.get_id(volume)
        return self._get("{}/{}".format(self.base_url, volume_id))

    def list(self):
        return self._list(self.base_url)

    def attach(self, volume):
        data = {'volume_id': base.get_id(volume)}
        return self._post(self.base_url, json=data)

    def detach(self, volume):
        data = {'force': True} if self.force_detach else {}
        volume_id = volume if self.force_detach else base.get_id(volume)
        url = "{}/{}".format(self.base_url, volume_id)
        return self._delete(url, json=data)


class ServerMetadata(base.Resource):
    pass


class ServerMetadataManager(Manager):
    resource_class = ServerMetadata

    def __init__(self, api, server):
        super(ServerMetadataManager, self).__init__(api)
        self.server_id = base.get_id(server)
        self.base_url = "/compute/servers/{}/metadata".format(self.server_id)

    def set(self, metadata):
        data = {'metadata': metadata}
        return self._post(self.base_url, json=data)

    def unset(self, metadata):
        data = {'metadata': {k: None for k in metadata}}
        return self._delete(self.base_url, json=data)


class ServerEvent(base.Resource):
    pass


class ServerEventManager(Manager):
    resource_class = ServerEvent

    def __init__(self, api, server):
        super(ServerEventManager, self).__init__(api)
        self.server_id = base.get_id(server)
        self.base_url = "/compute/servers/{}/events".format(self.server_id)

    def get(self, event):
        event_id = base.get_id(event)
        return self._get("{}/{}".format(self.base_url, event_id))

    def list(self):
        return self._list(self.base_url)
