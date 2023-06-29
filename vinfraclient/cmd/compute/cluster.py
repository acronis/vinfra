import argparse
import os
import yaml

from vinfraclient.argtypes import parse_dict_options
from vinfraclient.argtypes import parse_pair_options, parse_list_options
from vinfraclient.cmd.base import Lister, ShowOne, TaskCommand
from vinfraclient.cmd.compute.storage_policy import storage_policy_options
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import (
    find_resource, find_resources, join_options
)


def get_subnet_from_pairs(pairs):
    subnet = {}
    for key, value in pairs:
        if key == 'dhcp':
            if value not in ['enable', 'disable']:
                raise ValidationError(
                    "--subnet 'dhcp' invalid choice: {!r}".format(value))
            subnet['enable_dhcp'] = value == 'enable'
        elif key == 'allocation-pool':
            try:
                start, end = value.split('-')
            except ValueError:
                raise ValidationError("--subnet 'allocation-pool' unrecognized"
                                      "value: {!r}".format(value))
            subnet.setdefault("allocation_pools", []).append({
                'start_address': start, 'end_address': end
            })
        elif key == 'dns-server':
            subnet.setdefault("dns_servers", []).append(value)
        elif key in ['cidr', 'gateway']:
            subnet[key] = value
        else:
            raise ValidationError(
                "unrecognized argument: {}".format(key))
    if not subnet.get('cidr'):
        raise ValidationError("--subnet 'cidr' is required")
    return subnet


_CUSTOM_PARAM_SHORTCUTS = {
    'nova_scheduler_host_subset_size': ('nova-scheduler',
                                        'nova.conf',
                                        'DEFAULT',
                                        'scheduler_host_subset_size'),
    'nova_compute_cpu_allocation_ratio': ('nova-compute',
                                          'nova.conf',
                                          'DEFAULT',
                                          'cpu_allocation_ratio'),
    'nova_compute_ram_allocation_ratio': ('nova-compute',
                                          'nova.conf',
                                          'DEFAULT',
                                          'ram_allocation_ratio'),
    'neutron_openvswitch_vxlan_port': ('neutron-openvswitch-agent',
                                       'ml2_conf.ini',
                                       'agent',
                                       'vxlan_udp_port'),
    'placement_default_quota': ('placement-api',
                                'placement.conf',
                                'quota',
                                'default_trait_quota'),
    'load_balancer_default_quota': ('octavia-api',
                                    'octavia.conf',
                                    'quotas',
                                    'default_load_balancer_quota'),
    'k8s_default_quota': ('magnum-api',
                          'magnum.conf',
                          'quotas',
                          'max_clusters_per_project'),
    # Add another shortcuts here.
}


def _add_custom_param_args(parser):
    parser.add_argument(
        "--custom-param",
        action="append",
        metavar=('<service_name>', '<config_file>', '<section>', '<property>', '<value>'),
        nargs=5,
        help="OpenStack custom parameters."
    )
    parser.add_argument(
        "--nova-scheduler-ram-weight-multiplier",
        metavar="<value>",
        help="DEPRECATED! Use --scheduler-config."
    )

    for shortcut, path in _CUSTOM_PARAM_SHORTCUTS.items():
        parser.add_argument(
            "--{}".format(shortcut.replace('_', '-')),
            metavar="<value>",
            help="Shortcut for --custom-param {} <value>.".format(' '.join(path))
        )


def yaml_config_file(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError('%s does not exist' % path)

    with open(path, 'r') as fp:
        try:
            data = yaml.safe_load(fp)
        except yaml.YAMLError as ex:
            raise argparse.ArgumentTypeError('Cannot parse YAML: %s' % ex)

    return data


def _add_common_options(parser):
    parser.add_argument(
        "--force",
        action="store_true",
        default=None,
        help="Skip checks for minimal hardware requirements."
    )
    parser.add_argument(
        "--cpu-model",
        metavar="<cpu-model>",
        help="CPU model for virtual machines."
    )
    parser.add_argument(
        "--cpu-features",
        metavar="<cpu-features>",
        type=lambda x: x.split(','),
        help="A comma-separated list of CPU features to enable or disable for virtual machines.\n"
             "For example, 'ssbd,+vmx,-mpx' will enable ssbd and vmx and disable mpx.\n"
             "Note that if the first feature starts with a dash, the following syntax is used: --cpu-features='-vmx'."
    )
    parser.add_argument(
        "--enable-k8saas",
        action="store_true",
        default=None,
        help="Enable Kubernetes-as-a-Service services."
    )
    parser.add_argument(
        "--enable-lbaas",
        action="store_true",
        default=None,
        help="Enable Load-Balancing-as-a-Service services."
    )
    parser.add_argument(
        "--enable-metering",
        action="store_true",
        default=None,
        help="Enable metering services."
    )
    parser.add_argument(
        "--notification-forwarding",
        metavar="<transport-url>",
        dest="notification_forwarding",
        default=None,
        help="Enable notification forwarding through the specified transport URL.\n"
             "Transport URL format:\n"
             "driver://[user:pass@]host:port[,[userN:passN@]hostN:portN]?query\n"
             "Supported drivers: ampq, kafka, rabbit.\n"
             "Query params: topic - topic name, driver - messaging driver, "
             "possible values are "
             "messaging, messagingv2, routing, log, test, noop.\n"
             "Example: kafka://10.10.10.10:9092?topic=notifications"
    )
    parser.add_argument(
        "--disable-notification-forwarding",
        dest="notification_forwarding",
        action="store_false",
        help="Disable notification forwarding"
    )
    parser.add_argument(
        "--endpoint-hostname",
        metavar="<hostname>",
        dest="endpoint_hostname",
        default=None,
        help="Use given hostname for public endpoint.\n"
             "Specify empty value in quotes to use raw IP."
    )
    parser.add_argument(
        "--pci-passthrough-config",
        metavar="<path>",
        dest="pci_passthrough",
        type=yaml_config_file,
        default=None,
        help="Path to the PCI passthrough configuration file."
    )
    parser.add_argument(
        "--scheduler-config",
        metavar="<path>",
        dest="scheduler",
        type=yaml_config_file,
        default=None,
        help="Path to the scheduler configuration file."
    )
    _add_custom_param_args(parser)


def _custom_params_from(parsed_args):
    custom_params = []

    if parsed_args.custom_param is not None:
        custom_params.extend(parsed_args.custom_param)

    for shortcut, (serv, conf, sect, prop) in _CUSTOM_PARAM_SHORTCUTS.items():
        value = getattr(parsed_args, shortcut)
        if value is not None:
            custom_params.append([serv, conf, sect, prop, value])

    if custom_params:
        return [{
            'service_name': it[0],
            'config_file': it[1],
            'section': it[2],
            'property': it[3],
            'value': it[4],
        } for it in custom_params]

    return None


class ShowCompute(ShowOne):
    _description = "Display compute cluster details."

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute.cluster.get()
        return compute


class CreateCompute(TaskCommand):
    _description = "Create compute cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=True,
            help="A comma-separated list of node IDs or hostnames."
        )
        parser.add_argument(
            "--public-network",
            metavar="<network>",
            help="A physical network to connect the public virtual network to."
                 "It must include the 'VM public' traffic type."
        )
        parser.add_argument(
            "--subnet",
            metavar="cidr=CIDR[,key1=value1,key2=value2...]",
            type=parse_pair_options,
            help="Subnet for IP address management in the public virtual "
                 "network (the --public-network option is required):\n"
                 "cidr: subnet range in CIDR notation;\n"
                 "gateway: gateway IP address (optional);\n"
                 "dhcp: enable/disable the virtual DHCP server (optional);\n"
                 "allocation-pool: allocation pool of IP addresses from CIDR "
                 "in the format ip1-ip2, where ip1 and ip2 are starting and "
                 "ending IP addresses correspondingly. Specify the key "
                 "multiple times to create multiple IP pools (optional);\n"
                 "dns-server: DNS server IP address, specify multiple times "
                 "to set multiple DNS servers (optional).\n"
                 "Example: --subnet cidr=192.168.5.0/24,dhcp=enable"
        )
        parser.add_argument(
            "--vlan-id",
            metavar="<vlan-id>",
            type=int,
            choices=range(1, 4095),
            help="Create VLAN based public network by given VLAN id."
        )
        parser.add_argument(
            "--mtu",
            metavar="<mtu>",
            type=int,
            help='MTU value of public network',
        )
        _add_common_options(parser)
        storage_policy_options(parser, prefix='default-storage-policy-', failure_domain=True)

    def do_action(self, parsed_args):
        nodes = [find_resource(self.app.vinfra.nodes, node)
                 for node in parsed_args.nodes]

        external_network = None
        if parsed_args.public_network:
            net = find_resource(self.app.vinfra.networks,
                                parsed_args.public_network)
            external_network = {'network_id': net.id}

            if parsed_args.vlan_id:
                external_network['vlan_id'] = parsed_args.vlan_id

            if parsed_args.mtu:
                external_network['mtu'] = parsed_args.mtu

        if parsed_args.subnet:
            if not parsed_args.public_network:
                raise ValidationError(
                    "The --subnet option requires the --public-network "
                    "option to be specified.")
            subnet = get_subnet_from_pairs(parsed_args.subnet)
            external_network['subnet'] = subnet

        default_storage_policy = {}
        if parsed_args.tier is not None:
            default_storage_policy['tier'] = parsed_args.tier
        if parsed_args.redundancy is not None:
            default_storage_policy['redundancy'] = parsed_args.redundancy
        if parsed_args.failure_domain is not None:
            default_storage_policy['failure_domain'] = parsed_args.failure_domain
        default_storage_policy = default_storage_policy or None

        scheduler = parsed_args.scheduler
        ram_weight_multiplier = parsed_args.nova_scheduler_ram_weight_multiplier
        if ram_weight_multiplier is not None:
            if scheduler is not None:
                scheduler['ram_weight_multiplier'] = ram_weight_multiplier
            else:
                scheduler = {'ram_weight_multiplier': ram_weight_multiplier}

        return self.app.vinfra.compute.cluster.create_async(
            nodes, cpu_model=parsed_args.cpu_model,
            external_network=external_network, force=parsed_args.force,
            enable_k8saas=parsed_args.enable_k8saas,
            enable_lbaas=parsed_args.enable_lbaas,
            enable_metering=parsed_args.enable_metering,
            notification_forwarding=parsed_args.notification_forwarding,
            custom_params=_custom_params_from(parsed_args),
            external_address=parsed_args.endpoint_hostname,
            pci_passthrough=parsed_args.pci_passthrough,
            default_storage_policy=default_storage_policy,
            scheduler=scheduler,
            cpu_features=parsed_args.cpu_features
        )


class DeleteCompute(TaskCommand):
    _description = "Delete a node from the compute cluster."

    def do_action(self, parsed_args):
        task = self.app.vinfra.compute.cluster.delete_async()
        return task


class AddNode(TaskCommand):
    _description = "Add a node to the compute cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--compute",
            metavar="<is_compute>",
            dest="roles",
            action="append_const",
            const="compute",
            help="Compute node role"
        )
        parser.add_argument(
            "--controller",
            metavar="<is_controller>",
            dest="roles",
            action="append_const",
            const="controller",
            help="Compute controller node role"
        )
        parser.add_argument(
            "--hypervisor-type",
            choices=["VM", "CT"],
            default=None,
            # Hide help and cli options while not implemented in the interface
            help=argparse.SUPPRESS,
            # help="Compute node hypervisor type"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=None,
            help="Skip checks for minimal hardware requirements."
        )
        parser.add_argument(
            "nodes",
            metavar="<node>",
            nargs="+",
            help="ID or hostname of the compute node"
        )

    def do_action(self, parsed_args):
        if not parsed_args.roles:
            raise ValidationError(
                "At least one compute role for node should be specified"
            )

        nodes = find_resources(self.app.vinfra.nodes, parsed_args.nodes)
        task = self.app.vinfra.compute.nodes.add_async(nodes,
                                                       parsed_args.roles,
                                                       hypervisor_type=parsed_args.hypervisor_type,
                                                       force=parsed_args.force)
        return task


class DeleteNode(TaskCommand):
    _description = "Release a node from the compute cluster."

    def configure_parser(self, parser):
        parser.add_argument(
            "--compute",
            metavar="<is_compute>",
            dest="roles",
            action="append_const",
            const="compute",
            help="Compute node role"
        )
        parser.add_argument(
            "--controller",
            metavar="<is_controller>",
            dest="roles",
            action="append_const",
            const="controller",
            help="Compute controller node role"
        )
        parser.add_argument(
            "nodes",
            metavar="<node>",
            nargs="+",
            help="ID or hostname of the compute node"
        )

    def do_action(self, parsed_args):
        nodes = find_resources(self.app.vinfra.nodes, parsed_args.nodes)
        task = self.app.vinfra.compute.nodes.delete_async(nodes,
                                                          parsed_args.roles)
        return task


class ClusterStat(ShowOne):
    _description = "Display compute cluster statistics"

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.cluster.stat()


class BaselineCPU(ShowOne):
    _description = "Determine baseline CPU models for the compute cluster"

    def configure_parser(self, parser):
        parser.add_argument(
            "--nodes",
            metavar="<nodes>",
            type=parse_list_options,
            required=False,
            help="A comma-separated list of node IDs or hostnames."
        )

    def do_action(self, parsed_args):
        cluster_info = self.app.vinfra.compute.cluster.info()
        baselines = {node['hostname']:
                     {'models': node['models'], 'patched': node['patched']}
                     for node in cluster_info}
        if parsed_args.nodes:
            nodes = [find_resource(self.app.vinfra.nodes, node)
                     for node in parsed_args.nodes]
            baselines = {node.host: baselines[node.host] for node in nodes}

        all_models = {model for node in baselines.values() for model in node['models']}
        common_models = list(
            all_models.intersection(*[node['models'] for node in baselines.values()]))

        all_patched = all([node['patched'] for node in baselines.values()])

        baselines['All selected nodes'] = {
            'models': common_models, 'patched': all_patched}
        return baselines


class SetCompute(TaskCommand):
    _description = "Change compute cluster parameters"

    def configure_parser(self, parser):
        _add_common_options(parser)

    def do_action(self, parsed_args):
        scheduler = parsed_args.scheduler
        ram_weight_multiplier = parsed_args.nova_scheduler_ram_weight_multiplier
        if ram_weight_multiplier is not None:
            if scheduler is not None:
                scheduler['ram_weight_multiplier'] = ram_weight_multiplier
            else:
                scheduler = {'ram_weight_multiplier': ram_weight_multiplier}

        return self.app.vinfra.compute.cluster.reconfigure_async(
            cpu_model=parsed_args.cpu_model,
            enable_k8saas=parsed_args.enable_k8saas,
            enable_lbaas=parsed_args.enable_lbaas,
            enable_metering=parsed_args.enable_metering,
            notification_forwarding=parsed_args.notification_forwarding,
            custom_params=_custom_params_from(parsed_args),
            external_address=parsed_args.endpoint_hostname,
            force=parsed_args.force,
            pci_passthrough=parsed_args.pci_passthrough,
            scheduler=scheduler,
            cpu_features=parsed_args.cpu_features
        )


def _add_storage_common_options(parser):
    parser.add_argument(
        "name",
        metavar="<name>",
        help="Compute storage name",
    )
    parser.add_argument(
        "--params",
        metavar="<param=value>[,<param2=value2>] [--params <param3=value3>] ...",
        action='append',
        type=parse_dict_options,
        default=[{}],
        help=(
            r"--params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ...\n"
            "A comma-separated list of parameters in the format `key=value`."
            " This option can be used multiple times."
        )
    )
    parser.add_argument(
        "--secret-params",
        metavar="<param=value>[,<param2=value2>] [--secret-params <param3=value3>] ...",
        action='append',
        type=parse_dict_options,
        help=(
            r"--secret-params \<param=value\>[,\<param2=value2\>] [--params \<param3=value3\>] ..."
            "A comma-separated list of secret parameters in the format"
            " `key=value`. This option can be used multiple times."
        )
    )
    parser.add_argument(
        "--nfs-mount-options",
        metavar="<opts>",
        type=str,
        help="A comma-separated list of mount options for compute "
             "storages that use the generic NFS driver, with additional "
             "flags separated by spaces. Refer to 'mount(8)' and 'nfs(5)'.\n"
             "Example: 'nfsvers=4,minorversion=0,timeo=150,retrans=3 -m -s'\n"
             "Note that if nfs_shares_config is used, these mount options are "
             "applied to every share listed in the config file, "
             "unless overwritten in config file."
    )
    enabled = parser.add_mutually_exclusive_group()
    enabled.add_argument(
        "--enable",
        dest="enabled",
        action="store_true",
        default=None,
        help="Enable the compute storage",
    )
    enabled.add_argument(
        "--disable",
        dest="enabled",
        action="store_false",
        default=None,
        help="Disable the compute storage",
    )
    storage_type = parser.add_mutually_exclusive_group()
    storage_type.add_argument(
        "--pure",
        dest="storage_type",
        action="store_const",
        default=None,
        const="purestorage",
        help="Shortcut for adding a storage that uses the PureStorage driver."
    )
    storage_type.add_argument(
        "--nfs",
        dest="storage_type",
        action="store_const",
        default=None,
        const="nfs",
        help="Shortcut for adding a storage that uses the generic NFS driver."
    )


STORAGE_PARAMS = {
    'purestorage': {
        'volume_driver': 'cinder.volume.drivers.pure.PureISCSIDriver',
        'use_multipath_for_image_xfer': 'True',
    },
    'nfs': {
        'volume_driver': 'cinder.volume.drivers.nfs.NfsDriver',
        'nfs_sparsed_volumes': 'True',
        'nfs_snapshot_support': 'True',
        'nas_secure_file_permissions': 'False',
        'nas_secure_file_operations': 'False',
        'nfs_qcow2_volumes': 'True',
    },
}


def _set_default_params(parsed_args):
    default_params = STORAGE_PARAMS.get(parsed_args.storage_type)
    default_params['volume_backend_name'] = parsed_args.name
    params = parsed_args.params[0]
    if not params:
        params = default_params
    else:
        for param in default_params:
            if param in params:
                continue
            params[param] = default_params[param]
    return params


class AddComputeStorage(TaskCommand):
    _description = "Add a compute storage."

    def configure_parser(self, parser):
        _add_storage_common_options(parser)

    def do_action(self, parsed_args):
        if parsed_args.storage_type:
            parsed_args.params[0] = _set_default_params(parsed_args)
        if parsed_args.nfs_mount_options:
            parsed_args.params[0]['nfs_mount_options'] = parsed_args.nfs_mount_options
        return self.app.vinfra.compute.storages.create_async(
            name=parsed_args.name,
            params=join_options(parsed_args.params),
            secret_params=join_options(parsed_args.secret_params),
            enabled=parsed_args.enabled,
        )


class SetComputeStorage(TaskCommand):
    _description = "Modify compute storage parameters."

    def configure_parser(self, parser):
        _add_storage_common_options(parser)
        parser.add_argument(
            "--unset-params",
            metavar="<params>",
            type=parse_list_options,
            help="A comma-separated list of parameters to unset"
        )
        parser.add_argument(
            "--unset-secret-params",
            metavar="<params>",
            type=parse_list_options,
            help="A comma-separated list of secret parameters to unset"
        )

    def do_action(self, parsed_args):
        compute_storage = find_resource(self.app.vinfra.compute.storages,
                                        parsed_args.name)
        if parsed_args.nfs_mount_options:
            parsed_args.params[0]['nfs_mount_options'] = parsed_args.nfs_mount_options
        return compute_storage.update_async(
            params=join_options(parsed_args.params, parsed_args.unset_params),
            secret_params=join_options(parsed_args.secret_params, parsed_args.unset_secret_params),
            enabled=parsed_args.enabled,
        )


class ListComputeStorage(Lister):
    _description = "List existing compute storages."
    _default_fields = ['name', 'params', 'secret_params', 'enabled', 'configured']

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.storages.list()


class ShowComputeStorage(ShowOne):
    _description = "Show details of a compute storage."

    def configure_parser(self, parser):
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Compute storage name",
        )

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.compute.storages,
                             parsed_args.name)


class RemoveComputeStorage(TaskCommand):
    _description = "Remove a compute storage."

    def configure_parser(self, parser):
        parser.add_argument(
            "name",
            metavar="name",
            help="Compute storage name",
        )

    def do_action(self, parsed_args):
        compute_storage = find_resource(self.app.vinfra.compute.storages,
                                        parsed_args.name)
        return compute_storage.delete_async()


class ShowTask(ShowOne):
    _description = "Show compute task details."

    def configure_parser(self, parser):
        parser.add_argument(
            "--task-id", required=False, default=None,
            help="Compute task ID."
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.cluster.show_task(parsed_args.task_id)


class RetryTask(ShowOne):
    _description = "Retry a failed compute task."

    def configure_parser(self, parser):
        parser.add_argument(
            "--task-id", required=False, default=None,
            help="Compute task ID."
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.cluster.retry_task(parsed_args.task_id)


class AbortTask(ShowOne):
    _description = "Abort a failed compute task."

    def configure_parser(self, parser):
        parser.add_argument(
            "--task-id", required=False, default=None,
            help="Compute task ID."
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.cluster.abort_task(parsed_args.task_id)
