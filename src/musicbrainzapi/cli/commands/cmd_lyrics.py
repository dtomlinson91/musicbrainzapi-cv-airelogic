from pprint import pprint

import click
import musicbrainzngs

from musicbrainzapi.cli.cli import pass_environment
from musicbrainzapi.api import authenticate
from musicbrainzapi.api.command_builders import lyrics


class LyricsInfo:
    """docstring for LyricsInfo"""

    def __init__(self, artist: str) -> None:
        authenticate.set_useragent()
        self.artist = artist
        super().__init__()

    def _search_artist(self) -> None:
        self.artists = musicbrainzngs.search_artists(artist=self.artist)
        # pprint(self.artists['artist-list'])

        if self.artists.get('artist-count') == 0:
            self.chosen_artist = 'Null'

        # Get all results

        self.sort_names = dict(
            (i.get('id'), f'{i.get("sort-name")} | {i.get("disambiguation")}')
            if i.get('disambiguation') is not None
            else (i.get('id'), f'{i.get("sort-name")}')
            for i in self.artists['artist-list']
        )

        # Get accuracy scores

        self._accuracy_scores = dict(
            (i.get('id'), int(i.get('ext:score', '0')))
            for i in self.artists['artist-list']
        )

        # pprint(self._accuracy_scores)

        # Get top 5 results

        self.top_five_results = dict(
            (i, self._accuracy_scores.get(i))
            for i in sorted(
                self._accuracy_scores,
                key=self._accuracy_scores.get,
                reverse=True,
            )[0:5]
        )

        # pprint(self.top_five_results)

        # Check for 100% match
        self.chosen_artist = None
        for i, j in self.top_five_results.items():
            self.chosen_artist = 'Multiple' if j <= 100 else None

        return self


class CommandUtility:
    """docstring for CommandUtility"""

    def get_multiple_options(option: tuple):
        for i in option:
            pass


# @click.argument('path', required=False, type=click.Path(resolve_path=True))
# @click.command(short_help='a test command')
@click.option('--artist', '-a', required=True, multiple=True, type=str)
@click.command()
@pass_environment
def cli(ctx, artist) -> None:
    director = lyrics.LyricsClickDirector()
    builder = lyrics.LyricsBuilder()
    director.builder = builder
    director._get_initial_artists(artist)
    director._confirm_final_artist()
    director._set_artist_id_on_product()


if __name__ == '__main__':
    # LyricsInfo('Queenifie')._search_artist()
    LyricsInfo('Que')._search_artist()
