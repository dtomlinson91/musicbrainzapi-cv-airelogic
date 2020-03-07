from typing import Union

import click

from musicbrainzapi.cli.cli import pass_environment
from musicbrainzapi.api.command_builders import lyrics


# @click.argument('path', required=False, type=click.Path(resolve_path=True))
# @click.command(short_help='a test command')


@click.option('--dev', is_flag=True)
@click.option(
    '--save-output',
    required=False,
    help='Save the output to json files locally. Will use the path parameter if'
    ' provided else defaults to current working directory.',
    is_flag=True,
    default=False
)
@click.option(
    '--show-summary',
    required=False,
    help='Show summary statistics for the artist.',
    type=click.Choice(['album', 'year', 'all']),
)
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
    help='Artist/Group to search.',
)
@click.command()
@pass_environment
def cli(
    ctx,
    artist: str,
    country: Union[str, None],
    dev: bool,
    show_summary: str,
    save_output: bool
) -> None:
    """Search for lyrics statistics of an Artist/Group."""
    # lyrics_obj = list()
    director = lyrics.LyricsClickDirector()
    builder = lyrics.LyricsBuilder()
    director.builder = builder
    if dev:
        director._dev()
        raise (SystemExit)

    # build the Lyrics object
    director._get_initial_artists(artist, country)
    director._confirm_final_artist()
    director._query_for_data()
    director._get_lyrics()
    director._calculate_basic_statistics()
    if show_summary is not None:
        director._calculate_descriptive_statistics()
    
    # Get the Lyrics object
    lyrics_0 = director.builder.product
    # lyrics_obj.append(lyrics_0)

    # Show basic count
    lyrics_0.show_summary()
    # Show summary statistics
    if show_summary == 'all':
        lyrics_0.show_summary_statistics(group_by='album')
        lyrics_0.show_summary_statistics(group_by='year')
    elif show_summary in ['album', 'year']:
        lyrics_0.show_summary_statistics(group_by=show_summary)
