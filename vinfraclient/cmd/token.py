from vinfraclient.cmd.base import ShowOne


class ShowToken(ShowOne):
    _description = "Display the backend token."

    def do_action(self, parsed_args):
        return self.app.vinfra.token.get()


class CreateToken(ShowOne):
    _description = "Create the backend token."

    def configure_parser(self, parser):
        parser.add_argument(
            "--ttl",
            metavar="<ttl>",
            type=int,
            help="Token TTL, in seconds"
        )

    def do_action(self, parsed_args):
        return self.app.vinfra.token.create(ttl=parsed_args.ttl)


class ValidateToken(ShowOne):
    _description = "Validate the backend token."

    def configure_parser(self, parser):
        parser.add_argument(
            "token",
            help="Token value"
        )

    def do_action(self, parsed_args):
        status = self.app.vinfra.token.validate(parsed_args.token)
        return {'status': status}
