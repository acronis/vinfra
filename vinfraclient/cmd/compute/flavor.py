from vinfraclient.cmd.base import Command, Lister, ShowOne, flatten_args
from vinfraclient.utils import find_resource


class ListFlavor(Lister):
    _description = "List compute flavors."
    _default_fields = ['id', 'name', 'ram', 'swap', 'vcpus']

    def configure_parser(self, parser):
        parser.add_argument(
            '--placement',
            metavar='<placement>',
            action='filter',
            operators='any',
            help='List flavors added to a placement with the specified ID or '
                 'use a filter'
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.placement:
            filters['traits'] = parsed_args.placement

        data = self.app.vinfra.compute.flavors.list(filters=filters)
        return data


class ShowFlavor(ShowOne):
    _description = "Display compute  flavor details."

    def configure_parser(self, parser):
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Flavor ID or name"
        )

    def do_action(self, parsed_args):
        flavor = find_resource(self.app.vinfra.compute.flavors,
                               parsed_args.flavor)
        return flavor


class CreateFlavor(ShowOne):
    _description = "Create a new compute flavor."

    def configure_parser(self, parser):
        parser.add_argument(
            "--swap",
            type=int,
            metavar="<size-mb>",
            help="Swap space size, in megabytes"
        )
        parser.add_argument(
            "--vcpus",
            type=int,
            metavar="<vcpus>",
            required=True,
            help="Number of virtual CPUs"
        )
        parser.add_argument(
            "--ram",
            type=int,
            metavar="<size-mb>",
            required=True,
            help="Memory size, in megabytes"
        )
        parser.add_argument(
            "name",
            metavar="<flavor-name>",
            help="Flavor name"
        )

    def do_action(self, parsed_args):
        args = [parsed_args.name, parsed_args.vcpus, parsed_args.ram]
        kwargs = flatten_args(parsed_args, ['swap'])

        flavor = self.app.vinfra.compute.flavors.create(*args, **kwargs)
        return flavor


class DeleteFlavor(Command):
    _description = "Delete a compute flavor."

    def configure_parser(self, parser):
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Flavor ID or name"
        )

    def do_action(self, parsed_args):
        flavor = find_resource(self.app.vinfra.compute.flavors,
                               parsed_args.flavor)
        return flavor.delete()
