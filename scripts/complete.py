from cliff.complete import CompleteCommand

from vinfraclient.main import VinfraApp


if __name__ == '__main__':
    app = VinfraApp()
    app.NAME = 'vinfra'
    cmd = CompleteCommand(app, None)
    cmd.take_action(cmd.get_parser(None).parse_args([]))
