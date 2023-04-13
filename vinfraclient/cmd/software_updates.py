import argparse
from requests import exceptions as request_exceptions

from vinfra import api_versions
from vinfraclient import exceptions
from vinfraclient.argtypes import parse_dict_options, parse_list_options
from vinfraclient.cmd.base import ShowOne, TaskCommand
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import find_resource


class SoftwareUpdatesStatus(ShowOne):
    _description = "Show software updates status."

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.get()


def parse_maintenance_config(value):
    params = {'on-fail': 'stop', 'compute-mode': 'strict'}
    params.update(parse_dict_options(value))

    enabled = params.pop('enabled', None)
    if enabled is None:
        raise argparse.ArgumentTypeError("--maintenance 'enabled' is required")
    if enabled not in ['yes', 'no']:
        raise argparse.ArgumentTypeError(
            "Invalid argument for --maintenance 'enabled': {!r}"
            .format(enabled)
        )
    params['enabled'] = enabled == 'yes'

    on_fail = params.get('on-fail')
    if on_fail not in ('stop', 'skip', 'force'):
        raise argparse.ArgumentTypeError(
            "Invalid argument for --maintenance 'on-fail': {!r}"
            .format(on_fail)
        )

    compute_mode = params.get('compute-mode')
    if compute_mode not in ('strict', 'ignore', 'ignore_ext'):
        raise argparse.ArgumentTypeError(
            "Invalid argument for --maintenance 'compute-mode': {!r}"
            .format(compute_mode)
        )

    mapping = {
        'enabled': 'enabled',
        'on-fail': 'on_fail',
        'compute-mode': 'compute_mode',
    }

    maintenance = {}
    for k, v in params.items():
        if k not in mapping:
            raise argparse.ArgumentTypeError(
                "unrecognized argument: {}".format(k))
        maintenance[mapping[k]] = v

    return maintenance


def mode_to_maintenance(mode):
    maintenance = {}
    if mode == 'no_maintenance':
        maintenance['enabled'] = False
    else:
        maintenance['enabled'] = True
        maintenance['compute_mode'] = 'strict'
        if mode == 'stop':
            maintenance['on_fail'] = 'stop'
        elif mode == 'skip':
            maintenance['on_fail'] = 'skip'
        elif mode == 'force':
            maintenance['on_fail'] = 'force'

    return maintenance


class SoftwareUpdatesStart(TaskCommand):
    _description = "Start the software update procedure."

    def configure_parser(self, parser):
        parser.add_argument(
            '--maintenance',
            metavar="<enabled=enabled[,key1=value1,key2=value2...]>",
            dest='maintenance',
            type=parse_maintenance_config,
            default="enabled=yes,on-fail=stop,compute-mode=strict",
            help="Specify maintenance parameters:\n"
                 "enabled: enter maintenance during the upgrade "
                 "('yes' or 'no')\n"
                 "on-fail: choose how to proceed with the update if "
                 "maintenance fails ('stop', 'skip' or 'force')\n"
                 "compute-mode: choose how to proceed with the update if "
                 "a VM cannot be live migrated ('strict', 'ignore' "
                 "or 'ignore_ext')"
        )
        modes = ['stop', 'skip', 'force', 'no_maintenance']
        parser.add_argument(
            '--mode',
            choices=modes,
            help='Update mode (Deprecated): {} (default: stop)'.format(','.join(modes))
        )
        parser.add_argument(
            '--accept-eula',
            dest='accept_eula',
            action='store_true',
            default=False,
            help='Accept EULA.'
        )
        nodes = parser.add_mutually_exclusive_group()
        nodes.add_argument(
            '--nodes',
            dest='nodes',
            type=parse_list_options,
            help="A comma-separated list of node IDs or hostnames."
        )
        # --compute-only is Deprecated since 4.7.0
        nodes.add_argument(
            '--compute-only',
            dest='nodes',
            action='store_const',
            const=[],
            help=argparse.SUPPRESS
        )
        parser.add_argument(
            '--skip-control-plane',
            dest='skip_control_plane',
            action='store_true',
            default=False,
            help='Skip Control plane upgrade.'
        )

    def _validate_params(self, args):
        if (args.skip_control_plane and
                self.app.vinfra.api_version < api_versions.HCI_VER_47):
            raise ValidationError('The --skip-control-plane option can be '
                                  'used with 4.7 release or higher')

        if (args.nodes is not None and not args.nodes and
                self.app.vinfra.api_version >= api_versions.HCI_VER_47):
            raise ValidationError('The --compute-only option is deprecated.')

    def do_action(self, parsed_args):
        self._validate_params(parsed_args)

        maintenance = parsed_args.maintenance
        if parsed_args.mode:
            maintenance = mode_to_maintenance(parsed_args.mode)

        nodes = parsed_args.nodes and [find_resource(self.app.vinfra.nodes, node)
                                       for node in parsed_args.nodes]

        try:
            return self.app.vinfra.software_updates.start_async(dict(
                maintenance=maintenance,
                accept_eula=parsed_args.accept_eula,
                nodes=nodes,
                skip_control_plane=parsed_args.skip_control_plane
            ))
        except request_exceptions.HTTPError as exc:
            try:
                error = exc.response.json().get('error', {}).get('message', '')
            except Exception:
                error = ''
            if exc.response.status_code == 400 and 'EULA has not been accepted' in error:
                msg = ("EULA has not been accepted. "
                       "Read the updated "
                       "End-User License Agreement at "
                       "https://www.acronis.com/en-us/support/eula.html "
                       "and accept using --accept-eula option")
                raise exceptions.CommandError(msg)
            raise exc


class SoftwareUpdatesResume(TaskCommand):
    _description = 'Resume the software update procedure.'

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.resume_async()


class SoftwareUpdatesDownload(TaskCommand):
    _description = 'Download software updates.'

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.download_async()


class SoftwareUpdatesCheckForUpdates(TaskCommand):
    _description = 'Check for software updates.'

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.check_for_update_async()


class SoftwareUpdatesEligibilityCheck(TaskCommand):
    _description = "Check nodes' update eligibility."

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.eligibility_check_async()


class SoftwareUpdatesPause(TaskCommand):
    _description = 'Pause software updates.'

    def do_action(self, parsed_args):
        return self.app.vinfra.software_updates.pause_async()


class SoftwareUpdatesCancel(TaskCommand):
    _description = 'Cancel software updates.'

    def configure_parser(self, parser):
        maintenance_modes = ['exit', 'exit-keep-resources', 'hold']
        parser.add_argument(
            '--maintenance-mode',
            dest='maintenance_mode',
            choices=maintenance_modes,
            default='exit-keep-resources',
            help=('Maintenance mode: {} (default: exit-keep-resources)'
                  .format(','.join(maintenance_modes)))
        )

    def do_action(self, parsed_args):
        mapping = {
            'exit': 'leave',
            'exit-keep-resources': 'leave_ignore',
            'hold': 'hold',
        }
        maintenance_mode = mapping.get(parsed_args.maintenance_mode)
        return self.app.vinfra.software_updates.cancel_async(
            maintenance_mode=maintenance_mode
        )
