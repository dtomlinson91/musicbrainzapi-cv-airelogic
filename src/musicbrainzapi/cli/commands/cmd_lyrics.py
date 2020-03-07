import json
from typing import Union

import click

import matplotlib.pyplot as plt

from musicbrainzapi.cli.cli import pass_environment

import musicbrainzapi.wordcloud
from musicbrainzapi.api.lyrics.builder import LyricsBuilder
from musicbrainzapi.api.lyrics.director import LyricsClickDirector


@click.option('--dev', is_flag=True, help='Development flag. Do not use.')
@click.option(
    '--save-output',
    required=False,
    help='Save the output to json files locally. Will use the path parameter'
    ' if provided else defaults to current working directory.',
    is_flag=True,
    default=False,
)
@click.option(
    '--wordcloud',
    required=False,
    help='Generate a wordcloud from lyrics.',
    is_flag=True,
    default=False,
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
    wordcloud: bool,
    save_output: bool,
) -> None:
    """Search for lyrics statistics of an Artist/Group.
    
    Parameters
    ----------
    ctx : musicbrainzapi.cli.cli.Environment
        click environment class
    artist : str
        artist
    country : Union[str, None]
        country
    dev : bool
        dev flag - not to be used
    show_summary : str
        summary flag - used to display descriptive statistics
    wordcloud : bool
        wordcloud flag - used to create a wordcloud from lyrics
    save_output : bool
        save output flag - used to save output locally to disk
    """
    director = LyricsClickDirector()
    builder = LyricsBuilder()
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

    # Show wordcloud
    if wordcloud:
        click.echo('Generating wordcloud')
        cloud = musicbrainzapi.wordcloud.LyricsWordcloud.use_microphone(
            lyrics_0.all_albums_lyrics_count
        )
        cloud.create_word_cloud()
        show = click.confirm(
            'Wordcloud ready - press enter to show.', default=True
        )
        plt.imshow(
            cloud.wc.recolor(
                color_func=cloud.generate_grey_colours, random_state=3
            ),
            interpolation='bilinear',
        )
        plt.axis('off')
        if show:
            plt.show()
    if save_output:
        click.echo(f'Saving output to {ctx.path}')
        path = ctx.path if ctx.path[-1] == '/' else ctx.path + '/'
        attr = lyrics_0._attributes
        for a in attr:
            with open(f'{path}{a}.json', 'w') as f:
                json.dump(getattr(lyrics_0, a), f, indent=2)
