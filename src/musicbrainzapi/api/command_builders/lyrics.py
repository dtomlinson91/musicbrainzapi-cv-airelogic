from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from pprint import pprint
from typing import Union, List
import contextlib
import itertools
from progress.spinner import PieSpinner

# from pprint import pprint

import musicbrainzngs
import click
import addict

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

    @abstractstaticmethod
    def browse_releases(self) -> dict:
        pass

    @abstractstaticmethod
    def get_album_info_list(self) -> list:
        pass

    @abstractstaticmethod
    def paginate_results(self) -> list:
        pass

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def do_search_artists(self) -> None:
        pass

    @abstractmethod
    def do_sort_names(self) -> None:
        pass

    @abstractmethod
    def get_accuracy_scores(self) -> None:
        pass

    @abstractmethod
    def get_top_five_results(self) -> None:
        pass

    @abstractmethod
    def do_search_albums(self) -> None:
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
    def all_tracks(self) -> set:
        return self._all_tracks

    @all_tracks.setter
    def all_tracks(self, all_tracks: set) -> None:
        self._all_tracks = all_tracks
        self._product.all_tracks = all_tracks

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

    @staticmethod
    def browse_releases(
        artist_id: str,
        limit: int,
        release_type: list = list(),
        offset: Union[int, None] = None,
        includes: Union[List[str, None]] = list(),
    ) -> dict:
        # releases = musicbrainzngs.browse_releases(
        releases = musicbrainzngs.browse_release_groups(
            artist=artist_id,
            # track_artist=artist_id,
            limit=limit,
            release_type=release_type,
            release_status='official',
            offset=offset,
            includes=includes,
        )
        return releases

    @staticmethod
    def get_album_info_list(
        album_info_list: list, album_tracker: set, releases: addict.Dict
    ) -> list:
        for i in releases['release-list']:
            _throwaway_dict = addict.Dict()
            _throwaway_dict.album = i.title
            _throwaway_dict.year = i.date.split('-')[0]
            _throwaway_dict.tracks = [
                j.recording.title for j in i['medium-list'][0]['track-list']
            ]
            if i.title not in album_tracker:
                album_tracker.add(i.title)
                album_info_list.append(_throwaway_dict)
            else:
                pass
        return album_info_list, album_tracker

    @staticmethod
    def paginate_results(
        releases: addict.Dict, duplicated_tracks: list
    ) -> List:
        tracks = [
            j.recording.title
            for i in releases['release-list']
            for j in i['medium-list'][0]['track-list']
        ]
        for i in itertools.chain(tracks):
            duplicated_tracks.append(i)
        return duplicated_tracks

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._product = Lyrics

    def do_search_artists(self) -> None:
        self.musicbrainz_artists = musicbrainzngs.search_artists(
            artist=self.artist, country=self.country
        )
        # pprint(self.musicbrainz_artists['artist-list'])
        return self

    def do_sort_names(self) -> None:
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

    def do_search_albums(self) -> None:
        album_info_list = list()
        album_tracker = set()
        duplicated_tracks = list()
        limit, offset, page = (100, 0, 1)

        raw_releases = self.browse_releases(
            artist_id=self.artist_id,
            limit=limit,
            release_type=['album'],
            offset=offset,
            includes=['recordings'],
        )

        releases = addict.Dict(raw_releases)

        # import json
        # import os
        # with open(f'{os.getcwd()}/output.json', 'w+') as file:
        #     json.dump(releases, file, indent=4, sort_keys=True)

        # raise SystemExit

        duplicated_tracks = self.paginate_results(releases, duplicated_tracks)

        # Get album info list
        album_info_list, album_tracker = self.get_album_info_list(
            album_info_list, album_tracker, releases
        )

        bar_count = len(releases['release-list'])
        previous_bar_count = 0

        with PieSpinner(
            f'Finding all tracks in all albums for {self.artist}'
            'from Musicbrainz '
        ) as bar:
            while bar_count != previous_bar_count:
                offset += limit
                page += 1
                # Get next page
                raw_page_releases = self.browse_releases(
                    artist_id=self.artist_id,
                    limit=limit,
                    release_type=['album'],
                    offset=offset,
                    includes=['recordings'],
                )
                page_releases = addict.Dict(raw_page_releases)

                # Update list
                duplicated_tracks = self.paginate_results(
                    page_releases, duplicated_tracks
                )

                # Update album info list
                (
                    album_info_list,
                    album_tracker,
                ) = self.get_album_info_list(
                    album_info_list, album_tracker, releases
                )

                previous_bar_count = bar_count
                bar_count += len(page_releases['release-list'])
                bar.next()
            total_releases_count = bar_count

        tracks = set(duplicated_tracks)

        click.echo(
            f'Musicbrainz found {len(tracks)} unique tracks in '
            f'{total_releases_count} releases for {self.artist}'
        )

        # Set properties
        self.all_tracks = tracks
        self.all_albums_with_tracks = album_info_list
        pprint(self.all_albums_with_tracks)

        return self


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
        self.builder.do_search_artists()
        self.builder.do_sort_names()
        self.builder.get_accuracy_scores()
        self.builder.get_top_five_results()

    def _confirm_final_artist(self) -> None:
        artist_meta = None
        for i, j in self.builder._top_five_results.items():
            artist_meta = 'Multiple' if j <= 100 else None

        if artist_meta == 'Multiple':
            _position = []
            click.echo(
                f'Musicbrainz found several results for '
                f'{self.builder.artist[0]}. Which artist/group do you want?',
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
                ),
            )
            choice = _position[chosen - 1]
            click.echo(f'You chose {self.builder._sort_names.get(choice)}')
            self._artist = self.builder._sort_names.get(choice).split('|')[0]
            self._artist_id = choice

        elif artist_meta is None:
            click.echo(
                f'Musicbrainz did not find any results for '
                f'{self.builder.artist[0]}. Check the spelling or consider '
                'alternative names that the artist/group may go by.'
            )
            raise SystemExit()

    def _search_for_all_tracks(self) -> None:
        self.builder.do_search_albums()
        pprint(self.builder._product.all_tracks)
        # pprint(self.builder._product.all_albums_with_tracks)

    def _set_artist_id_on_product(self) -> None:
        self.builder.artist_id = self._artist_id
        self.builder.artist = self._artist


@dataclass
class Lyrics:
    """docstring for Lyrics"""

    __slots__ = [
        'artist_id',
        'artist',
        'country',
        'all_tracks',
        'all_albums_with_tracks',
    ]
    artist_id: str
    artist: str
    country: Union[str, None]
    all_tracks: set
    all_albums_with_tracks: list
