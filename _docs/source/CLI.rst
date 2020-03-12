***
CLI
***

As the CLI is provided by `Click`_ , you can pass the ``--help`` option to the base command, or any subcommands, to see information on usage and all available options.

.. _Click: https://click.palletsprojects.com/en/7.x/

Full options of the CLI are provided on this page.

.. important:: The ``--path`` option should be provided to the base command. This is so the path provided can be used in all subcommands.


Quickstart
==========

If you want to see everything the module offers run the following:

.. code-block:: bash

    musicbrainzapi --path . lyrics -a "savage garden" -c gb --show-summary all --wordcloud --save-output

This will search for all tracks across all albums for the artist Savage Garden. 

``--show-summary all`` will show descriptive statistics for both albums and years for this artist.

``--wordcloud`` will generate a wordcloud showing the most popular words across all lyrics.

``--save-output`` will save the module's output to disk as ``.json`` files.

Outputs
=======

The following files will be saved to disk 

- all_albums_lyrics_sum.json - Total number of words in a track for each album.
- year_statistics.json - Descriptive statistics by year.
- album_statistics.json - Descriptive statistics by album
- all_albums_with_tracks.json - Track titles for each album.
- all_albums_with_lyrics.json - Lyrics for each track for each album.
- all_albums_lyrics_count.json - Shows a frequency count of each word in every track.

CLI Documentation
=================

.. click:: musicbrainzapi.cli.cli:cli
  :prog: musicbrainzapi
  :show-nested:
