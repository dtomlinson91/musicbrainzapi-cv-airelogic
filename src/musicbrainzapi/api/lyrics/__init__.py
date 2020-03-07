from __future__ import annotations
from typing import Union, Dict, List
from dataclasses import dataclass
import math

from beautifultable import BeautifulTable
import click
import numpy as np


@dataclass
class Lyrics:
    """Lyrics object for an artist.
    """

    artist_id: str
    artist: str
    country: Union[str, None]
    all_albums_with_tracks: List[Dict[str, List[str]]]
    all_albums_with_lyrics: List[Dict[str, List[str]]]
    all_albums_lyrics_count: List[Dict[str, List[List[str, int]]]]
    all_albums_lyrics_sum: List[Dict[str, List[int, str]]]
    album_statistics: Dict[str, Dict[str, int]]
    year_statistics: Dict[str, Dict[str, int]]

    _attributes = [
        'all_albums_with_tracks',
        'all_albums_with_lyrics',
        'all_albums_lyrics_count',
        'all_albums_lyrics_sum',
        'album_statistics',
        'year_statistics',
    ]

    def __init__(self) -> None:
        pass

    def show_summary(self) -> None:
        """Show the average word count for all lyrics

        Returns
        -------
        None
        """
        all_averages = []

        for i in self.album_statistics.values():
            try:
                all_averages.append(i['avg'])
            except (TypeError, ValueError):
                pass
        # print(all_averages)
        try:
            final_average = math.ceil(np.mean(all_averages))
        except ValueError:
            click.echo(
                'Oops! https://lyrics.ovh couldn\'t find any lyrics across any'
                ' album. This is caused by inconsistent Artist names from'
                ' Musicbrainz and lyrics.ovh. Try another artist.'
            )
            raise (SystemExit)
        output = BeautifulTable(max_width=200)
        output.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
        output.column_headers = [
            'Average number of words in tracks across all albums\n'
            f'for {self.artist}'
        ]
        output.append_row([final_average])
        click.echo(output)

        return self

    def show_summary_statistics(self, group_by: str) -> None:
        """Summary

        Parameters
        ----------
        group_by : str
            Parameter to group statistics by. Valid options are album or year

        Returns
        -------
        None
        """
        stats_obj = getattr(self, f'{group_by}_statistics')
        stats = [
            'avg',
            'std',
            'min',
            'max',
            'median',
            'count',
            'p_10',
            'p_25',
            'p_75',
            'p_90',
        ]
        output_0 = BeautifulTable(max_width=200)
        output_0.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
        output_0.column_headers = [
            'Descriptive statistics for number of words in tracks across all'
            f' {group_by}s\nfor {self.artist}'
        ]
        output_1 = BeautifulTable(max_width=200)
        output_1.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
        output_1.column_headers = [
            group_by,
            stats[0],
            stats[1],
            stats[2],
            stats[3],
            stats[4],
            stats[5],
            stats[6],
            stats[7],
            stats[8],
            stats[9],
        ]
        for group, s in stats_obj.items():
            try:
                output_1.append_row(
                    [
                        group,
                        s.get(stats[0]),
                        s.get(stats[1]),
                        s.get(stats[2]),
                        s.get(stats[3]),
                        s.get(stats[4]),
                        s.get(stats[5]),
                        s.get(stats[6]),
                        s.get(stats[7]),
                        s.get(stats[8]),
                        s.get(stats[9]),
                    ]
                )
            except AttributeError:
                continue
        output_0.append_row([output_1])
        click.echo(output_0)
        return self
