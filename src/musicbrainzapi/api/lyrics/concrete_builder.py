from __future__ import annotations
from abc import ABC, abstractstaticmethod, abstractmethod
from typing import Union


class LyricsConcreteBuilder(ABC):
    """Abstract concrete builder for Lyrics
    """

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
    def set_useragent() -> None:
        pass

    @abstractstaticmethod
    def construct_lyrics_url() -> None:
        pass

    @abstractstaticmethod
    def request_lyrics_from_url() -> None:
        pass

    @abstractstaticmethod
    def strip_punctuation() -> None:
        pass

    @abstractstaticmethod
    def get_descriptive_statistics() -> None:
        pass

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

    @abstractmethod
    def find_lyrics_urls(self) -> None:
        pass

    @abstractmethod
    def find_all_lyrics(self) -> None:
        pass

    @abstractmethod
    def count_words_in_lyrics(self) -> None:
        pass

    @abstractmethod
    def calculate_track_totals(self) -> None:
        pass

    @abstractmethod
    def calculate_final_average_by_album(self) -> None:
        pass

    @abstractmethod
    def calculate_final_average_by_year(self) -> None:
        pass
