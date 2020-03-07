from __future__ import annotations
from abc import ABC, abstractstaticmethod, abstractmethod
from typing import Union

from musicbrainzapi.api import authenticate


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
    def set_useragent():
        authenticate.set_useragent()

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
