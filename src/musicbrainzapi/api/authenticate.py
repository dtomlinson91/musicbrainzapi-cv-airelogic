import musicbrainzngs

from musicbrainzapi.__header__ import __header__
from musicbrainzapi.__version__ import __version__


def set_useragent() -> None:
    """
    Function to set the correct user agent required for musicbrainz api
    access.
    """
    musicbrainzngs.set_useragent(__header__, __version__)

