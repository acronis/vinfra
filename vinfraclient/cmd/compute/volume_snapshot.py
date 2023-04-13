from vinfraclient.cmd.base import Lister, ShowOne, TaskCommand
from vinfraclient.utils import find_resource


def _common_set_options(parser):
    parser.add_argument(
        "--description",
        metavar="<description>",
        help="Volume snapshot description"
    )


def _volume_snapshot_arg(parser):
    parser.add_argument(
        "volume_snapshot",
        metavar="<volume-snapshot>",
        help="Volume snapshot ID or name"
    )


def _volume_arg(parser, required=False):
    parser.add_argument(
        "--volume",
        metavar="<volume>",
        required=required,
        help="Volume ID or name"
    )


class ListVolumeSnapshot(Lister):
    _description = "List compute volume snapshots."
    _default_fields = ['id', 'name', 'status', 'volume_id']

    def configure_parser(self, parser):
        _volume_arg(parser)

    def do_action(self, parsed_args):
        if parsed_args.volume:
            vol_id = find_resource(self.app.vinfra.compute.volumes,
                                   parsed_args.volume).id
            return self.app.vinfra.compute.volume_snapshots.list(vol_id)
        return self.app.vinfra.compute.volume_snapshots.list()


class ShowVolumeSnapshot(ShowOne):
    _description = "Show details of a compute volume snapshot."

    def configure_parser(self, parser):
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        volume_snapshot = find_resource(
            self.app.vinfra.compute.volume_snapshots,
            parsed_args.volume_snapshot
        )
        return volume_snapshot


class CreateVolumeSnapshot(TaskCommand):
    _description = "Create a new compute volume snapshot."

    def configure_parser(self, parser):
        _common_set_options(parser)
        _volume_arg(parser, required=True)

        parser.add_argument(
            "name",
            metavar="<volume-snapshot-name>",
            help="Volume snapshot name"
        )

    def do_action(self, parsed_args):
        volume_snapshot_manager = self.app.vinfra.compute.volume_snapshots
        volume = find_resource(
            self.app.vinfra.compute.volumes, parsed_args.volume
        )
        volume_snapshot = volume_snapshot_manager.create_async(
            volume.id,
            name=parsed_args.name,
            description=parsed_args.description
        )
        return volume_snapshot


class SetVolumeSnapshot(ShowOne):
    _description = "Modify a volume snapshot."

    def configure_parser(self, parser):
        _common_set_options(parser)
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="A new name for the volume snapshot"
        )
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        vinfra = self.app.vinfra
        volume_snapshot = find_resource(
            vinfra.compute.volume_snapshots, parsed_args.volume_snapshot
        )
        volume_snapshot = volume_snapshot.update(
            name=parsed_args.name,
            description=parsed_args.description
        )
        return volume_snapshot


class UploadToImage(TaskCommand):
    _description = "Create a compute image from a compute volume snapshot."

    def configure_parser(self, parser):
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Image name"
        )
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        volume_snapshot = find_resource(
            self.app.vinfra.compute.volume_snapshots,
            parsed_args.volume_snapshot
        )
        return volume_snapshot.upload_to_image_async(name=parsed_args.name)


class ResetVolumeSnapshotState(TaskCommand):
    _description = "Reset the state of a compute volume snapshot."

    def configure_parser(self, parser):
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        volume_snapshot = find_resource(
            self.app.vinfra.compute.volume_snapshots,
            parsed_args.volume_snapshot
        )
        return volume_snapshot.reset_state_async()


class RevertToSnapshot(TaskCommand):
    _description = "Revert a compute volume to a snapshot."

    def configure_parser(self, parser):
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        volume_snapshot = find_resource(
            self.app.vinfra.compute.volume_snapshots,
            parsed_args.volume_snapshot
        )
        return volume_snapshot.revert_to_snapshot()


class DeleteVolumeSnapshot(TaskCommand):
    _description = "Delete a compute volume snapshot."

    def configure_parser(self, parser):
        _volume_snapshot_arg(parser)

    def do_action(self, parsed_args):
        volume_snapshot = find_resource(
            self.app.vinfra.compute.volume_snapshots,
            parsed_args.volume_snapshot
        )
        return volume_snapshot.delete_async()
