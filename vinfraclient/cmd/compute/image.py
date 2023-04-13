import os
import sys

import progressbar as pb

from vinfraclient import exceptions
from vinfraclient import utils
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd import base


def _image_arg(parser):
    parser.add_argument(
        "image",
        metavar="<image>",
        help="Image ID or name"
    )


def _common_set_options(parser):
    parser.add_argument(
        "--min-disk",
        type=int,
        metavar="<size-gb>",
        help=" Minimum disk size required to boot from image, in gigabytes"
    )
    parser.add_argument(
        "--min-ram",
        type=int,
        metavar="<size-mb>",
        help="Minimum RAM size required to boot from image, in megabytes"
    )
    parser.add_argument(
        "--os-distro",
        metavar="<os-distro>",
        help="OS distribution. To list available distributions, "
             "run 'vinfra service compute show'."
    )
    parser.add_argument(
        "--protected",
        dest="protected",
        action="store_true",
        default=None,
        help="Protect image from deletion."
    )
    parser.add_argument(
        "--unprotected",
        dest="protected",
        action="store_false",
        default=None,
        help="Allow image to be deleted.",
    )
    parser.add_argument(
        "--public",
        dest="visibility",
        action="store_const",
        const="public",
        default=None,
        help="Make image accessible to all users."
    )
    parser.add_argument(
        "--private",
        dest="visibility",
        action="store_const",
        const="shared",
        default=None,
        help="Make image accessible only to the owners."
    )


class ListImage(base.Lister):
    _description = "List compute images."
    _default_fields = ['id', 'name', 'size', 'status', 'disk_format']
    _sort_keys = ['id', 'name', 'status', 'created_at', 'updated_at'
                  'size', 'disk_format']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of images to list. To list all images, '
                 'set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<image>',
            help='List images after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List images with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show an image with the specified ID or list images using '
                 'a filter.'
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            action='filter',
            operators='in',
            help='List images with the specified status or use a filter.'
        )
        parser.add_argument(
            '--placement',
            metavar='<placement>',
            action='filter',
            operators='any',
            help='List images added to a placement with the specified ID or '
                 'use a filter'
        )
        parser.add_argument(
            '--disk-format',
            metavar='<disk-format>',
            help='List images with the specified disk format.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List images that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators. '
                 'Specify multiple project IDs as a comma-separated list.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List images that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            '--sort',
            metavar='<sort>',
            help="List images sorted by key.\n"
                 "The sorting format is <sort-key>:<order>. The order is 'asc' or 'desc'.\n"
                 "Supported sort keys: {}".format(', '.join(self._sort_keys))
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.id:
            filters['id'] = parsed_args.id
        if parsed_args.status:
            filters['status'] = parsed_args.status
        if parsed_args.placement:
            filters['traits'] = parsed_args.placement
        if parsed_args.disk_format:
            filters['disk_format'] = parsed_args.disk_format
        if parsed_args.project:
            manager = self.app.vinfra.compute.projects
            filters['project_id'] = utils.validate_resources_from_operator(
                manager, parsed_args.project)
        if parsed_args.domain:
            domain = utils.find_resource(self.app.vinfra.domains, parsed_args.domain)
            filters['domain_id'] = domain.id
        if parsed_args.sort:
            filters['sort'] = parsed_args.sort

        data = self.app.vinfra.compute.images.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)
        return data


class ShowImage(base.ShowOne):
    _description = "Display compute image details."

    def configure_parser(self, parser):
        _image_arg(parser)

    def do_action(self, parsed_args):
        image = utils.find_resource(self.app.vinfra.compute.images,
                                    parsed_args.image)
        return image


class CreateImage(base.TaskCommand):
    _description = "Create a new compute image."

    def configure_parser(self, parser):
        _common_set_options(parser)

        disk_formats = ['aki', 'ami', 'ari', 'detect', 'iso', 'ploop',
                        'qcow2', 'raw', 'vdi', 'vhd', 'vhdx', 'vmdk']
        container_formats = [
            'aki', 'ami', 'ari', 'bare', 'docker', 'ovf', 'ova']

        parser.add_argument(
            "--disk-format",
            type=str,
            metavar="<disk_format>",
            default="detect",
            choices=disk_formats,
            help="Disk format {} (default: detect)".format(
                ','.join(disk_formats)
            )
        )
        parser.add_argument(
            "--container-format",
            type=str,
            metavar="<format>",
            default="bare",
            choices=container_formats,
            help="Container format: {} (default: bare)".format(
                ','.join(container_formats)
            )
        )
        parser.add_argument(
            "--tags",
            metavar="<tags>",
            type=parse_list_options,
            help="A comma-separated list of tags"
        )
        parser.add_argument(
            "name",
            metavar="<image-name>",
            help="Image name"
        )
        parser.add_argument(
            "--verify",
            action='store_true',
            help="Verify the checksum of the uploaded image"
        )
        parser.add_argument(
            "--file",
            metavar="<file>",
            required=True,
            help="Create image from a local file"
        )
        parser.add_argument(
            "--uefi",
            metavar="<uefi>",
            dest='hw_firmware_type',
            action='store_const',
            const='uefi',
            default=None,
            help="Create image with UEFI."
        )

    def do_action(self, parsed_args):
        def image_create(stream, args):
            return self.app.vinfra.compute.images.create_async(
                stream, args.name, args.disk_format, args.container_format,
                min_disk=args.min_disk, min_ram=args.min_ram,
                os_distro=args.os_distro, protected=args.protected,
                visibility=args.visibility, tags=args.tags,
                verify=args.verify,
                hw_firmware_type=args.hw_firmware_type,
            )

        if parsed_args.verify and not parsed_args.wait:
            raise exceptions.ValidationError(
                'The --verify option must be used together with the --wait option')

        if parsed_args.hw_firmware_type and parsed_args.file.endswith('.iso'):
            raise exceptions.ValidationError(
                "UEFI option cannot be used with ISO images."
            )

        # NOTE(akurbatov): request to upload image can get unauthorized
        # response. Client can then try to reauth in background and repeat
        # request. But stream offset must be then reseted. Make sure user
        # passed correct login and password to not complicate logic by simple
        # backend API call:
        self.app.vinfra.get_meta()

        try:
            stream = open(parsed_args.file, mode='rb')
        except Exception as err:
            raise exceptions.ValidationError(
                'Failed to open {} ({})'.format(parsed_args.file, err))

        if (
                parsed_args.formatter != 'table'
                or not self.app.stderr.isatty()
        ):
            return image_create(stream, parsed_args)

        pattern = 'Uploading image to server [elapsed time: %s]... '
        widgets = [pb.Timer(format=pattern), pb.AnimatedMarker()]
        pbar = pb.ProgressBar(maxval=80, term_width=80, widgets=widgets,
                              fd=self.app.stderr)
        with utils.progress_bar_context(self.app, pbar):
            return image_create(stream, parsed_args)


class DeleteImage(base.Command):
    _description = "Delete a compute image."

    def configure_parser(self, parser):
        _image_arg(parser)

    def do_action(self, parsed_args):
        image = utils.find_resource(self.app.vinfra.compute.images,
                                    parsed_args.image)
        return image.delete()


class SetImage(base.ShowOne):
    _description = "Modify compute image parameters."

    def configure_parser(self, parser):
        _common_set_options(parser)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Image name"
        )
        _image_arg(parser)

    def do_action(self, parsed_args):
        image = utils.find_resource(self.app.vinfra.compute.images,
                                    parsed_args.image)
        return image.update(
            name=parsed_args.name, min_disk=parsed_args.min_disk,
            min_ram=parsed_args.min_ram, os_distro=parsed_args.os_distro,
            protected=parsed_args.protected, visibility=parsed_args.visibility)


class SaveImage(base.Command):
    _description = "Download a compute image."

    def configure_parser(self, parser):
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="File to save the image to (default: stdout)"
        )
        _image_arg(parser)

    def do_action(self, parsed_args):
        image = utils.find_resource(self.app.vinfra.compute.images,
                                    parsed_args.image)
        fdst = None
        if not parsed_args.file:
            fdst = sys.stdout
        else:
            if os.path.exists(parsed_args.file):
                raise exceptions.ValidationError(
                    'File "{}" exists'.format(parsed_args.file))
            fdst = open(parsed_args.file, 'wb')

        image.download(fdst)
