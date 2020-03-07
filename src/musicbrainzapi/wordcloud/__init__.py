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

from musicbrainzapi.api.command_builders.lyrics import Lyrics

if typing.TYPE_CHECKING:
    import PIL.PngImagePlugin.PngImageFile


class LyricsWordcloud:

    """docstring for LyricsWordcloud"""

    def __init__(
        self,
        pillow_img: 'PIL.PngImagePlugin.PngImageFile',
        all_albums_lyrics_count: 'Lyrics.all_albums_lyrics_count',
    ):
        self.pillow_img = pillow_img
        self.all_albums_lyrics_count = all_albums_lyrics_count

    @classmethod
    def use_microphone(
        cls, all_albums_lyrics_count: 'Lyrics.all_albums_lyrics_count',
    ) -> LyricsWordcloud:
        mic_resource = resources.path(
            'musicbrainzapi.wordcloud.resources', 'mic.png'
        )
        with mic_resource as m:
            mic_img = Image.open(m)

        return cls(mic_img, all_albums_lyrics_count)

    def _get_lyrics_list(self) -> None:
        self.lyrics_list = list()
        for i in self.all_albums_lyrics_count:
            for album, lyric in i.items():
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
        self.freq = collections.Counter(self.lyrics_list)

    def _get_char_mask(self) -> None:
        self.char_mask = np.array(self.pillow_img)

    @staticmethod
    def generate_grey_colours(
        word: str,
        font_size: str,
        random_state: typing.Union[None, bool] = None,
        *args,
        **kwargs,
    ) -> str:
        colour = f'hsl(0, 0%, {random.randint(60, 100)}%)'
        return colour

    def _generate_word_cloud(self) -> None:
        self.wc = WordCloud(
            max_words=50,
            width=500,
            height=500,
            mask=self.char_mask,
            random_state=1,
        ).generate_from_frequencies(self.freq)
        return self

    def _generate_plot(self) -> None:
        plt.imshow(
            self.wc.recolor(
                color_func=self.generate_grey_colours, random_state=3
            ),
            interpolation='bilinear',
        )
        plt.axis('off')
        return self

    def save_to_disk(self, path: str):
        pass

    def show_word_cloud(self):
        plt.show()

    def create_word_cloud(self) -> None:
        self._get_lyrics_list()
        self._get_frequencies()
        self._get_char_mask()
        self._generate_word_cloud()
        self._generate_plot()
        return self
