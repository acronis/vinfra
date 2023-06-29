from vinfraclient import argtypes
from vinfraclient import utils
from vinfraclient.cmd import base


def _common_set_options(parser):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="Volume description"
    )
    parser.add_argument(
        "--network-install",
        metavar="<network_install>",
        type=argtypes.boolean,
        help="Perform network install ('true' or 'false')."
    )


def _volume_arg(parser):
    parser.add_argument(
        "volume",
        metavar="<volume>",
        help="Volume ID or name"
    )


def _storage_policy_arg(parser, required=False):
    parser.add_argument(
        "--storage-policy",
        metavar="<storage_policy>",
        required=required,
        help="Storage policy ID or name"
    )


def _size_arg(parser, required=False):
    parser.add_argument(
        "--size",
        metavar="<size-gb>",
        type=int,
        required=required,
        help="Volume size, in gigabytes"
    )


def _get_storage_policy_name(vinfra, args, kwargs):
    if not args.storage_policy:
        return kwargs

    # API requires storage policy name (not storage policy ID)
    s_policy = utils.find_resource(vinfra.compute.storage_policies,
                                   args.storage_policy)
    kwargs['storage_policy_name'] = s_policy.name
    return kwargs


class ListVolume(base.Lister):
    _description = "List compute volumes."
    _default_fields = ['id', 'name', 'size', 'status', 'os-vol-host-attr:host']
    _sort_keys = ['id', 'name', 'size', 'status', 'created_at']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of volumes to list. To list all volumes, '
                 'set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<volume>',
            help='List volumes after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List volumes with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators=('in', 'contains'),
            help='Show a volume with the specified ID or list volumes using '
                 'a filter.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List volumes that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List volumes that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help='List volumes with the specified status.'
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            type=int,
            help='List volumes with the specified size.'
        )
        parser.add_argument(
            '--storage-policy',
            metavar='<host>',
            help='List volumes with the specified storage policy name or ID.'
        )
        parser.add_argument(
            '--volume-type',
            metavar='<type>',
            help='List volumes with the specified type.'
        )
        parser.add_argument(
            '--sort',
            metavar='<sort>',
            help="List volumes sorted by key.\n"
                 "The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'.\n"
                 "Supported sort keys: {}".format(', '.join(self._sort_keys))
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.id:
            filters['id'] = parsed_args.id
        if parsed_args.project:
            manager = self.app.vinfra.compute.projects
            filters['project_id'] = utils.validate_resources_from_operator(
                manager, parsed_args.project)
        if parsed_args.domain:
            domain = utils.find_resource(self.app.vinfra.domains, parsed_args.domain)
            filters['domain_id'] = domain.id
        if parsed_args.status:
            filters['status'] = parsed_args.status
        if parsed_args.size:
            filters['size'] = parsed_args.size
        if parsed_args.storage_policy:
            spolicy = utils.find_resource(
                self.app.vinfra.compute.storage_policies,
                parsed_args.storage_policy)
            filters['storage_policy_id'] = spolicy.id
        if parsed_args.volume_type:
            filters['volume_type'] = parsed_args.volume_type
        if parsed_args.sort:
            filters['sort'] = parsed_args.sort
        data = self.app.vinfra.compute.volumes.list(limit=parsed_args.limit,
                                                    marker=parsed_args.marker,
                                                    filters=filters)
        return data


class ShowVolume(base.ShowOne):
    _description = "Display compute volume details."

    def configure_parser(self, parser):
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return volume


class CreateVolume(base.TaskCommand):
    _description = "Create a new compute volume."

    def configure_parser(self, parser):
        _common_set_options(parser)

        parser.add_argument(
            "--image",
            metavar="<image>",
            help="Source compute image ID or name"
        )
        parser.add_argument(
            "--snapshot",
            metavar="<snapshot>",
            help="Source compute volume snapshot ID or name"
        )
        _storage_policy_arg(parser, required=True)
        _size_arg(parser, required=True)
        parser.add_argument(
            "name",
            metavar="<volume-name>",
            help="Volume name"
        )

    def do_action(self, parsed_args):
        volume_manager = self.app.vinfra.compute.volumes
        # API requires storage policy name (not storage policy ID)
        s_policy = utils.find_resource(
            self.app.vinfra.compute.storage_policies,
            parsed_args.storage_policy)
        args = [parsed_args.size, s_policy.name]

        kwargs_names = ['name', 'description', 'network_install']
        kwargs = base.flatten_args(parsed_args, kwargs_names)

        if parsed_args.image:
            kwargs['image'] = utils.find_resource(
                self.app.vinfra.compute.images, parsed_args.image)
        if parsed_args.snapshot:
            kwargs['snapshot'] = utils.find_resource(
                self.app.vinfra.compute.volume_snapshots, parsed_args.snapshot)

        volume = volume_manager.create_async(*args, **kwargs)
        return volume


class SetVolume(base.ShowOne):
    _description = "Modify volume parameters"

    def configure_parser(self, parser):
        _common_set_options(parser)
        _storage_policy_arg(parser)
        parser.add_argument(
            "--bootable",
            metavar="<bootable>",
            type=argtypes.boolean,
            help="Make bootable ('true' or 'false')."
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the volume"
        )
        parser.add_argument(
            "--no-placements",
            dest="no_placements",
            action="store_true",
            help="Clean up placements"
        )
        _volume_arg(parser)

    def do_action(self, parsed_args):
        vinfra = self.app.vinfra

        kwargs_names = ['name', 'description', 'network_install', 'bootable', 'no_placements']
        kwargs = base.flatten_args(parsed_args, kwargs_names)
        _get_storage_policy_name(self.app.vinfra, parsed_args, kwargs)

        volume = utils.find_resource(vinfra.compute.volumes, parsed_args.volume)
        volume = volume.update(**kwargs)
        return volume


class ExtendVolume(base.TaskCommand):
    _description = "Extend a compute volume."

    def configure_parser(self, parser):
        parser.add_argument(
            "--size",
            required=True,
            metavar="<size_gb>",
            help="Size to extend to"
        )
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return volume.extend_async(parsed_args.size)


class CloneVolume(base.TaskCommand):
    _description = "Create a new compute volume from a compute volume."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            required=True,
            help="New volume name"
        )
        _size_arg(parser)
        _storage_policy_arg(parser)
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        kwargs_names = ['size']
        kwargs = base.flatten_args(parsed_args, kwargs_names)
        _get_storage_policy_name(self.app.vinfra, parsed_args, kwargs)

        return volume.clone_async(parsed_args.name, **kwargs)


class UploadToImage(base.TaskCommand):
    _description = "Create a compute image from a compute volume."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Image name"
        )
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return volume.upload_to_image_async(name=parsed_args.name)


class ResetVolumeState(base.TaskCommand):
    _description = "Reset compute volume state"

    def configure_parser(self, parser):
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return volume.reset_state_async()


class DeleteVolume(base.TaskCommand):
    _description = "Delete a compute volume."

    def configure_parser(self, parser):
        _volume_arg(parser)

    def do_action(self, parsed_args):
        volume = utils.find_resource(self.app.vinfra.compute.volumes,
                                     parsed_args.volume)
        return volume.delete_async()
