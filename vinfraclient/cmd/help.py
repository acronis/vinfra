import sys

from cliff import help  # pylint: disable=redefined-builtin


class HelpCommand(help.HelpCommand):
    client_required = False
    auth_required = False

    def take_action(self, parsed_args):
        try:
            return super(HelpCommand, self).take_action(parsed_args)
        except ValueError:
            if not parsed_args.cmd:
                raise

            cmds = []
            for arg in parsed_args.cmd:
                if arg.startswith('-'):
                    break
                cmds.append(arg)

            msg = "Unknown command '{}'".format(' '.join(cmds))
            sys.stderr.write(msg + '\n')
            sys.exit(1)
