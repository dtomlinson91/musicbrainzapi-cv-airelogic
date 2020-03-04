from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from pprint import pprint
from typing import Union
import contextlib

# from pprint import pprint

import musicbrainzngs
import click

from musicbrainzapi.api import authenticate


class LyricsConcreteBuilder(ABC):
    """docstring for Lyrics"""

    @abstractstaticmethod
    def set_useragent():
        authenticate.set_useragent()

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


class LyricsBuilder(LyricsConcreteBuilder):
    """docstring for LyricsBuilder"""

    @staticmethod
    def set_useragent() -> None:
        authenticate.set_useragent()

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

    @staticmethod
    def browse_releases(
        artist_id: str,
        limit: int,
        release_type: list,
        offset: Union[int, None] = None,
    ) -> dict:
        releases = musicbrainzngs.browse_releases(
            artist=artist_id,
            limit=limit,
            release_type=release_type,
            offset=offset,
            includes=['recordings'],
        )
        return releases

    @staticmethod
    def browse_recordings(
        release: str, limit: int, offset: Union[int, None]
    ) -> dict:
        recordings = musicbrainzngs.browse_recordings(
            release=release, limit=limit, offset=offset
        )
        return recordings

    def do_search_albumns(self) -> None:
        limit = 100
        offset = 0
        page = 1
        self.releases_list = list()
        releases = self.browse_releases(self.artist_id, limit, ['album'])
        total_releases_count = releases['release-count']
        page_releases_list = releases['release-list']
        self.releases_list += page_releases_list
        with click.progressbar(
            length=total_releases_count - limit,
            label='Finding all albumns from Musicbrainz',
        ) as bar:
            while len(self.releases_list) < total_releases_count:
                offset += limit
                page += 1
                page_releases = self.browse_releases(
                    self.artist_id, limit, ['album'], offset
                )
                page_releases_list = page_releases['release-list']
                self.releases_list += page_releases_list
                bar.update(limit)
        click.echo(f'Found {total_releases_count} albums for {self.artist}')
        return self

    def do_filter_albums_official(self) -> None:
        # Get official albums only
        _official_albums_list = list()
        for i in self.releases_list:
            with contextlib.suppress(KeyError):
                if i['status'] == 'Official':
                    _official_albums_list.append(i)
        self.official_albums = dict(
            (i['id'], i['title']) for i in _official_albums_list
        )
        # pprint(self.official_albums)
        return self

    def do_search_album_tracks(self) -> None:
        # No album is over 100 tracks so we don't need to iterate
        limit = 100
        offset = 0
        recordings_list = list()
        self.recordings = dict()
        with click.progressbar(
            length=len(self.official_albums),
            label='Finding all tracks in albums from Musicbrainz',
        ) as bar:
            for i in self.official_albums:
                _recordings_result = self.browse_recordings(
                    i, limit=limit, offset=offset
                )
                album_recordings_list = _recordings_result['recording-list']
                recordings_list.append(
                    dict((i['id'], i['title']) for i in album_recordings_list)
                )
                bar.update(1)
        for i in recordings_list:
            self.recordings = {**self.recordings, **i}
        # pprint(self.recordings)
        click.echo(
            f'Found {len(self.recordings)} tracks from '
            f'{len(self.official_albums)} albums for {self.artist}'
        )
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
                f'Musicbrainz found several results for {self.builder.artist[0]}'
                '. Which artist/group do you want?',
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

    def _set_artist_id_on_product(self) -> None:
        self.builder.artist_id = self._artist_id
        self.builder.artist = self._artist
        # print(self.builder._product.artist_id)
        # print(self.builder._product.artist)
        # print(self.builder._product.__slots__)


@dataclass
class Lyrics:
    """docstring for Lyrics"""

    __slots__ = ['artist_id', 'artist']
    artist_id: str
    artist: str


if __name__ == '__main__':
    # director = LyricsClickDirector()
    # builder = LyricsBuilder()
    # director.builder = builder
    # director._get_initial_artists('One Direction')
    # director._confirm_final_artist()
    # director._set_artist_id_on_product()
    # director.builder._product
    print(type(Lyrics))
