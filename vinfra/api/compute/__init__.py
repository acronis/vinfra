from vinfra.api.compute.cluster import Cluster
from vinfra.api.compute.storages import ComputeStorageManager
from vinfra.api.compute.flavors import FlavorManager
from vinfra.api.compute.floating_ips import FloatingIpManager
from vinfra.api.compute.images import ImageManager
from vinfra.api.compute.k8saas import K8saasClusterManager
from vinfra.api.compute.keys import ComputeSshKeyManager
from vinfra.api.compute.load_balancer import LoadBalancerManager, PoolManager
from vinfra.api.compute import networks
from vinfra.api.compute import projects
from vinfra.api.compute.traits import TraitManager
from vinfra.api.compute.nodes import NodeManager
from vinfra.api.compute.quotas import QuotasManager
from vinfra.api.compute.routers import RouterManager
from vinfra.api.compute.security_groups import SecurityGroupManager
from vinfra.api.compute.security_groups import SecurityGroupRuleManager
from vinfra.api.compute.servers import ServerManager
from vinfra.api.compute import stacks
from vinfra.api.compute.storage_policies import StoragePolicyManager
from vinfra.api.compute.volume_snapshots import VolumeSnapshotManager
from vinfra.api.compute.volumes import VolumeManager
from vinfra.api.compute import vpn


class Compute(object):

    def __init__(self, api):
        self.api = api
        self.cluster = Cluster(api)
        self.storages = ComputeStorageManager(api)
        self.flavors = FlavorManager(api)
        self.floating_ips = FloatingIpManager(api)
        self.images = ImageManager(api)
        self.keys = ComputeSshKeyManager(api)
        self.networks = networks.NetworkManager(api)
        self.routers = RouterManager(api)
        self.nodes = NodeManager(api)
        self.projects = projects.ProjectManager(api)
        self.quotas = QuotasManager(api)
        self.security_groups = SecurityGroupManager(api)
        self.security_group_rules = SecurityGroupRuleManager(api)
        self.servers = ServerManager(api)
        self.storage_policies = StoragePolicyManager(api)
        self.subnets = networks.SubnetManager(api)
        self.traits = TraitManager(api)
        self.volumes = VolumeManager(api, self.images)
        self.volume_snapshots = VolumeSnapshotManager(api, self.images)
        self.k8saas = K8saasClusterManager(api)
        self.load_balancers = LoadBalancerManager(api)
        self.load_balancer_pools = PoolManager(api)
        self.stacks = stacks.StackManager(api)
        self.stack_resources = stacks.StackResourcesManager(api)
        self.stack_templates = stacks.StackTemplateManager(api)
        self.vpn = vpn.VpnManager(api)
