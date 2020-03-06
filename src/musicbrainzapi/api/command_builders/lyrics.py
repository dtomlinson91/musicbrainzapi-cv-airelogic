from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from pprint import pprint
from typing import Union, List, Dict
import html
import json
import os

import musicbrainzngs
import click
import addict
import requests

from musicbrainzapi.api import authenticate


class LyricsConcreteBuilder(ABC):
    """docstring for Lyrics"""

    @property
    @abstractmethod
    def product(self) -> None:
        pass

    @property
    @abstractmethod
    def artist(self) -> str:
        pass

    @artist.setter
    @abstractmethod
    def artist(self, artist: str) -> None:
        pass

    @property
    @abstractmethod
    def country(self) -> Union[str, None]:
        pass

    @country.setter
    @abstractmethod
    def country(self, country: Union[str, None]) -> None:
        pass

    @property
    @abstractmethod
    def artist_id(self) -> str:
        pass

    @artist_id.setter
    @abstractmethod
    def artist_id(self, artist_id: str) -> None:
        pass

    @abstractstaticmethod
    def set_useragent():
        authenticate.set_useragent()

    # @abstractstaticmethod
    # def browse_releases(self) -> dict:
    #     pass

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def find_artists(self) -> None:
        pass

    @abstractmethod
    def sort_artists(self) -> None:
        pass

    @abstractmethod
    def get_accuracy_scores(self) -> None:
        pass

    @abstractmethod
    def get_top_five_results(self) -> None:
        pass

    @abstractmethod
    def find_all_albums(self) -> None:
        pass

    @abstractmethod
    def find_all_tracks(self) -> None:
        pass


class LyricsBuilder(LyricsConcreteBuilder):
    """docstring for LyricsBuilder"""

    @property
    def product(self) -> Lyrics:
        product = self._product
        return product

    @property
    def artist(self) -> str:
        return self._artist

    @artist.setter
    def artist(self, artist: str) -> None:
        self._artist = artist
        self._product.artist = artist

    @property
    def country(self) -> Union[str, None]:
        return self._country

    @country.setter
    def country(self, country: Union[str, None]) -> None:
        self._country = country
        self._product.country = country

    @property
    def artist_id(self) -> str:
        return self._artist_id

    @artist_id.setter
    def artist_id(self, artist_id: str) -> None:
        self._artist_id = artist_id
        self._product.artist_id = artist_id

    @property
    def all_albums_with_tracks(self) -> list:
        return self._all_albums_with_tracks

    @all_albums_with_tracks.setter
    def all_albums_with_tracks(self, all_albums_with_tracks: list) -> None:
        self._all_albums_with_tracks = all_albums_with_tracks
        self._product.all_albums_with_tracks = all_albums_with_tracks

    @staticmethod
    def set_useragent() -> None:
        authenticate.set_useragent()

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._product = Lyrics

    def find_artists(self) -> None:
        self.musicbrainz_artists = musicbrainzngs.search_artists(
            artist=self.artist, country=self.country
        )
        # pprint(self.musicbrainz_artists['artist-list'])
        return self

    def sort_artists(self) -> None:
        self._sort_names = dict(
            (i.get('id'), f'{i.get("sort-name")} | {i.get("disambiguation")}')
            if i.get('disambiguation') is not None
            else (i.get('id'), f'{i.get("sort-name")}')
            for i in self.musicbrainz_artists['artist-list']
        )
        return self

    def get_accuracy_scores(self) -> None:
        self._accuracy_scores = dict(
            (i.get('id'), int(i.get('ext:score', '0')))
            for i in self.musicbrainz_artists['artist-list']
        )
        return self

    def get_top_five_results(self) -> None:
        self._top_five_results = dict(
            (i, self._accuracy_scores.get(i))
            for i in sorted(
                self._accuracy_scores,
                key=self._accuracy_scores.get,
                reverse=True,
            )[0:5]
        )
        return self

    def find_all_albums(self) -> None:
        limit, offset, page = (100, 0, 1)

        resp_0 = addict.Dict(
            musicbrainzngs.browse_release_groups(
                artist=self.artist_id, release_type=['album'], limit=limit
            )
        )

        total_releases = resp_0['release-group-count']
        response_releases = len(resp_0['release-group-list'])

        with click.progressbar(
            length=total_releases,
            label=f'Searching Musicbrainz for all albums from {self.artist}',
        ) as bar:

            release_group_ids = addict.Dict(
                (i.id, i.title)
                for i in resp_0['release-group-list']
                if i.type == 'Album'
            )

            bar.update(response_releases)

            while response_releases > 0:
                # Get next page
                offset += limit
                page += 1

                resp_1 = addict.Dict(
                    musicbrainzngs.browse_release_groups(
                        artist=self.artist_id,
                        release_type=['album'],
                        limit=limit,
                        offset=offset,
                    )
                )
                response_releases = len(resp_1['release-group-list'])

                release_group_ids = addict.Dict(
                    **release_group_ids,
                    **addict.Dict(
                        (i.id, i.title)
                        for i in resp_1['release-group-list']
                        if i.type == 'Album'
                    ),
                )
                bar.update(response_releases)

        self.release_group_ids = release_group_ids
        click.echo(f'Found {len(release_group_ids)} albums for {self.artist}.')

        del (resp_0, resp_1)
        return self

    def find_all_tracks(self) -> None:
        self.all_albums = list()
        total_albums = len(self.release_group_ids)
        self.total_track_count = 0

        with click.progressbar(
            length=total_albums,
            label=(
                'Searching Musicbrainz for all songs in all albums for '
                f'{self.artist}'
            ),
        ) as bar:
            for id, alb in self.release_group_ids.items():
                resp_0 = addict.Dict(
                    musicbrainzngs.browse_releases(
                        release_group=id,
                        release_type=['album'],
                        includes=['recordings'],
                        limit=100,
                    )
                )

                album_track_count = [
                    i['medium-list'][0]['track-count']
                    for i in resp_0['release-list']
                ]

                self.total_track_count += max(album_track_count)

                max_track_pos = album_track_count.index(max(album_track_count))

                album_tracks = resp_0['release-list'][max_track_pos]

                try:
                    album_year = resp_0['release-list'][
                        max_track_pos
                    ].date.split('-')[0]
                except TypeError:
                    album_year = 'Missing'

                album_tracks = addict.Dict(
                    (
                        alb + f' [{album_year}]',
                        [
                            i.recording.title
                            for i in resp_0['release-list'][max_track_pos][
                                'medium-list'
                            ][0]['track-list']
                        ],
                    )
                )

                self.all_albums.append(album_tracks)

                bar.update(1)

        # pprint(self.all_albums)
        click.echo(
            f'Found {self.total_track_count} songs in total across'
            f' {len(self.release_group_ids)} albums for {self.artist}'
        )
        del resp_0
        return self

    def find_lyrics_urls(self) -> None:
        self.all_albums_lyrics_url = list()
        for x in self.all_albums:
            for alb, songs in x.items():
                lyrics = addict.Dict(
                    (
                        alb,
                        [
                            self.construct_lyrics_url(self.artist, i)
                            for i in songs
                        ],
                    )
                )
                self.all_albums_lyrics_url.append(lyrics)

        # pprint(self.all_albums_lyrics_url)
        return self

    def find_all_lyrics(self) -> None:
        self.all_albums_lyrics = list()

        with click.progressbar(
            length=self.total_track_count,
            label=f'Finding lyrics for {self.total_track_count}'
            f' tracks for {self.artist}. This may take some time! ☕️',
        ) as bar:

            for x in self.all_albums_lyrics_url:
                for alb, urls in x.items():
                    for i in urls:
                        lyrics = addict.Dict(
                            (alb, [self.request_lyrics_from_url(i)])
                        )
                        self.all_albums_lyrics.append(lyrics)
                        bar.update(1)
        return self

    @staticmethod
    def construct_lyrics_url(artist: str, song: str) -> str:
        lyrics_api_base = 'https://api.lyrics.ovh/v1'
        lyrics_api_url = html.escape(f'{lyrics_api_base}/{artist}/{song}')
        return lyrics_api_url

    @staticmethod
    def request_lyrics_from_url(url: str) -> str:
        resp = requests.get(url)

        # No lyrics for a song will return a key of 'error', we pass on this.
        try:
            lyrics = resp.json()['lyrics']
            return lyrics
        except KeyError:
            return


class LyricsClickDirector:
    """docstring for LyricsClickDirector"""

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> LyricsBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: LyricsBuilder) -> None:
        self._builder = builder

    def _get_initial_artists(self, artist: str, country: str) -> None:
        self.builder.artist = artist
        self.builder.country = country
        self.builder.set_useragent()
        self.builder.find_artists()
        self.builder.sort_artists()
        self.builder.get_accuracy_scores()
        self.builder.get_top_five_results()
        return self

    def _confirm_final_artist(self) -> None:
        artist_meta = None
        for i, j in self.builder._top_five_results.items():
            artist_meta = 'Multiple' if j <= 100 else None

        if artist_meta == 'Multiple':
            _position = []
            click.echo(
                f'Musicbrainz found several results for '
                f'{self.builder.artist[0]}. Which artist/group do you want?'
            )
            for i, j in zip(self.builder._top_five_results, range(1, 6)):
                click.echo(
                    f'[{j}] {self.builder._sort_names.get(i)}'
                    f' ({self.builder._accuracy_scores.get(i)}% match)'
                )
                _position.append(i)
            chosen = int(
                click.prompt(
                    f'Enter choice, default is',
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
        self.builder.find_all_albums()
        self.builder.find_all_tracks()
        self.builder._product.all_albums_with_tracks = self.builder.all_albums
        return self

    def _get_lyrics(self) -> None:
        self.builder.find_lyrics_urls()
        self.builder.find_all_lyrics()
        self.builder._product.all_albums_with_lyrics = (
            self.builder.all_albums_lyrics
        )

        with open(f'{os.getcwd()}/lyrics.json', 'w+') as file:
            json.dump(
                self.builder.all_albums_lyrics, file, indent=4, sort_keys=True
            )


@dataclass
class Lyrics:
    """docstring for Lyrics"""

    __slots__ = [
        'artist_id',
        'artist',
        'country',
        'all_albums_with_tracks',
        'all_albums_with_lyrics',
    ]
    artist_id: str
    artist: str
    country: Union[str, None]
    all_albums_with_tracks: List[Dict[str, List[str]]]
    all_albums_with_lyrics: List[Dict[str, List[str]]]
