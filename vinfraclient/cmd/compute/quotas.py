import argparse
import collections
import logging

from vinfra import api_versions

from vinfraclient import exceptions
from vinfraclient import utils
from vinfraclient.cmd.base import ShowOne, Command

LOG = logging.getLogger(__name__)


class ShowComputeQuotas(ShowOne):
    _description = "List compute quotas."

    @classmethod
    def _flatten_dict(cls, dict_, parent_key=None):
        rv = []
        size_multiplier = {
            'storage.storage_policies.': 1,
            'compute.ram_quota.': 1,
            # the next values are deprecated starting from 4.0 release:
            'compute.ram.': 1 << 20,
            'storage.gigabytes.': 1 << 30,
        }
        for k, v in dict_.items():
            if parent_key:
                new_key = "{}.{}".format(parent_key, k)
            else:
                new_key = k

            if isinstance(v, collections.MutableMapping):
                rv.extend(cls._flatten_dict(v, new_key).items())
            else:
                for field, mul in size_multiplier.items():
                    if new_key.startswith(field) and v > 0:
                        v = utils.SizeValue(v * mul).humanize()
                rv.append((new_key, v))
        return dict(rv)

    def configure_parser(self, parser):
        parser.add_argument(
            "project_id",
            help="Project ID",
        )
        parser.add_argument(
            "--usage",
            action="store_true",
            help="Include quota usage",
        )

    @staticmethod
    def _safe_mul(val, mul):
        return val if val < 0 else int(val * mul)

    def _fixup_ram(self, data):
        compute = data.get('compute')
        if not compute:
            return

        # Starting from 3.5 release API returns ram in bytes. Report
        # compute['ram'] in MiB, compute['ram_quota'] in bytes
        mib = 1 << 20
        LOG.warning("'ram' field is deprecated, use 'ram_quota' field "
                    "instead.")
        ram = compute['ram']
        ram_quota = compute['ram_quota'] = {}

        if self.app.vinfra.api_version >= api_versions.HCI_VER_35:
            ram['limit'] = self._safe_mul(ram['limit'], 1. / mib)
        ram_quota['limit'] = self._safe_mul(ram['limit'], mib)

        if 'used' in compute['ram']:
            if self.app.vinfra.api_version >= api_versions.HCI_VER_35:
                ram['used'] = self._safe_mul(ram['used'], 1. / mib)
            ram_quota['used'] = self._safe_mul(ram['used'], mib)

    def _fixup_storage(self, data):
        storage = data.get('storage')
        if not storage:
            return

        # Starting from 4.0 release API returns storage_policies in bytes
        # instead of 'gigabytes' field. Report compute['gigabytes'] for
        # 4.0+ and 'storage_policies' for 3.5-
        gib = 1 << 30

        def get_dict(cur_dict, mul):
            rv = {}
            for sp_name, limit in cur_dict.items():
                fix_limit = {'limit': self._safe_mul(limit['limit'], mul)}
                if 'used' in limit:
                    fix_limit['used'] = self._safe_mul(limit['used'], mul)
                rv[sp_name] = fix_limit
            return rv

        LOG.warning("'gigabytes' field is deprecated, use 'storage_policies' "
                    "field instead.")
        if self.app.vinfra.api_version >= api_versions.HCI_VER_40:
            storage['gigabytes'] = (
                get_dict(storage['storage_policies'], 1. / gib))
        else:
            storage['storage_policies'] = get_dict(storage['gigabytes'], gib)

    def do_action(self, parsed_args):
        data = self.app.vinfra.compute.quotas.show(parsed_args.project_id,
                                                   usage=parsed_args.usage)
        data = data.to_dict()
        self._fixup_ram(data)
        self._fixup_storage(data)

        if parsed_args.formatter == 'table':
            return self._flatten_dict(data)

        return data


class UpdateComputeQuotas(Command):
    _description = "Update compute quotas."

    @staticmethod
    def gigabytes(value):
        rv = {}
        for storage_policy in value.split(','):
            storage_policy = storage_policy.strip()
            try:
                sp_name, sp_size = storage_policy.rsplit(':', 1)
                sp_size = int(sp_size)
            except ValueError:
                raise argparse.ArgumentTypeError('Invalid gigabytes format')

            rv[sp_name] = sp_size

        return rv

    @staticmethod
    def storage_policy(value):
        try:
            sp_name, sp_size = value.strip().rsplit(':', 1)
            sp_size = utils.SizeValue(sp_size).value
        except ValueError:
            raise argparse.ArgumentTypeError(
                'Invalid --storage-policy format')
        return sp_name, sp_size

    @staticmethod
    def ram_size(value):
        try:
            return utils.SizeValue(value.strip()).value
        except ValueError:
            raise argparse.ArgumentTypeError(
                'Invalid --ram-size format')

    @staticmethod
    def placement(value):
        rv = {}
        for placement in value.split(','):
            placement = placement.strip()
            try:
                placement_name, placement_size = placement.rsplit(':', 1)
                placement_size = int(placement_size)
            except ValueError:
                raise argparse.ArgumentTypeError('Invalid placement format')
            else:
                rv[placement_name] = {"limit": placement_size}
        return rv

    def configure_parser(self, parser):
        parser.add_argument(
            "project_id",
            help="Project ID"
        )
        parser.add_argument(
            "--cores",
            type=int,
            metavar='<cores>',
            help="Number of cores",
        )
        ram_group = parser.add_mutually_exclusive_group()
        parser.add_argument(
            "--ram",
            type=int,
            metavar='<ram>',
            help="Number of RAM, in megabytes, deprecated",
        )
        ram_group.add_argument(
            "--ram-size",
            type=self.ram_size,
            metavar='<ram>',
            help="Number of RAM",
        )
        parser.add_argument(
            "--floatingip",
            type=int,
            metavar='<floatingip>',
            help="Number of floating IP addresses",
        )
        parser.add_argument(
            "--ipsec-site-connection",
            type=int,
            metavar='<ipsec-site-connection>',
            help="Number of VPN IPsec site connections",
        )
        storage_group = parser.add_mutually_exclusive_group()
        storage_group.add_argument(
            "--gigabytes",
            type=self.gigabytes,
            help="Comma-separated list of <storage_policy>:<size>, deprecated",
        )
        storage_group.add_argument(
            "--storage-policy",
            dest="storage_policies",
            action="append",
            type=self.storage_policy,
            help="Storage policy in the format <storage_policy>:<size>. "
                 "(this option can be used multiple times).",
        )
        parser.add_argument(
            "--k8saas-cluster",
            type=int,
            metavar='<cluster>',
            help="The new value for the Kubernetes clusters quota limit",
        )
        parser.add_argument(
            "--lbaas-loadbalancer",
            type=int,
            metavar='<load_balancer>',
            help="The new value for the load balancer quota limit. The value -1"
                 " means unlimited.",
        )
        parser.add_argument(
            "--placement",
            type=self.placement,
            help="Comma-separated list of <placement_id>:<size>",
        )

    def do_action(self, parsed_args):
        if parsed_args.gigabytes:
            LOG.warning('The --gigabytes option is deprecated, use '
                        '--storage-policy option instead.')
            parsed_args.storage_policies = (
                (sp_name, sp_size << 30 if sp_size > 0 else sp_size)
                for sp_name, sp_size in parsed_args.gigabytes.items())

        ver = self.app.vinfra.api_version
        if parsed_args.ram and ver >= api_versions.HCI_VER_35:
            LOG.warning('The --ram option is deprecated, use --ram-size '
                        'instead.')
            ram = parsed_args.ram
            parsed_args.ram_size = ram << 20 if ram > 0 else ram  # Mbs -> Bytes
        elif parsed_args.ram_size and ver < api_versions.HCI_VER_40:
            raise exceptions.CommandError('The --ram-size option can be used '
                                          'with 4.0 release or higher.')

        self.app.vinfra.compute.quotas.update(
            parsed_args.project_id,
            compute_cores=parsed_args.cores,
            compute_ram=parsed_args.ram_size,
            network_floatingip=parsed_args.floatingip,
            network_ipsec_site_connection=parsed_args.ipsec_site_connection,
            k8saas_cluster=parsed_args.k8saas_cluster,
            lbaas_loadbalancer=parsed_args.lbaas_loadbalancer,
            storage_policies=parsed_args.storage_policies,
            placement=parsed_args.placement,
        )
