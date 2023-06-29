import base64
import hashlib
import os
import sys

from vinfraclient.cmd.base import Command, Lister, ShowOne
from vinfraclient.exceptions import ValidationError
from vinfraclient.utils import find_resource


class ListComputeSshKey(Lister):
    _description = "List compute ssh keys."
    _default_fields = ['name', 'description', 'created_at']

    def do_action(self, parsed_args):
        data = self.app.vinfra.compute.keys.list()
        return data


class ShowComputeSshKey(ShowOne):
    _description = "Display compute ssh key details."

    def configure_parser(self, parser):
        parser.add_argument(
            "key",
            metavar="<ssh-key>",
            help="SSH key name."
        )

    def do_action(self, parsed_args):
        key = find_resource(self.app.vinfra.compute.keys,
                            parsed_args.key)

        key = key.to_dict()
        public_key = key.pop('public_key').strip().split()[1]
        public_key = base64.b64decode(public_key)
        fingerprint = hashlib.md5(public_key).hexdigest()  # nosec
        key['public_key_fingerprint'] = ':'.join(
            odd + even for odd, even in zip(
                fingerprint[::2], fingerprint[1::2]
            )
        )
        return key


class CreateComputeSshKey(ShowOne):
    _description = "Create new compute ssh key."

    def configure_parser(self, parser):
        parser.add_argument(
            "--public-key",
            metavar="<public-key>",
            required=True,
            help="Public key from stdin(specify '-') or filename path"
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="SSH key description."
        )
        parser.add_argument(
            "key",
            metavar="<ssh-key>",
            help="SSH key name."
        )

    @staticmethod
    def _validate_public_key_path(public_key_normalized_path):
        if (
                not os.path.exists(public_key_normalized_path)
                and not os.path.isfile(public_key_normalized_path)
        ):
            raise ValidationError(
                "File '{}' does not exist. Please specify valid public key "
                "file".format(public_key_normalized_path)
            )
        try:
            with open(public_key_normalized_path, 'r') as _:
                public_key_value = _.read()
        except Exception:
            raise ValidationError(
                "Failed to read {} file".format(public_key_normalized_path)
            )

        return public_key_value

    def _prepare_public_key(self, parsed_args):
        if parsed_args.public_key == '-':
            if self.app.options.verbose_level:
                sys.stderr.write('Enter Public key:\n')
            return sys.stdin.readline()
        public_key_normalized_path = os.path.normpath(
            parsed_args.public_key
        )
        return self._validate_public_key_path(
            public_key_normalized_path
        )

    def do_action(self, parsed_args):
        args = [parsed_args.key]
        kwargs = {'public_key': self._prepare_public_key(parsed_args)}

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        key = self.app.vinfra.compute.keys.create(*args, **kwargs)

        key = key.to_dict()
        del key['public_key']

        return key


class DeleteComputeSshKey(Command):
    _description = "Delete compute ssh key."

    def configure_parser(self, parser):
        parser.add_argument(
            "key",
            metavar="<ssh-key>",
            help="SSH key name."
        )

    def do_action(self, parsed_args):
        key = find_resource(self.app.vinfra.compute.keys,
                            parsed_args.key)
        return key.delete()
