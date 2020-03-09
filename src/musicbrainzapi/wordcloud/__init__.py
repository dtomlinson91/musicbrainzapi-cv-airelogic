"""
Wordcloud from lyrics.
"""

from __future__ import annotations
import collections
from importlib import resources
import random
import re
import typing

from matplotlib import pyplot as plt
from PIL import Image
from wordcloud import STOPWORDS, WordCloud
import numpy as np

from musicbrainzapi.api.lyrics import Lyrics

if typing.TYPE_CHECKING:
    import PIL.PngImagePlugin.PngImageFile


class LyricsWordcloud:
    """Create a word cloud from Lyrics.

    Attributes
    ----------
    all_albums_lyrics_count : list
        List of all albums + track lyrics counted by each word
    char_mask : np.array
        numpy array containing data for the word cloud image
    freq : collections.Counter
        Counter object containing counts for all words across all tracks
    lyrics_list : list
        List of all words from all lyrics across all tracks.
    pillow_img : PIL.PngImagePlugin.PngImageFile
        pillow image of the word cloud base
    wc : wordcloud.WordCloud
        WordCloud object
    """

    def __init__(
        self,
        pillow_img: 'PIL.PngImagePlugin.PngImageFile',
        all_albums_lyrics_count: 'Lyrics.all_albums_lyrics_count',
    ):
        """
        Create a worcloud object.

        Parameters
        ----------
        pillow_img : PIL.PngImagePlugin.PngImageFile
            pillow image of the word cloud base
        all_albums_lyrics_count : Lyrics.all_albums_lyrics_count
            List of all albums + track lyrics counted by each word
        """
        self.pillow_img = pillow_img
        self.all_albums_lyrics_count = all_albums_lyrics_count

    @classmethod
    def use_microphone(
        cls, all_albums_lyrics_count: 'Lyrics.all_albums_lyrics_count',
    ) -> LyricsWordcloud:
        """
        Class method to instantiate with a microphone base image.

        Parameters
        ----------
        all_albums_lyrics_count : Lyrics.all_albums_lyrics_count
            List of all albums + track lyrics counted by each word

        """
        mic_resource = resources.path(
            'musicbrainzapi.wordcloud.resources', 'mic.png'
        )
        with mic_resource as m:
            mic_img = Image.open(m)

        return cls(mic_img, all_albums_lyrics_count)

    @staticmethod
    def generate_grey_colours(
        # word: str,
        # font_size: str,
        # random_state: typing.Union[None, bool] = None,
        *args,
        **kwargs,
    ) -> str:
        """Static method to generate a random grey colour."""
        colour = f'hsl(0, 0%, {random.randint(60, 100)}%)'
        return colour

    def _get_lyrics_list(self) -> None:
        """Gets all words from lyrics in a single list + cleans them.
        """
        self.lyrics_list = list()
        for i in self.all_albums_lyrics_count:
            for _, lyric in i.items():
                for track in lyric:
                    try:
                        for word in track:
                            for _ in range(1, word[1]):
                                cleaned = word[0]
                                cleaned = re.sub(
                                    r'[\(\[].*?[\)\]]', ' ', cleaned
                                )
                                cleaned = re.sub(
                                    r'[^a-zA-Z0-9\s]', '', cleaned
                                )
                                cleaned = cleaned.lower()
                                if cleaned in STOPWORDS:
                                    continue
                                self.lyrics_list.append(cleaned)
                    except IndexError:
                        pass
        return self

    def _get_frequencies(self) -> None:
        """Get frequencies of words from a list.
        """
        self.freq = collections.Counter(self.lyrics_list)

    def _get_char_mask(self) -> None:
        """Gets a numpy array for the image file.
        """
        self.char_mask = np.array(self.pillow_img)

    def _generate_word_cloud(self) -> None:
        """Generates a word cloud
        """
        self.wc = WordCloud(
            max_words=150,
            width=1500,
            height=1500,
            mask=self.char_mask,
            random_state=1,
        ).generate_from_frequencies(self.freq)
        return self

    def _generate_plot(self) -> None:
        """Plots the wordcloud and sets matplotlib options.
        """
        plt.imshow(
            self.wc.recolor(
                color_func=self.generate_grey_colours, random_state=3
            ),
            interpolation='bilinear',
        )
        plt.axis('off')
        return self

    # def show_word_cloud(self):
        # """Shows the word cloud.
        # """
        # plt.show()

    def create_word_cloud(self) -> None:
        """Creates a word cloud
        """
        self._get_lyrics_list()
        self._get_frequencies()
        self._get_char_mask()
        self._generate_word_cloud()
        self._generate_plot()
        return self
