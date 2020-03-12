import os
from importlib import import_module

import click

from musicbrainzapi.__version__ import __version__
from musicbrainzapi.__header__ import __header__

# pylint:disable=invalid-name

CONTEXT_SETTINGS = dict(auto_envvar_prefix="COMPLEX")


class Environment:
    """Environment class to house shared parameters between all subcommands."""

    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()


pass_environment = click.make_pass_decorator(
    Environment, ensure=True
)
cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "commands")
)


class ComplexCLI(click.MultiCommand):
    """Access and run subcommands."""

    def list_commands(self, ctx):
        """List all subcommands."""
        rv = [
            filename[4:-3]
            for filename in os.listdir(cmd_folder)
            if filename.endswith(".py") and filename.startswith("cmd_")
        ]
        rv.sort()
        return rv

    def get_command(self, ctx, cmd_name):
        """Get chosen subcummands."""
        mod = import_module(f"musicbrainzapi.cli.commands.cmd_{cmd_name}")
        return getattr(mod, cmd_name)


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, writable=True),
    help="Local path to save any output files.",
    default=os.getcwd(),
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.version_option(
    version=__version__,
    prog_name=__header__,
    message=f"{__header__} version {__version__} 🎤",
)
@pass_environment
def cli(ctx, verbose, path):
    """Display base command for the musicbrainzapi program."""
    ctx.verbose = verbose
    if path is not None:
        click.echo(f"Path set to {os.path.expanduser(path)}")
        ctx.path = os.path.expanduser(path)
