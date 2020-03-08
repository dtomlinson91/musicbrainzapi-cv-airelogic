from __future__ import annotations
import json
import os

import click

from musicbrainzapi.api.lyrics.builder import LyricsBuilder
from musicbrainzapi.api.lyrics import Lyrics


class LyricsClickDirector:
    """Director for Lyrics builder.
    """

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> LyricsBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: LyricsBuilder) -> None:
        self._builder = builder

    def _get_initial_artists(self, artist: str, country: str) -> None:
        """Search Musicbrainz api for an artist

        Parameters
        ----------
        artist : str
            Artist to search for
        country : str
            Country artist comes from.
        """
        self.builder.artist = artist
        self.builder.country = country
        self.builder.set_useragent()
        self.builder.find_artists()
        self.builder.sort_artists()
        self.builder.get_accuracy_scores()
        self.builder.get_top_five_results()
        return self

    def _confirm_final_artist(self) -> None:
        """Confirm the artist from the user.

        Raises
        ------
        SystemExit
            If no artist is found will cleanly quit.
        """
        artist_meta = None
        for i, j in self.builder._top_five_results.items():
            artist_meta = 'Multiple' if j <= 100 else None

        if artist_meta == 'Multiple':
            _position = []
            click.echo(
                click.style(
                    f'Musicbrainz found several results for '
                    f'{self.builder.artist[0]}. Which artist/group do you want'
                    '?',
                    fg='green',
                )
            )
            for i, j in zip(self.builder._top_five_results, range(1, 6)):
                click.echo(
                    f'[{j}] {self.builder._sort_names.get(i)}'
                    f' ({self.builder._accuracy_scores.get(i)}% match)'
                )
                _position.append(i)
            chosen = int(
                click.prompt(
                    click.style(f'Enter choice, default is', blink=True),
                    default=1,
                    type=click.IntRange(
                        1, len(self.builder._top_five_results)
                    ),
                )
            )
            choice = _position[chosen - 1]
            click.echo(f'You chose {self.builder._sort_names.get(choice)}')
            self._artist = self.builder._sort_names.get(choice).split('|')[0]
            self._artist_id = choice

            # Set artist and artistID on builder + product
            self.builder.artist_id = self._artist_id
            self.builder.artist = self._artist

        elif artist_meta is None:
            click.echo(
                f'Musicbrainz did not find any results for '
                f'{self.builder.artist[0]}. Check the spelling or consider '
                'alternative names that the artist/group may go by.'
            )
            raise SystemExit()
        return self

    def _query_for_data(self) -> None:
        """Query Musicbrainz api for albums + track data.
        """
        self.builder.find_all_albums()
        self.builder.find_all_tracks()
        self.builder._product.all_albums_with_tracks = self.builder.all_albums
        return self

    def _get_lyrics(self) -> None:
        """Get Lyrics for each track
        """
        self.builder.find_lyrics_urls()
        self.builder.find_all_lyrics()
        self.builder._product.all_albums_with_lyrics = (
            self.builder.all_albums_lyrics
        )
        self.builder.count_words_in_lyrics()
        # with open(f'{os.getcwd()}/lyrics_count.json', 'w+') as file:
        #     json.dump(
        #         self.builder.all_albums_lyrics_count,
        #         file,
        #         indent=2,
        #         sort_keys=True,
        #     )
        self.builder._product.all_albums_lyrics_count = (
            self.builder.all_albums_lyrics_count
        )
        return self

    def _calculate_basic_statistics(self) -> None:
        """Calculate a basic average for all tracks.
        """
        self.builder.calculate_track_totals()
        self.builder._product.all_albums_lyrics_sum = (
            self.builder.all_albums_lyrics_sum
        )
        return self

    def _calculate_descriptive_statistics(self) -> None:
        """Calculate descriptive statistics for album and/or year.
        """
        self.builder.calculate_final_average_by_album()
        self.builder.calculate_final_average_by_year()
        self.builder._product.album_statistics = self.builder.album_statistics
        self.builder._product.year_statistics = self.builder.year_statistics
        return self

    def _dev(self) -> None:
        """Dev function - used for testing
        """
        self.builder.calculate_final_average_by_album()
        self.builder.calculate_final_average_by_year()
        self.builder._product.album_statistics = self.builder.album_statistics
        self.builder._product.year_statistics = self.builder.year_statistics
        self.builder._product.artist_id = None
        self.builder._product.artist = 'Katzenjammer'
        self.builder._product.show_summary()
        self.builder._product.show_summary_statistics(group_by='year')
        return self

    @staticmethod
    def _get_product(builder_inst: LyricsBuilder) -> Lyrics:
        """Returns the constructed Lyrics object

        Parameters
        ----------
        builder_inst : LyricsBuilder
            Builder class for Lyrics object

        Returns
        -------
        Lyrics
            Lyrics object
        """
        return builder_inst._product
