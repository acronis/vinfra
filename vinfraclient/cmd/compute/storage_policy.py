import argparse

from vinfra.api.failure_domains import available_failure_domains
from vinfra.api.compute.storage_policies import Replicas, Encoding
from vinfraclient.argtypes import parse_dict_options
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import Command, Lister, ShowOne
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import find_resource, join_options


# spec => desc
SUPPORTED_QOS_SPECS = {
    'total_iops_sec': 'Total number of I/O operations per second',
    'read_iops_sec': 'Read number of I/O operations per second',
    'write_iops_sec': 'Write number of I/O operations per second',
    'total_bytes_sec': 'Total number of bytes per second',
    'read_bytes_sec': 'Read number of bytes per second',
    'write_bytes_sec': 'Write number of bytes per second',
    'total_iops_sec_per_gb': 'Total number of I/O operations per second per GB',
    'read_iops_sec_per_gb': 'Read number of I/O operations per second per GB',
    'write_iops_sec_per_gb': 'Write number of I/O operations per second per GB',
    'total_iops_sec_per_gb_min': 'Total number of I/O operations per second per GB (min)',
    'read_iops_sec_per_gb_min': 'Read number of I/O operations per second per GB (min)',
    'write_iops_sec_per_gb_min': 'Write number of I/O operations per second per GB (min)',
    'total_bytes_sec_per_gb': 'Total number of bytes per second per GB',
    'read_bytes_sec_per_gb': 'Read number of bytes per second per GB',
    'write_bytes_sec_per_gb': 'Write number of bytes per second per GB',
    'total_bytes_sec_per_gb_min': 'Total number of bytes per second per GB (min)',
    'read_bytes_sec_per_gb_min': 'Read number of bytes per second per GB (min)',
    'write_bytes_sec_per_gb_min': 'Write number of bytes per second per GB (min)',
}


def parse_replicas(value):
    try:
        if ':' in value:
            norm, minimum = map(int, value.split(':'))
            return Replicas(norm, minimum=minimum)
        return Replicas(int(value))
    except Exception:
        raise argparse.ArgumentTypeError("unrecognized format mapping")


def parse_encoding(value):
    try:
        m, n = map(int, value.split('+'))
    except Exception:
        raise argparse.ArgumentTypeError("unrecognized format mapping")
    return Encoding(m, n)


def storage_policy_options(
        parser, required=False, use_defaults=False,
        encoding=True, replicas=True,
        failure_domain=True, qos=False,
        storage=False, params=False, prefix=''):
    if required or use_defaults:
        # use_defaults and required are mutually exclusive
        assert required != use_defaults

    parser.add_argument(
        "--{}tier".format(prefix),
        choices=['0', '1', '2', '3'],
        dest="tier",
        default=0 if use_defaults else None,
        required=required,
        help="Storage tier"
             "{}".format(" (default: %(default)s)" if use_defaults else "")
    )
    redundancy_group = parser.add_mutually_exclusive_group(required=required)
    if replicas:
        redundancy_group.add_argument(
            "--{}replicas".format(prefix),
            metavar="<norm>",
            dest="redundancy",
            type=parse_replicas,
            default='1' if use_defaults else None,
            help="Storage replication mapping in the format:\n"
                 "norm: the number of replicas to maintain;\n"
                 "{}".format("(default: %(default)s)" if use_defaults else "")
        )
    if encoding:
        redundancy_group.add_argument(
            "--{}encoding".format(prefix),
            metavar="<M>+<N>",
            dest="redundancy",
            type=parse_encoding,
            default='1+0' if use_defaults else None,
            help="Storage erasure encoding mapping in the format:\n"
                 "M: the number of data blocks;\n"
                 "N: the number of parity blocks."
        )
    if failure_domain:
        failure_domain_types = available_failure_domains()
        parser.add_argument(
            "--{}failure-domain".format(prefix),
            choices=failure_domain_types,
            dest="failure_domain",
            required=required,
            default=failure_domain_types[0] if use_defaults else None,
            help="Storage failure domain"
                 "{}".format(" (default: %(default)s)" if use_defaults else "")
        )

    if qos:
        for spec, desc in SUPPORTED_QOS_SPECS.items():
            arg = '--' + spec.replace('_', '-')
            parser.add_argument(
                arg,
                required=False,
                type=int,
                metavar='<limit>',
                help=desc
            )

    if storage:
        parser.add_argument(
            "--storage",
            metavar="<storage-name>",
            help="Compute storage name",
        )

    if params:
        parser.add_argument(
            "--params",
            metavar="<param=value>[,<param2=value2>] [--params <param3=value3>] ...",
            action='append',
            type=parse_dict_options,
            help="Custom parameters",
        )


def _prepare_qos_specs(parsed_args, sp_obj=None):
    new_qos_specs = {}
    current_qos_specs = getattr(sp_obj, 'qos', {})

    for qos_spec_attr in SUPPORTED_QOS_SPECS:
        val = getattr(parsed_args, qos_spec_attr)

        if val is None:
            if qos_spec_attr in current_qos_specs:
                new_qos_specs[qos_spec_attr] = current_qos_specs[qos_spec_attr]
            continue

        new_qos_specs[qos_spec_attr] = val

    return new_qos_specs


def _storage_policy_arg(parser):
    parser.add_argument(
        "storage_policy",
        metavar="<storage-policy>",
        help="Storage policy ID or name"
    )


class RedundancyColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        redundancy = self._value
        if redundancy is not None:
            params = redundancy['params']
            if not params:  # in case of self service 'params' are not set
                return redundancy['type']

            if redundancy['type'] == 'replicas':
                if params['min'] is not None:
                    return 'replicas={}:{}'.format(params['norm'],
                                                   params['min'])
                return 'replicas={}'.format(params['norm'])
            elif redundancy['type'] == 'encoding':
                return 'encoding={}+{}'.format(params['M'], params['N'])
        return super(RedundancyColumn, self).human_readable()


class ListStoragePolicy(Lister):
    _description = "List existing storage policies."
    _default_fields = ['id', 'name', 'tier', 'redundancy', 'failure_domain', 'qos']
    _formatters = {'redundancy': RedundancyColumn}

    def do_action(self, parsed_args):
        data = self.app.vinfra.compute.storage_policies.list()
        return data


class ShowStoragePolicy(ShowOne):
    _description = "Show details of a storage policy."
    _formatters = {'redundancy': RedundancyColumn}

    def configure_parser(self, parser):
        _storage_policy_arg(parser)

    def do_action(self, parsed_args):
        return find_resource(self.app.vinfra.compute.storage_policies,
                             parsed_args.storage_policy)


class CreateStoragePolicy(ShowOne):
    _description = "Create a new storage policy."
    _formatters = {'redundancy': RedundancyColumn}

    def configure_parser(self, parser):
        storage_policy_options(parser, required=False, qos=True, storage=True,
                               params=True)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Storage policy name"
        )

    def do_action(self, parsed_args):
        args = [parsed_args.name, parsed_args.tier, parsed_args.redundancy,
                parsed_args.failure_domain]
        qos_specs = _prepare_qos_specs(parsed_args)

        params = join_options(parsed_args.params) or {}
        return self.app.vinfra.compute.storage_policies.create(
            *args, qos=qos_specs, storage=parsed_args.storage,
            params=params)


class SetStoragePolicy(ShowOne):
    _description = "Modify storage policy parameters."
    _formatters = {'redundancy': RedundancyColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the storage policy"
        )
        storage_policy_options(parser, required=False, qos=True, storage=True,
                               params=True)
        parser.add_argument(
            "--unset-params",
            metavar="<params>",
            type=parse_list_options,
            help="A comma-separated list of parameters to unset"
        )
        _storage_policy_arg(parser)

    def do_action(self, parsed_args):
        # storage policy can't be updated partially
        s_policy = find_resource(self.app.vinfra.compute.storage_policies,
                                 parsed_args.storage_policy)

        def get(attr):
            return getattr(parsed_args, attr) or getattr(s_policy, attr)

        args = map(get, ['name', 'tier', 'redundancy', 'failure_domain'])
        qos_specs = _prepare_qos_specs(parsed_args, sp_obj=s_policy)
        return s_policy.update(
            *args, qos=qos_specs, storage=parsed_args.storage,
            params=join_options(parsed_args.params, parsed_args.unset_params))


class DeleteStoragePolicy(Command):
    _description = "Remove an existing storage policy."

    def configure_parser(self, parser):
        _storage_policy_arg(parser)

    def do_action(self, parsed_args):
        s_policy = find_resource(self.app.vinfra.compute.storage_policies,
                                 parsed_args.storage_policy)
        return s_policy.delete()
