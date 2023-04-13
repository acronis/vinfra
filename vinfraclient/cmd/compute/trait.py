from vinfraclient import utils
from vinfraclient.argtypes import parse_list_options
from vinfraclient.cmd.base import Command, Lister, ShowOne


class ListTrait(Lister):
    _description = "List compute placements."
    _default_fields = [
        'id', 'name', 'description', 'nodes',
        'images', 'servers', 'flavors', 'isolated'
    ]

    def do_action(self, parsed_args):
        data = self.app.vinfra.compute.traits.list()
        return data


class ShowTrait(ShowOne):
    _description = "Display compute placement details."

    def configure_parser(self, parser):
        parser.add_argument(
            "placement",
            metavar="<placement>",
            help="Placement ID or name"
        )

    def do_action(self, parsed_args):
        trait = utils.find_resource(
            self.app.vinfra.compute.traits, parsed_args.placement
        )
        return trait


class CreateTrait(ShowOne):
    _description = "Create a new compute placement."

    def configure_parser(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--isolated",
            action="store_true",
            help="Create isolated placement (hard policy, default)"
        )
        group.add_argument(
            "--non-isolated",
            action="store_true",
            help="Create non-isolated placement (soft policy)"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Placement description"
        )
        parser.add_argument(
            "--nodes",
            type=parse_list_options,
            metavar="<nodes>",
            help="A comma-separated list of compute node hosts or IDs to "
                 "assign to a compute placement"
        )
        parser.add_argument(
            "--images",
            type=parse_list_options,
            metavar="<images>",
            help="A comma-separated list of image names or IDs to assign to a "
                 "compute placement"
        )
        parser.add_argument(
            "--flavors",
            type=parse_list_options,
            metavar="<flavors>",
            help="A comma-separated list of flavor names or IDs to assign to a "
                 "compute placement"
        )
        parser.add_argument(
            "name",
            metavar="<placement-name>",
            help="Placement name"
        )

    def do_action(self, parsed_args):
        if parsed_args.images:
            parsed_args.images = (
                utils.find_resources(self.app.vinfra.compute.images,
                                     parsed_args.images))
        if parsed_args.nodes:
            parsed_args.nodes = (
                utils.find_resources(self.app.vinfra.compute.nodes,
                                     parsed_args.nodes))
        if parsed_args.flavors:
            parsed_args.flavors = (
                utils.find_resources(self.app.vinfra.compute.flavors,
                                     parsed_args.flavors))

        if parsed_args.isolated:
            isolated = True
        elif parsed_args.non_isolated:
            isolated = False
        else:
            isolated = None

        trait = self.app.vinfra.compute.traits.create(
            parsed_args.name, description=parsed_args.description,
            nodes=parsed_args.nodes, images=parsed_args.images,
            flavors=parsed_args.flavors, isolated=isolated)

        return trait


class DeleteTrait(Command):
    _description = "Delete a compute placement."

    def configure_parser(self, parser):
        parser.add_argument(
            "placement",
            metavar="<placement>",
            help="Placement ID or name"
        )

    def do_action(self, parsed_args):
        trait = utils.find_resource(self.app.vinfra.compute.traits,
                                    parsed_args.placement)
        return trait.delete()


class UpdateTrait(ShowOne):
    _description = "Update a compute placement."

    def configure_parser(self, parser):
        parser.add_argument(
            "placement",
            metavar="<placement>",
            help="Placement ID or name"
        )
        parser.add_argument(
            "--name",
            metavar="<placement-name>",
            help="A new name for the placement"
        )
        parser.add_argument(
            "--description",
            metavar="<placement-description>",
            help="A new description for the placement"
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--non-isolated",
            action="store_true",
            help="Make placement non-isolated (soft policy)"
        )
        group.add_argument(
            "--isolated",
            action="store_true",
            help="Make placement isolated (hard policy)"
        )

    def do_action(self, parsed_args):
        trait = utils.find_resource(self.app.vinfra.compute.traits,
                                    parsed_args.placement)

        if parsed_args.isolated:
            isolated = True
        elif parsed_args.non_isolated:
            isolated = False
        else:
            isolated = None

        return trait.update(
            name=parsed_args.name,
            description=parsed_args.description,
            isolated=isolated
        )


class AssignTrait(Command):
    _description = 'Assign images and nodes to a compute placement.'

    def configure_parser(self, parser):
        parser.add_argument(
            "placement",
            metavar="<placement>",
            help="Placement ID or name"
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--images",
            type=parse_list_options,
            metavar="<images>",
            help="A comma-separated list of image names or IDs to assign to a "
                 "compute placement"
        )
        group.add_argument(
            "--nodes",
            type=parse_list_options,
            metavar="<nodes>",
            help="A comma-separated list of compute node hosts or IDs to "
                 "assign to a compute placement"
        )
        group.add_argument(
            "--flavors",
            type=parse_list_options,
            metavar="<flavors>",
            help="A comma-separated list of flavor names or IDs to assign to a "
                 "compute placement"
        )

    def do_action(self, parsed_args):
        trait = utils.find_resource(self.app.vinfra.compute.traits,
                                    parsed_args.placement)

        if parsed_args.images:
            images = utils.find_resources(self.app.vinfra.compute.images,
                                          parsed_args.images)
            return trait.assign('images', images)
        elif parsed_args.nodes:
            nodes = utils.find_resources(self.app.vinfra.nodes,
                                         parsed_args.nodes)
            return trait.assign('nodes', nodes)
        elif parsed_args.flavors:
            flavors = utils.find_resources(self.app.vinfra.compute.flavors,
                                           parsed_args.flavors)
            return trait.assign('flavors', flavors)


class DeleteAssignTrait(Command):
    _description = 'Remove images and nodes from a compute placement.'

    def configure_parser(self, parser):
        parser.add_argument(
            "placement",
            metavar="<placement>",
            help="Placement ID or name"
        )

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--image",
            metavar="<image>",
            help="An image name or ID to remove from a compute placement"
        )
        group.add_argument(
            "--node",
            metavar="<node>",
            help="A compute node host or ID to remove from a compute placement"
        )
        group.add_argument(
            "--flavor",
            metavar="<flavor>",
            help="A flavor name or ID to remove from a compute placement"
        )

    def do_action(self, parsed_args):
        trait = utils.find_resource(self.app.vinfra.compute.traits,
                                    parsed_args.placement)

        if parsed_args.image:
            image = utils.find_resource(self.app.vinfra.compute.images,
                                        parsed_args.image)
            return trait.delete_assign('images', image)
        elif parsed_args.node:
            node = utils.find_resource(self.app.vinfra.nodes,
                                       parsed_args.node)
            return trait.delete_assign('nodes', node)
        elif parsed_args.flavor:
            flavor = utils.find_resource(self.app.vinfra.compute.flavors,
                                         parsed_args.flavor)
            return trait.delete_assign('flavors', flavor)
