from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from pprint import pprint
from typing import Union, List, Dict
import html
import json
import os
from collections import Counter
import string
import math
import statistics

import musicbrainzngs
import click
import addict
import requests
import numpy

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
                'Searching Musicbrainz for all tracks in all albums for '
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
            f'Found {self.total_track_count} tracks across'
            f' {len(self.release_group_ids)} albums for {self.artist}'
        )
        del resp_0
        return self

    def find_lyrics_urls(self) -> None:
        self.all_albums_lyrics_url = list()
        for x in self.all_albums:
            for alb, tracks in x.items():
                lyrics = addict.Dict(
                    (
                        alb,
                        [
                            self.construct_lyrics_url(self.artist, i)
                            for i in tracks
                        ],
                    )
                )
                self.all_albums_lyrics_url.append(lyrics)

        # pprint(self.all_albums_lyrics_url)
        return self

# change this for progressbar for i loop
    def find_all_lyrics(self) -> None:
        self.all_albums_lyrics = list()

        with click.progressbar(
            length=self.total_track_count,
            label=f'Finding lyrics for {self.total_track_count}'
            f' tracks for {self.artist}. This may take some time! ☕️',
        ) as bar:

            for x in self.all_albums_lyrics_url:
                for alb, urls in x.items():
                    bar.update(1)
                    update = len(urls)
                    lyrics = addict.Dict(
                        (alb, [self.request_lyrics_from_url(i) for i in urls])
                    )
                    self.all_albums_lyrics.append(lyrics)
                    bar.update(update - 1)
        return self

    def count_words_in_lyrics(self) -> None:
        # remove punctuation, fix click bar
        self.all_albums_lyrics_count = list()
        print(self.total_track_count)
        with click.progressbar(
            length=self.total_track_count, label=f'Processing lyrics'
        ) as bar:
            for x in self.all_albums_lyrics:
                for alb, lyrics in x.items():
                    update = len(lyrics)
                    bar.update(1)
                    lyrics = addict.Dict(
                        (
                            alb,
                            [
                                Counter(i.split()).most_common()
                                if i is not None
                                else 'No Lyrics'
                                for i in lyrics
                            ],
                        )
                    )
                    self.all_albums_lyrics_count.append(lyrics)
                    bar.update(update - 1)
        click.echo(f'Processed lyrics for {self.total_track_count} tracks.')
        return self

    # rename this
    def calculate_average_all_albums(self) -> None:
        self.all_albums_lyrics_sum = list()
        # with open(f'{os.getcwd()}/lyrics_count.json', 'r') as f:
        #     album_lyrics = json.load(f)
        album_lyrics = self.all_albums_lyrics_count
        count = 0
        for i in album_lyrics:
            count += len(i)
            for album, lyrics_list in i.items():
                album_avg = list()
                d = addict.Dict()
                print(album)
                for j in lyrics_list:
                    if j != 'No Lyrics':
                        song_total = 0
                        for k in j:
                            song_total += k[1]
                    else:
                        song_total = "No Lyrics"
                    album_avg.append(song_total)
                # We want to avoid a ValueError when we loop through
                # the first time
                try:
                    d = addict.Dict(**d, **addict.Dict(album, album_avg))
                except ValueError:
                    d = addict.Dict((album, album_avg))
                # print(d)
                self.all_albums_lyrics_sum.append(d)
        # print(count)
        with open(f'{os.getcwd()}/lyrics_sum_all_album.json', 'w+') as f:
            json.dump(self.all_albums_lyrics_sum, f)
        return self

    def calculate_final_average_by_album(self) -> None:
        self.album_statistics = addict.Dict()
        album_lyrics = self.all_albums_lyrics_sum
        # with open(f'{os.getcwd()}/lyrics_sum_all_album.json', 'r') as f:
        #     album_lyrics = json.load(f)

        for i in album_lyrics:
            for album, count in i.items():
                # We filter twice, once to remove strings, then to filter
                # the integers
                _count = [d for d in count if isinstance(d, int)]
                _count = [d for d in _count if d > 1]
                _d = self.get_descriptive_statistics(_count)
                self.album_statistics = addict.Dict(
                    **self.album_statistics, **addict.Dict((album, _d))
                )
        pprint(self.album_statistics)

    # implement above in this
    def calculate_final_average_by_year(self) -> None:
        group_by_years = addict.Dict()
        self.year_statistics = addict.Dict()
        album_lyrics = self.all_albums_lyrics_sum
        # with open(f'{os.getcwd()}/lyrics_sum_all_album.json', 'r') as f:
        #     album_lyrics = json.load(f)

        # Merge years together
        for i in album_lyrics:
            for album, count in i.items():
                year = album.split('[')[-1].strip(']')
                try:
                    group_by_years = addict.Dict(
                        **group_by_years, **addict.Dict((year, count))
                    )
                # First loop returns value error for empty dict
                except ValueError:
                    group_by_years = addict.Dict((year, count))
                # Multiple years raise a TypeError - we append
                except TypeError:
                    group_by_years.get(year).extend(count)

        for year, y_count in group_by_years.items():
            _y_count = [d for d in y_count if isinstance(d, int)]
            _y_count = [d for d in _y_count if d > 1]
            _d = self.get_descriptive_statistics(_y_count)
            self.year_statistics = addict.Dict(
                **self.year_statistics, **addict.Dict((year, _d))
            )
        pprint(self.year_statistics)

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
            lyrics = LyricsBuilder.strip_punctuation(resp.json()['lyrics'])
            return lyrics
        except (KeyError, json.decoder.JSONDecodeError):
            return

    @staticmethod
    def strip_punctuation(word: str) -> str:
        _strip = word.translate(str.maketrans('', '', string.punctuation))
        return _strip

    @staticmethod
    def get_descriptive_statistics(nums: list) -> Dict[str, int]:
        avg = math.ceil(numpy.mean(nums))
        median = math.ceil(numpy.median(nums))
        std = math.ceil(numpy.std(nums))
        max = math.ceil(numpy.max(nums))
        min = math.ceil(numpy.min(nums))
        p_10 = math.ceil(numpy.percentile(nums, 10))
        p_25 = math.ceil(numpy.percentile(nums, 25))
        p_75 = math.ceil(numpy.percentile(nums, 75))
        p_90 = math.ceil(numpy.percentile(nums, 90))
        count = len(nums)
        _d = addict.Dict(
            ('avg', avg),
            ('median', median),
            ('std', std),
            ('max', max),
            ('min', min),
            ('p_10', p_10),
            ('p_25', p_25),
            ('p_75', p_75),
            ('p_90', p_90),
            ('count', count)
        )
        return _d


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
        self.builder.count_words_in_lyrics()
        with open(f'{os.getcwd()}/lyrics_count.json', 'w+') as file:
            json.dump(
                self.builder.all_albums_lyrics_count,
                file,
                indent=4,
                sort_keys=True,
            )
        self.builder._product.all_albums_lyrics_count = (
            self.builder.all_albums_lyrics_count
        )
        return self

    def _calculate_average(self) -> None:
        self.builder.calculate_average_all_albums()
        self.builder._product.all_albums_lyrics_sum = (
            self.builder.all_albums_lyrics_sum
        )
        pprint(self.builder._product.all_albums_lyrics_sum)
        self.builder.calculate_final_average_by_album()
        self.builder.calculate_final_average_by_year()

    def _dev(self) -> None:
        self.builder.calculate_final_average_by_album()
        self.builder.calculate_final_average_by_year()


@dataclass
class Lyrics:
    """docstring for Lyrics"""

    __slots__ = [
        'artist_id',
        'artist',
        'country',
        'all_albums_with_tracks',
        'all_albums_with_lyrics',
        'all_albums_lyrics_count',
        'all_albums_lyrics_sum',
    ]
    artist_id: str
    artist: str
    country: Union[str, None]
    all_albums_with_tracks: List[Dict[str, List[str]]]
    all_albums_with_lyrics: List[Dict[str, List[str]]]
    all_albums_lyrics_count: List[Dict[str, List[List[str, int]]]]
    all_albums_lyrics_sum: List[Dict[str, List[int, str]]]
