from vinfra.api import base
from vinfra.api.compute.base import Manager
from vinfra.utils import flatten_args


class CreateTaskEnabled(base.StatusTask):
    status = 'ACTIVE'


class CreateTaskDisabled(base.StatusTask):
    status = 'DISABLED'


class UpdateTaskEnabled(base.StatusTask):
    status = 'ACTIVE'


class UpdateTaskDisabled(base.StatusTask):
    status = 'DISABLED'


class UpdatePoolTask(base.ChainedTask):
    def __init__(self, pool, load_balancer, enabled=None):
        pool_task_class = (UpdateTaskDisabled if enabled is False else
                           UpdateTaskEnabled)
        # it looks like better to avoid dynamic class
        # creation and do not rely on the original LB status: better to
        # check LB is not in PENDING status.
        lb_task_class = type('LbTaskClass',
                             (base.StatusTask,),
                             {"status": load_balancer.status})
        super(UpdatePoolTask, self).__init__(
            pool,
            pool_task_class(pool.manager, pool),
            lb_task_class(load_balancer.manager, load_balancer)
        )

    def wait(self, timeout=None):
        super(UpdatePoolTask, self).wait(timeout=timeout)
        return self.task_results[0]


class RecreateTask(base.StatusTask):
    status = 'ACTIVE'


class FailoverTask(base.StatusTask):
    status = 'ACTIVE'


class LoadBalancer(base.Resource):
    def delete_async(self):
        return self.manager.delete_async(self)

    def delete(self):
        return self.manager.delete(self)

    def update_async(self, **params):
        return self.manager.update_async(self, **params)

    def update(self, **params):
        return self.manager.update(self, **params)

    def stats(self):
        return self.manager.stats(self)

    def recreate_async(self):
        return self.manager.recreate_async(self)

    def recreate(self):
        return self.manager.recreate(self)

    def failover_async(self):
        return self.manager.failover_async(self)


class LoadBalancerManager(Manager):
    resource_class = LoadBalancer
    base_url = "/compute/lbaas/loadbalancers"

    def list(self):
        return self._list(self.base_url)

    def get(self, load_balancer):
        load_balancer_id = base.get_id(load_balancer)
        return self._get("{}/{}".format(self.base_url, load_balancer_id))

    def create_async(
            self, name, network, address=None, description=None,
            enabled=None, floating_ip=None, pools=None, ha_enabled=None,
            ip_version=None,
    ):
        data = {
            'name': name,
            'network_id': base.get_id(network),
        }
        if address is not None:
            data['address'] = address
        if description is not None:
            data['description'] = description
        if enabled is not None:
            data['enabled'] = enabled
        if floating_ip is not None:
            data['floating_ip'] = floating_ip
        if pools is not None:
            data['pools'] = pools
        if ha_enabled is not None:
            data['ha_enabled'] = ha_enabled
        if ip_version:
            data['ip_version'] = ip_version

        load_balancer = self._post(self.base_url, json=data)
        if enabled is None or enabled:
            return CreateTaskEnabled(self, load_balancer)
        return CreateTaskDisabled(self, load_balancer)

    @base.async_wait
    def create(self, *args, **kwargs):
        return self.create_async(*args, **kwargs)

    def delete_async(self, load_balancer):
        load_balancer_id = base.get_id(load_balancer)
        self._delete("{}/{}".format(self.base_url, load_balancer_id))
        return base.DeleteTask(self, load_balancer)

    @base.async_wait
    def delete(self, load_balancer):
        return self.delete_async(load_balancer)

    def update_async(self, load_balancer, name=None, description=None, enabled=None):
        load_balancer_id = base.get_id(load_balancer)

        params = {}
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description
        if enabled is not None:
            params['enabled'] = enabled

        url = "{}/{}".format(self.base_url, load_balancer_id)
        self._patch(url, json=params)

        if enabled is None or enabled:
            return UpdateTaskEnabled(self, load_balancer)
        return UpdateTaskDisabled(self, load_balancer)

    @base.async_wait
    def update(self, *args, **kwargs):
        return self.update_async(*args, **kwargs)

    def stats(self, load_balancer):
        load_balancer_id = base.get_id(load_balancer)
        return self._get(
            "{}/{}/stats".format(self.base_url, load_balancer_id)
        )

    def recreate_async(self, load_balancer):
        load_balancer_id = base.get_id(load_balancer)
        load_balancer = self._post(
            "{}/{}/recreate".format(self.base_url, load_balancer_id)
        )
        return RecreateTask(self, load_balancer)

    @base.async_wait
    def recreate(self, *args, **kwargs):
        return self.recreate_async(*args, **kwargs)

    def failover_async(self, load_balancer):
        load_balancer_id = base.get_id(load_balancer)
        self._post(
            "{}/{}/failover".format(self.base_url, load_balancer_id)
        )
        return FailoverTask(self, load_balancer)


class Pool(base.Resource):
    def __init__(self, manager, info):
        if info:
            if 'healthmonitor' in info and info['healthmonitor'] is not None:
                if info['healthmonitor']['type'] == 'UDP-CONNECT':
                    info['healthmonitor']['type'] = 'UDP'
        super(Pool, self).__init__(manager, info)

    def update(self, *args, **kwargs):
        return self.manager.update(self, *args, **kwargs)

    def delete(self):
        return self.manager.delete(self)


class PoolManager(Manager):
    resource_class = Pool
    base_url = '/compute/lbaas/pools'

    def create_async(
            self, load_balancer, name, protocol, port, lb_algorithm,
            backend_protocol, backend_port, certificate=None,
            connection_limit=None, description=None, enabled=None,
            healthmonitor=None, members=None, private_key=None,
            sticky_session=None,
    ):  # pylint: disable=too-many-arguments
        load_balancer_id = base.get_id(load_balancer)

        data = {
            'loadbalancer_id': load_balancer_id,
            'name': name,
            'protocol': protocol,
            'protocol_port': port,
            'lb_algorithm': lb_algorithm,
            'backend_protocol': backend_protocol,
            'backend_protocol_port': backend_port,
        }
        data.update(flatten_args(
            certificate=certificate,
            connection_limit=connection_limit,
            description=description,
            enabled=enabled,
            healthmonitor=healthmonitor,
            members=members,
            private_key=private_key,
            sticky_session=sticky_session,
        ))
        if 'healthmonitor' in data:
            if data['healthmonitor']['type'] == 'UDP':
                data['healthmonitor']['type'] = 'UDP-CONNECT'

        pool = self._post(self.base_url, json=data)
        return CreateTaskEnabled(self, pool)

    @base.async_wait
    def create(self, *args, **kwargs):
        return self.create_async(*args, **kwargs)

    def list(self):
        return self._list(self.base_url)

    def get(self, pool):
        pool_id = base.get_id(pool)
        return self._get("{}/{}".format(self.base_url, pool_id))

    def update(
            self, pool, certificate=None, connection_limit=None,
            backend_protocol=None, backend_port=None, description=None,
            enabled=None, healthmonitor=None, lb_algorithm=None, members=None,
            name=None, private_key=None, protocol=None, protocol_port=None,
            sticky_session=None
    ):  # pylint: disable=too-many-arguments
        pool_id = base.get_id(pool)

        data = flatten_args(
            certificate=certificate,
            connection_limit=connection_limit,
            backend_protocol=backend_protocol,
            backend_protocol_port=backend_port,
            description=description,
            enabled=enabled,
            healthmonitor=healthmonitor,
            lb_algorithm=lb_algorithm,
            members=members,
            name=name,
            private_key=private_key,
            protocol=protocol,
            protocol_port=protocol_port,
            sticky_session=sticky_session,
        )
        if 'healthmonitor' in data:
            hm_type = data['healthmonitor'].get('type')
            if hm_type and hm_type == 'UDP':
                data['healthmonitor']['type'] = 'UDP-CONNECT'

        lb_manager = self.api.compute.load_balancers
        loadbalancer_id = pool.get().to_dict()['loadbalancer_id']
        load_balancer = lb_manager.get(loadbalancer_id)

        self._patch("{}/{}".format(self.base_url, pool_id), json=data)
        return UpdatePoolTask(pool, load_balancer, enabled=enabled)

    def delete(self, pool):
        pool_id = base.get_id(pool)
        return self._delete("{}/{}".format(self.base_url, pool_id))
