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


# pylint:disable=line-too-long
class LyricsWordcloud:
    """
    Create a Wordcloud from Lyrics.

    The docstring continues here.

    It should contain:

    - something
    - something else

    Args:
        pillow_img (PIL.PngImagePlugin.PngImageFile): pillow image of the word
            cloud base
        all_albums_lyrics_count (dict): A dictionary containing the lyrics from
           a whole album.

    !!! Attributes

        - `pillow_img` (pillow): A pillow image.

    Anything else can go here.

    Example:
        Here is how you can use it

    """

    def __init__(
        self,
        pillow_img: "PIL.PngImagePlugin.PngImageFile",
        all_albums_lyrics_count: "Lyrics.all_albums_lyrics_count",
    ):
        self.pillow_img = pillow_img
        self.all_albums_lyrics_count = all_albums_lyrics_count
        self.test = []

    @classmethod
    def use_microphone(
        cls, all_albums_lyrics_count: "Lyrics.all_albums_lyrics_count",
    ) -> LyricsWordcloud:
        """Create a LyricsWordcloud using a microphone as a base image.

        Args:
            all_albums_lyrics_count (dict): A dictionary containing the lyrics from a whole album.
        Returns:
            LyricsWordcloud: Instance of itself with a micrphone image loaded in.

        """
        mic_resource = resources.path("musicbrainzapi.wordcloud.resources", "mic.png")
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
        """Static method to return a random grey color.

        Returns:
            str: A random grey colour in `hsl` form.

            Can be any grey colour.
        """
        return f"hsl(0, 0%, {random.randint(60, 100)}%)"

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
                                cleaned = re.sub(r"[\(\[].*?[\)\]]", " ", cleaned)
                                cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", cleaned)
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
            max_words=150, width=1500, height=1500, mask=self.char_mask, random_state=1,
        ).generate_from_frequencies(self.freq)
        return self

    def _generate_plot(self) -> None:
        """Plots the wordcloud and sets matplotlib options.
        """
        plt.imshow(
            self.wc.recolor(color_func=self.generate_grey_colours, random_state=3),
            interpolation="bilinear",
        )
        plt.axis("off")
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
