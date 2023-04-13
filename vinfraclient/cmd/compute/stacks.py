from vinfraclient import utils
from vinfraclient.cmd.base import (
    Command,
    KeyValuePair,
    Lister,
    ShowOne
)


def _add_stack_id_param(parser):
    parser.add_argument(
        "id",
        metavar="<id>",
        help="Stack identity"
    )


class CreateStack(ShowOne):

    _description = "Create a new stack."

    def configure_parser(self, parser):
        parser.add_argument(
            "template",
            metavar="<template>",
            help="Name of the template that will be used to create a stack"
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Stack name"
        )
        parser.add_argument(
            "-p", "--param",
            action=KeyValuePair,
            metavar="<parameter>",
            help="Stack template parameter in the key=value format. "
                 "Specify this option multiple times to pass multiple parameters."
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.stacks.create(
            name=parsed_args.name,
            template=parsed_args.template,
            params=parsed_args.param
        )


class DeleteStack(Command):

    _description = "Delete a stack."

    def configure_parser(self, parser):
        _add_stack_id_param(parser)

    def do_action(self, parsed_args):
        stack = utils.find_resource(self.app.vinfra.compute.stacks, parsed_args.id)
        stack.delete()


class ListStacks(Lister):

    _description = "List stacks."
    _default_fields = [
        "id",
        "stack_name",
        "stack_status"
    ]

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.stacks.list()


class ShowStack(ShowOne):

    _description = "Display stack details."

    def configure_parser(self, parser):
        _add_stack_id_param(parser)

    def do_action(self, parsed_args):
        stack = utils.find_resource(self.app.vinfra.compute.stacks, parsed_args.id)
        return self.app.vinfra.compute.stacks.get(stack)


class GetStackResources(ShowOne):

    _description = "Get resources allocated for the stack."

    def configure_parser(self, parser):
        _add_stack_id_param(parser)

    def do_action(self, parsed_args):
        stack = utils.find_resource(self.app.vinfra.compute.stacks, parsed_args.id)
        stack_resources_list = self.app.vinfra.compute.stack_resources.get_resources(stack)
        return {
            "resources": stack_resources_list
        }


class GetTemplateParameters(ShowOne):

    _description = "Get template parameters."

    def configure_parser(self, parser):
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Stack template name"
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.stack_templates.get_template_parameters(parsed_args.name)
