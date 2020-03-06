from typing import Union

import click

from musicbrainzapi.cli.cli import pass_environment
from musicbrainzapi.api.command_builders import lyrics


# @click.argument('path', required=False, type=click.Path(resolve_path=True))
# @click.command(short_help='a test command')
@click.option(
    '--country',
    '-c',
    default=None,
    required=False,
    multiple=False,
    type=str,
    help='ISO A-2 Country code (https://en.wikipedia.org/wiki/ISO_3166-1_alpha'
    '-2) Example: GB',
)
@click.option(
    '--artist',
    '-a',
    required=True,
    multiple=True,
    type=str,
    help='Artist/Group to search lyrics for.',
)
@click.option(
    '--save-lyrics', required=False, is_flag=True, help='Save the lyrics '
)
@click.command()
@pass_environment
def cli(ctx, artist: str, country: Union[str, None], save_lyrics) -> None:
    """
    Search for lyrics of an Artist/Group.
    """
    print(f'save_lyrics={save_lyrics}')
    director = lyrics.LyricsClickDirector()
    builder = lyrics.LyricsBuilder()
    director.builder = builder
    director._get_initial_artists(artist, country)
    director._confirm_final_artist()
    director._query_for_data()
    director._get_lyrics()
