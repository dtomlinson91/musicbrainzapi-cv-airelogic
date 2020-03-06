import os
import sys
from importlib import import_module

import click

from musicbrainzapi.__version__ import __version__
from musicbrainzapi.__header__ import __header__

CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')


class Environment(object):
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()


pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'commands')
)


class ComplexCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = import_module(f'musicbrainzapi.cli.commands.cmd_{name}')
            # mod = __import__(
            #     'complex.commands.cmd_' + name, None, None, ['cli']
            # )
        except ImportError as e:
            print(e)
            return
        return mod.cli


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.option(
    '-p',
    '--path',
    type=click.Path(
        exists=False, file_okay=False, resolve_path=True, writable=True
    ),
    help='Path to save results.',
    default=os.path.expanduser('~/.musicbrainzapi')
)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@click.version_option(
    version=__version__,
    prog_name=__header__,
    message=f'{__header__} version {__version__} 🎤',
)
@pass_environment
def cli(ctx, verbose, path):
    """A complex command line interface."""
    ctx.verbose = verbose
    if path is not None:
        click.echo(f'Path set to {os.path.expanduser(path)}')
        ctx.path = os.path.expanduser(path)


if __name__ == '__main__':
    cli()
