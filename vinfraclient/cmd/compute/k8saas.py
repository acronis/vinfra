import argparse
import re

from vinfra import exceptions as vinfra_exceptions
from vinfraclient import argtypes
from vinfraclient.argtypes import parse_dict_options
from vinfraclient.cmd import base
from vinfraclient import exceptions
from vinfraclient.utils import find_resource


def _common_set_options(parser):
    parser.add_argument(
        "--master-node-count",
        metavar="<count>",
        type=int,
        help="The amount of master nodes in the Kubernetes cluster"
    )
    parser.add_argument(
        "--node-count",
        metavar="<count>",
        type=int,
        help="The amount of worker nodes in the Kubernetes cluster"
    )
    parser.add_argument(
        "--min-node-count",
        metavar="<count>",
        type=int,
        help="The minimum amount of worker nodes in the Kubernetes cluster"
    )
    parser.add_argument(
        "--max-node-count",
        metavar="<count>",
        type=int,
        help="The maximum amount of worker nodes in the Kubernetes cluster"
    )


def _advanced_network_configuratin_args(parser):
    parser.add_argument(
        "--containers-network-cidr",
        metavar="<cidr>",
        help="Container network range in CIDR notation"
    )
    parser.add_argument(
        "--containers-network-node-subnet-prefix-length",
        metavar="<prefix_length>",
        type=int,
        help="The prefix length of a container subnet allocated to "
             "each Kubernetes node"
    )
    parser.add_argument(
        "--service-network-cidr",
        metavar="<cidr>",
        help="Kubernetes service network range in CIDR notation"
    )
    parser.add_argument(
        "--dns-service-ip",
        metavar="<ip>",
        help="DNS service IP address"
    )


def _cluster_arg(parser):
    parser.add_argument(
        "cluster",
        metavar="<cluster>",
        help="Cluster ID or name"
    )


def _workergroup_arg(parser):
    parser.add_argument(
        "workergroup",
        metavar="<worker-group>",
        help="Worker group ID or name"
    )


def _storage_policy_arg(parser, required=False):
    parser.add_argument(
        "--volume-storage-policy",
        metavar="<policy>",
        required=required,
        help="The name of the storage policy for the volume "
             "where containers will reside"
    )


def _labels_arg(parser):

    def parse_labels(value):
        labels = parse_dict_options(value)
        labels = {k.replace('-', '_'): v for k, v in labels.items()}
        return labels

    parser.add_argument(
        "--labels",
        metavar="<key1=value1,key2=value2,key3=value3...>",
        type=parse_labels,
        help="Arbitrary labels in the form of key=value pairs to "
             "associate with a cluster"
    )


def check_agent_health(cluster):
    health = cluster.healthcheck()
    if health is None:
        return

    unhealth_servers = [
        server['id'] for ng in health.nodegroups
        for server in ng['servers']
        if server['agent_status'] != 'active']

    if unhealth_servers:
        raise vinfra_exceptions.VinfraError(
            "The following Kubernetes servers are not responding to requests: "
            "{}".format(", ".join(unhealth_servers)))


class ListK8saasCluster(base.Lister):
    _description = "List Kubernetes clusters."
    _default_fields = ['id', 'name', 'status']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.k8saas.list()


class ShowK8saasCluster(base.ShowOne):
    _description = "Display Kubernetes cluster details."

    def configure_parser(self, parser):
        _cluster_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.compute.k8saas,
                             parsed_args.cluster)


class ShowK8saasClusterHealth(base.ShowOne):
    _description = "Display Kubernetes cluster health details."

    def configure_parser(self, parser):
        _cluster_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)
        return cluster.healthcheck()


class ShowK8saasClusterConfig(base.Command):
    _description = "Display Kubernetes cluster config."

    def configure_parser(self, parser):
        _cluster_arg(parser)

    # NOTE(akurbatov): override take_action to not produce
    # "Operation successful" on stdout.
    def take_action(self, parsed_args):
        data = self.app.vinfra.compute.k8saas.get_config(parsed_args.cluster)
        self.app.stdout.write(data + '\n')


class RotateK8saasClusterCA(base.TaskCommand):
    _description = "Rotate Kubernetes cluster CA certificates."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        parser.add_argument(
            "--skip-healthcheck",
            action="store_true",
            help=argparse.SUPPRESS,
        )

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)

        if not parsed_args.skip_healthcheck:
            check_agent_health(cluster)

        task = cluster.rotate_ca_async()
        return task


class UpgradeK8saasCluster(base.TaskCommand):
    _description = "Upgrade Kubernetes cluster."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        parser.add_argument(
            "version",
            metavar="<version>",
            help="Kubernetes version"
        )
        parser.add_argument(
            "--skip-healthcheck",
            action="store_true",
            help=argparse.SUPPRESS,
        )

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)

        warnings = getattr(cluster, 'warnings', [])
        if not parsed_args.skip_healthcheck and \
                'upgrade-requires-reboot' not in warnings:
            check_agent_health(cluster)

        task = cluster.upgrade_async(
            version=parsed_args.version
        )
        return task


class K8saasDefaultsShow(base.ShowOne):
    _description = "Show default Kubernetes parameters values"

    def configure_parser(self, parser):
        parser.add_argument(
            "version",
            metavar="<version>",
            nargs='?',
            help="Kubernetes version"
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.k8saas.get_defaults(
            version=parsed_args.version)


class K8saasDefaultsSet(base.ShowOne):
    _description = "Manage default Kubernetes parameters values"

    def configure_parser(self, parser):
        parser.add_argument(
            "version",
            metavar="<version>",
            nargs='?',
            help="Kubernetes version"
        )
        _labels_arg(parser)
        parser.add_argument(
            "--master-flavor",
            metavar="<flavor>",
            help="The flavor to be used for Kubernetes master nodes"
        )
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            help="The flavor to be used for Kubernetes worker nodes"
        )
        parser.add_argument(
            "--dns-nameserver",
            metavar="<dns-nameserver>",
            help="The DNS nameserver to use for clusters"
        )
        parser.add_argument(
            "--discovery-url",
            metavar="<discovery-url>",
            help="Specifies custom delivery url for node discovery"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing defaults associated with the version"
        )

    def do_action(self, parsed_args):
        options = ['master_flavor', 'flavor', 'dns_nameserver', 'discovery_url',
                   'labels']
        params = base.flatten_args(parsed_args, options)
        if not parsed_args.clear and not params:
            raise exceptions.ValidationError('No options are provided')

        if not parsed_args.version:
            parsed_args.version = 'default'
        if parsed_args.clear:
            data = self.app.vinfra.compute.k8saas.set_defaults(parsed_args.version)
        if params:
            data = self.app.vinfra.compute.k8saas.set_defaults(
                parsed_args.version, **params)
        return data


class CreateK8saasCluster(base.TaskCommand):
    _description = "Create a new Kubernetes cluster."

    def configure_parser(self, parser):
        _common_set_options(parser)

        _storage_policy_arg(parser, required=False)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Kubernetes cluster name"
        )
        parser.add_argument(
            "--kubernetes-version",
            metavar="<version>",
            help="Kubernetes version"
        )
        parser.add_argument(
            "--master-flavor",
            metavar="<flavor>",
            required=True,
            help="The flavor to be used for Kubernetes master nodes"
        )
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            required=True,
            help="The flavor to be used for Kubernetes worker nodes"
        )
        parser.add_argument(
            "--volume-size",
            metavar="<size>",
            type=int,
            help="The storage size of containers on each Kubernetes node"
            )
        parser.add_argument(
            "--external-network",
            metavar="<network>",
            required=True,
            help="The ID or name of the network that will provide Internet "
                 "access to Kubernetes nodes"
        )
        parser.add_argument(
            "--network",
            metavar="<network>",
            help="The ID or name of the network that will provide networking "
                 "to Kubernetes nodes"
        )
        parser.add_argument(
            "--key-name",
            metavar="<key-name>",
            required=True,
            help="The key pair to use for accessing the Kubernetes nodes"
        )
        parser.add_argument(
            "--use-floating-ip",
            metavar="<use-floating-ip>",
            type=argtypes.boolean,
            help="Use floating IP addresses for all Kubernetes nodes "
                 "('true' or 'false')."
        )
        parser.add_argument(
            "--enable-public-access",
            action="store_true",
            help="Use floating IP addresses for Kubernetes API "
                 "('true' or 'false')."
        )
        parser.add_argument(
            "--api-lb-flavor",
            metavar="<api-lb-flavor>",
            help="The ID or name of octavia flavor to use for API and ETCD "
                 "loadbalancers."
        )
        parser.add_argument(
            "--default-lb-flavor",
            metavar="<default-lb-flavor>",
            help="The ID or name of octavia flavor to use as default for"
                 " openstack-provider-created loadbalancers."
        )
        parser.add_argument(
            "--monitoring-enabled",
            action="store_true",
            help="Enable installation of cluster monitoring.",
        )
        _labels_arg(parser)
        _advanced_network_configuratin_args(parser)

    def do_action(self, parsed_args):  # pylint: disable=too-many-statements
        master_flavor = find_resource(self.app.vinfra.compute.flavors,
                                      parsed_args.master_flavor)

        kwargs = {
            'name': parsed_args.name,
            'master_flavor': master_flavor.name,
            'key_name': parsed_args.key_name,
        }

        ext_network = find_resource(self.app.vinfra.compute.networks,
                                    parsed_args.external_network)
        kwargs['external_network_id'] = ext_network.id

        flavor = find_resource(self.app.vinfra.compute.flavors,
                               parsed_args.flavor)

        worker_pool = {
            'flavor': flavor.name,
        }
        if parsed_args.node_count is not None:
            worker_pool['node_count'] = parsed_args.node_count
        if parsed_args.min_node_count:
            worker_pool['min_node_count'] = parsed_args.min_node_count
        if parsed_args.max_node_count:
            worker_pool['max_node_count'] = parsed_args.max_node_count
        kwargs['worker_pools'] = [worker_pool]

        if parsed_args.network is not None:
            network = find_resource(self.app.vinfra.compute.networks,
                                    parsed_args.network)
            kwargs['network_id'] = network.id
        if parsed_args.use_floating_ip is not None:
            kwargs['floating_ip_enabled'] = parsed_args.use_floating_ip
        if parsed_args.enable_public_access is not None:
            kwargs['public_access_enabled'] = parsed_args.enable_public_access
        if parsed_args.master_node_count is not None:
            kwargs['master_node_count'] = parsed_args.master_node_count
        if parsed_args.kubernetes_version is not None:
            kwargs['version'] = parsed_args.kubernetes_version
        if parsed_args.volume_size is not None:
            kwargs['containers_volume_size'] = parsed_args.volume_size
        if parsed_args.volume_storage_policy is not None:
            kwargs['containers_volume_storage_policy'] = \
                parsed_args.volume_storage_policy
        if parsed_args.api_lb_flavor is not None:
            kwargs['api_lb_flavor'] = parsed_args.api_lb_flavor
        if parsed_args.default_lb_flavor is not None:
            kwargs['default_lb_flavor'] = parsed_args.default_lb_flavor
        if parsed_args.monitoring_enabled:
            kwargs['monitoring_enabled'] = True
        if parsed_args.labels:
            kwargs['labels'] = parsed_args.labels

        containers_network = {}
        if parsed_args.containers_network_cidr is not None:
            containers_network['cidr'] = parsed_args.containers_network_cidr
        if parsed_args.containers_network_node_subnet_prefix_length is not None:
            containers_network['node_subnet_prefix_length'] = \
                parsed_args.containers_network_node_subnet_prefix_length
        if containers_network:
            kwargs['containers_network'] = containers_network

        service_network = {}
        if parsed_args.service_network_cidr is not None:
            service_network['cidr'] = parsed_args.service_network_cidr
        if parsed_args.dns_service_ip is not None:
            service_network['dns_ip'] = parsed_args.dns_service_ip
        if service_network:
            kwargs['service_network'] = service_network

        return self.app.vinfra.compute.k8saas.create_async(**kwargs)


class SetK8saasCluster(base.TaskCommand):
    _description = "Modify Kubernetes cluster parameters."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        parser.add_argument(
            "--node-count",
            metavar="<count>",
            type=int,
            help="The amount of worker nodes in the Kubernetes cluster"
        )

    def do_action(self, parsed_args):
        vinfra = self.app.vinfra

        kwargs = {}
        if parsed_args.node_count is not None:
            kwargs['worker_pools'] = [{'node_count': parsed_args.node_count}]

        return find_resource(vinfra.compute.k8saas,
                             parsed_args.cluster).update_async(**kwargs)


class DeleteK8saasCluster(base.TaskCommand):
    _description = "Delete a Kubernetes cluster."

    def configure_parser(self, parser):
        _cluster_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)
        task = cluster.delete_async()
        return task


class ListK8saasWorkerGroup(base.Lister):
    _description = "List Kubernetes worker groups."
    _default_fields = ['id', 'name', 'status']

    def configure_parser(self, parser):
        _cluster_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)
        return cluster.nodegroups_manager.list()


class ShowK8saasWorkerGroup(base.ShowOne):
    _description = "Display Kubernetes worker group details."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        _workergroup_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)
        return find_resource(cluster.nodegroups_manager,
                             parsed_args.workergroup)


class CreateK8saasWorkerGroup(base.TaskCommand):
    _description = "Create a new Kubernetes worker group."

    def configure_parser(self, parser):
        _cluster_arg(parser)

        parser.add_argument(
            "name",
            metavar="<name>",
            help="Kubernetes worker group name"
        )
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            required=True,
            help="The flavor to be used for Kubernetes worker group"
        )
        parser.add_argument(
            "--node-count",
            metavar="<count>",
            type=int,
            default=1,
            help="The amount of worker nodes in the Kubernetes worker group"
        )
        parser.add_argument(
            "--min-node-count",
            metavar="<count>",
            type=int,
            help="The minimum amount of worker nodes in the Kubernetes cluster"
        )
        parser.add_argument(
            "--max-node-count",
            metavar="<count>",
            type=int,
            help="The maximum amount of worker nodes in the Kubernetes cluster"
        )
        _labels_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)

        flavor = find_resource(self.app.vinfra.compute.flavors,
                               parsed_args.flavor)

        kwargs = dict(
            flavor=flavor.name,
            name=parsed_args.name,
            node_count=parsed_args.node_count,
            min_node_count=parsed_args.min_node_count,
            max_node_count=parsed_args.max_node_count,
            labels=parsed_args.labels,
        )

        return cluster.nodegroups_manager.create_async(**kwargs)


def validate_remove_node_id(value):
    # number or UUID in lower case with '-'
    if not re.match(r'^(\d+|[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}'
                    r'-[89ab][a-f0-9]{3}-[a-f0-9]{12})$', value):
        raise argparse.ArgumentTypeError(
            '"{}" is invalid node ID'.format(value))
    return value


class SetK8saasWorkerGroup(base.TaskCommand):
    _description = "Modify Kubernetes worker group parameters."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        _workergroup_arg(parser)
        parser.add_argument(
            "--node-count",
            metavar="<count>",
            type=int,
            help="The amount of worker nodes in the Kubernetes cluster"
        )
        parser.add_argument(
            "--min-node-count",
            metavar="<count>",
            type=int,
            help="The minimum amount of worker nodes in the Kubernetes cluster"
        )
        max_node_count_group = parser.add_mutually_exclusive_group()
        max_node_count_group.add_argument(
            "--max-node-count",
            metavar="<count>",
            type=int,
            help="The maximum amount of worker nodes in the Kubernetes cluster."
        )
        parser.add_argument(
            "--remove-node",
            metavar="<id>",
            dest="nodes_to_remove",
            action="append",
            type=validate_remove_node_id,
            help="The ID of worker node to remove",
        )

    def do_action(self, parsed_args):
        vinfra = self.app.vinfra

        cluster = find_resource(
            vinfra.compute.k8saas, parsed_args.cluster)
        nodegroup = find_resource(
            cluster.nodegroups_manager, parsed_args.workergroup)

        params = dict(
            node_count=parsed_args.node_count,
            min_node_count=parsed_args.min_node_count,
            nodes_to_remove=parsed_args.nodes_to_remove,
        )
        if parsed_args.max_node_count:
            params['max_node_count'] = parsed_args.max_node_count

        return nodegroup.update_async(**params)


class DeleteK8saasWorkerGroup(base.TaskCommand):
    _description = "Delete a Kubernetes worker group."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        _workergroup_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)
        workergroup = find_resource(cluster.nodegroups_manager,
                                    parsed_args.workergroup)

        return workergroup.delete_async()


class UpgradeK8saasWorkerGroup(base.TaskCommand):
    _description = "Upgrade Kubernetes worker group."

    def configure_parser(self, parser):
        _cluster_arg(parser)
        _workergroup_arg(parser)

    def do_action(self, parsed_args):
        cluster = find_resource(self.app.vinfra.compute.k8saas,
                                parsed_args.cluster)

        workergroup = find_resource(cluster.nodegroups_manager,
                                    parsed_args.workergroup)

        return workergroup.upgrade_async()
