from vinfraclient import exceptions
from vinfraclient.cmd.base import ShowOne
from vinfraclient.utils import get_password


class ShowSsl(ShowOne):
    _description = "Display SSL configuration."

    def do_action(self, parsed_args):
        return self.app.vinfra.ssl.get()


class SetSsl(ShowOne):
    _description = "Update the SSL certificate."

    def configure_parser(self, parser):
        ssl = parser.add_mutually_exclusive_group(required=True)
        ssl.add_argument(
            "--self-signed",
            action="store_true",
            help="Generate a new self-signed certificate."
        )
        ssl.add_argument(
            "--cert-file",
            help="Path to a file with the new certificate."
        )

        parser.add_argument(
            "--key-file",
            help="Path to a file with the private key (only used with the "
                 "--cert-file option)."
        )
        parser.add_argument(
            "--password",
            action="store_true",
            help="Read certificate password from stdin (only used with the "
                 "--cert-file option).",
        )

    @staticmethod
    def _get_stream(file_name):
        try:
            return open(file_name, mode='rb')
        except Exception as err:
            raise exceptions.ValidationError(
                'Failed to open "{}" ({}).'.format(file_name, err))

    def do_action(self, parsed_args):
        if parsed_args.key_file and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --key-file option can only be used with the --cert-file "
                "option.")
        if parsed_args.password and not parsed_args.cert_file:
            raise exceptions.ValidationError(
                "The --password option can only be used with the --cert-file "
                "option.")

        if parsed_args.self_signed:
            return self.app.vinfra.ssl.set(True, gen_cert=True)

        cert_stream = self._get_stream(parsed_args.cert_file)

        key_stream = None
        if parsed_args.key_file:
            key_stream = self._get_stream(parsed_args.key_file)

        password = None
        if parsed_args.password:
            password = get_password("Certificate password: ")
            if not password:
                raise exceptions.ValidationError('Password cannot be empty.')

        return self.app.vinfra.ssl.set(True, password=password,
                                       cert=cert_stream, key=key_stream)
