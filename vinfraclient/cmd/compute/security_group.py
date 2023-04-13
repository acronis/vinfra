from vinfraclient import utils
from vinfraclient.cmd import base
from vinfraclient.exceptions import ValidationError


class ListSecurityGroup(base.Lister):
    _description = "List security groups."
    _default_fields = ['id', 'name', 'description', 'project_id']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of security groups to list. '
                 'To list all security groups, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            help='List security groups after the marker.'
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            action='filter',
            operators='contains',
            help='List security groups with the specified name or use a filter.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a security group with the specified ID or list '
                 'security groups using a filter.'
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            action='filter',
            operators='in',
            help='List security groups that belong to projects with the specified names or IDs. '
                 'Can only be performed by system administrators.'
        )
        parser.add_argument(
            "--domain",
            metavar="<domain>",
            help='List security groups that belong to a domain with the specified name or ID. '
                 'Can only be performed by system administrators.'
        )

    def do_action(self, parsed_args):
        filters = {}
        if parsed_args.name:
            filters['name'] = parsed_args.name
        if parsed_args.id:
            filters['id'] = parsed_args.id
        if parsed_args.project:
            # Make sure project exists. Otherwise admin user can accidentally
            # create a SG that belongs to a non-existent project.
            manager = self.app.vinfra.compute.projects
            filters['project_id'] = utils.validate_resources_from_operator(
                manager, parsed_args.project)
        if parsed_args.domain:
            domain = utils.find_resource(self.app.vinfra.domains, parsed_args.domain)
            filters['domain_id'] = domain.id

        data = self.app.vinfra.compute.security_groups.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)
        return data


class ShowSecurityGroup(base.ShowOne):
    _description = "Display information about a security group."

    def configure_parser(self, parser):
        parser.add_argument(
            "security_group",
            metavar="<security-group>",
            help="Security group name or ID"
        )

    def do_action(self, parsed_args):
        return utils.find_resource(self.app.vinfra.compute.security_groups,
                                   parsed_args.security_group)


class CreateSecurityGroup(base.ShowOne):
    _description = "Create a security group."

    def configure_parser(self, parser):
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Security group name"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Security group description"
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.compute.security_groups.create(
            parsed_args.name, description=parsed_args.description)


class DeleteSecurityGroup(base.Command):
    _description = "Delete a security group."

    def configure_parser(self, parser):
        parser.add_argument(
            "security_group",
            metavar="<security-group>",
            help="Security group name or ID"
        )

    def do_action(self, parsed_args):
        sg = utils.find_resource(self.app.vinfra.compute.security_groups,
                                 parsed_args.security_group)

        if utils.SYSTEM_TAG not in sg.tags:
            return sg.delete()

        raise ValidationError("System security group cannot be deleted")

class SetSecurityGroup(base.ShowOne):
    _description = "Modify a security group."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            help="Security group name"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Security group description"
        )
        parser.add_argument(
            "security_group",
            metavar="<security-group>",
            help="Security group name or ID"
        )

    def do_action(self, parsed_args):
        sg = utils.find_resource(self.app.vinfra.compute.security_groups,
                                 parsed_args.security_group)
        return sg.update(name=parsed_args.name,
                         description=parsed_args.description)


class ListSecurityGroupRule(base.Lister):
    _description = "List security group rules."
    _default_fields = ['id', 'security_group_id', 'direction', 'protocol',
                       'remote_ip_prefix', 'remote_group_id']

    def configure_parser(self, parser):
        parser.add_argument(
            '--limit',
            metavar='<num>',
            type=int,
            help='The maximum number of security group rules to list. '
                 'To list all security group rules, set the option to -1.'
        )
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            help='List security group rules after the marker.'
        )
        parser.add_argument(
            '--id',
            metavar='<id>',
            action='filter',
            operators='in',
            help='Show a security group rule with the specified ID or list '
                 'security group rules using a filter.'
        )
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help='List security group rules in a particular security group '
                 'specified by name or ID.'
        )

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute

        filters = {}
        if parsed_args.id:
            filters['id'] = parsed_args.name
        if parsed_args.group:
            group = utils.find_resource(compute.security_groups,
                                        parsed_args.group)
            filters['security_group_id'] = group.id

        rules = compute.security_group_rules.list(
            limit=parsed_args.limit, marker=parsed_args.marker,
            filters=filters)
        return rules


class ShowSecurityGroupRule(base.ShowOne):
    _description = "Display information about a security group rule."

    def configure_parser(self, parser):
        parser.add_argument(
            "security_group_rule",
            metavar="<security-group-rule>",
            help="Security group rule ID"
        )

    def do_action(self, parsed_args):
        manager = self.app.vinfra.compute.security_group_rules
        return utils.find_resource(manager, parsed_args.security_group_rule)


class CreateSecurityGroupRule(base.ShowOne):
    _description = "Create a security group rule."

    def configure_parser(self, parser):
        parser.add_argument(
            "--remote-group",
            metavar="<remote-group>",
            help="Remote security group name or ID"
        )
        parser.add_argument(
            "--remote-ip",
            metavar="<ip-address>",
            help="Remote IP address block in CIDR notation"
        )
        parser.add_argument(
            '--ethertype',
            metavar='<ethertype>',
            choices=['IPv4', 'IPv6'],
            help="Ethertype of network traffic: IPv4 or IPv6"
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            help="IP protocol: tcp, udp, icmp, vrrp and others"
        )
        parser.add_argument(
            '--port-range-max',
            metavar='<port-range-max>',
            type=int,
            help="The maximum port number in the port range that satisfies "
                 "the security group rule"
        )
        parser.add_argument(
            '--port-range-min',
            metavar='<port-range-min>',
            type=int,
            help="The minimum port number in the port range that satisfies "
                 "the security group rule"
        )
        # required params:
        direction_group = parser.add_mutually_exclusive_group(required=True)
        direction_group.add_argument(
            "--ingress",
            dest='direction',
            action='store_const',
            const='ingress',
            help="Rule for incoming network traffic"
        )
        direction_group.add_argument(
            "--egress",
            dest='direction',
            action='store_const',
            const='egress',
            help="Rule for outgoing network traffic"
        )
        parser.add_argument(
            "security_group",
            metavar="<security-group>",
            help="Security group name or ID to create the rule in"
        )

    def do_action(self, parsed_args):
        compute = self.app.vinfra.compute

        security_group = utils.find_resource(
            compute.security_groups, parsed_args.security_group)

        remote_group = None
        if parsed_args.remote_group:
            remote_group = utils.find_resource(
                compute.security_groups, parsed_args.remote_group)

        return compute.security_group_rules.create(
            security_group, parsed_args.direction,
            remote_group=remote_group,
            remote_ip_prefix=parsed_args.remote_ip,
            protocol=parsed_args.protocol,
            ethertype=parsed_args.ethertype,
            port_range_max=parsed_args.port_range_max,
            port_range_min=parsed_args.port_range_min)


class DeleteSecurityGroupRule(base.Command):
    _description = "Delete a security group rule."

    def configure_parser(self, parser):
        parser.add_argument(
            "security_group_rule",
            metavar="<security-group-rule>",
            help="Security group rule name or ID"
        )

    def do_action(self, parsed_args):
        manager = self.app.vinfra.compute.security_group_rules
        sg = utils.find_resource(manager, parsed_args.security_group_rule)
        return sg.delete()
