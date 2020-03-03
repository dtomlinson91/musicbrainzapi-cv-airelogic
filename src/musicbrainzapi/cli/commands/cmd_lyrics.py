from pprint import pprint

import click
import musicbrainzngs

from musicbrainzapi.cli.cli import pass_environment
from musicbrainzapi.api import authenticate


class LyricsInfo:
    """docstring for LyricsInfo"""

    def __init__(self, artist: str) -> None:
        authenticate.set_useragent()
        self.artist = artist
        super().__init__()

    def _search_artist(self) -> None:
        self.artists = musicbrainzngs.search_artists(artist=self.artist)
        pprint(self.artists['artist-list'])

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
            if self.chosen_artist is None:
                if j == 100:
                    self.chosen_artist = i
                    break

        # pprint(self.sort_names.get(self.chosen_artist))
        return self


class CommandUtility:
    """docstring for CommandUtility"""

    def get_multiple_options(option: tuple):
        for i in option:
            pass


@click.argument('path', required=False, type=click.Path(resolve_path=True))
@click.option('--artist', '-a', required=True, multiple=True, type=str)
@click.command(short_help='a test command')
@pass_environment
def cli(ctx, artist, path: click.Path) -> None:
    # print(artist)
    artist_0 = LyricsInfo(artist)._search_artist()
    print(f'artist_0 = {artist_0.chosen_artist}')
    if artist_0.chosen_artist is None:

        for i, j in zip(artist_0.top_five_results, range(1, 6)):
            click.echo(
                f'[{j}] {artist_0.sort_names.get(i)}'
                f' ({artist_0._accuracy_scores.get(i)}% match)'
            )

        click.prompt(
        f'We found several results for {artist[0]}, which artist/group do you   want?'
        )
        # implement this
    elif artist_0.chosen_artist == 'Null':
        click.echo(f"We didn't find any results for {artist}")
    else:
        click.confirm(
            f'Musicbrainz a perfect match for {artist[0]} with '
            f'"{artist_0.sort_names.get(artist_0.chosen_artist)}" (100% match)'
            '. Is this correct?'
        )



if __name__ == '__main__':
    LyricsInfo('Queenifie')._search_artist()
