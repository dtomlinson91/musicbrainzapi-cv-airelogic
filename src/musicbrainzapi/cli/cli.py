import os
import sys
from importlib import import_module

import click


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
    '--home',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help='Changes the folder to operate on.',
)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@pass_environment
def cli(ctx, verbose, home):
    """A complex command line interface."""
    ctx.verbose = verbose
    if home is not None:
        ctx.home = home

if __name__ == '__main__':
    cli()
