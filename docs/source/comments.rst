***********************
Comments + Improvements
***********************

Python packages
===============

In this project we use the following Python packages:

+----------------+-------------------------------------------------------------------------+
| musicbrainzngs | This is a python wrapper around the Musicbrainz api.                    |
|                | This was used primarily to save time - the module handles all           |
|                | the endpoints and it provides checks to make sure variables             |
|                | passed are valid for the api. Behind the scenes it is using             |
|                | the requests library, and parsing the output into a python dict.        |
+----------------+-------------------------------------------------------------------------+
| addict         | The addict library gives us a Dict class. This is a personal preference |
|                | but I find the syntax easier to work with than standard python when     |
|                | dealing with many dictionaries. It is just subclass of the default      |
|                | ``dict`` class.                                                         |
+----------------+-------------------------------------------------------------------------+
| numpy          | One of the best python libraries - it gives us easy access to quantiles |
|                | and other basic stats.                                                  |
+----------------+-------------------------------------------------------------------------+
| beautifultable | Prints nice tables to stdout. Useful for showing data with a CLI.       |
+----------------+-------------------------------------------------------------------------+
| wordcloud      | The best library (I've found) for generating wordclouds.                |
+----------------+-------------------------------------------------------------------------+
| click          | I personally prefer click over alternatives like Cleo. This is used     |
|                | to provide the framework for the CLI.                                   |
+----------------+-------------------------------------------------------------------------+

Caveats
=======

The lyrics.ovh api requires the artist to match exactly what it has on record - it will not do any parsing to try look for similar matches. An example of this can be seen with the band "The All‐American Rejects". Musicbrainz returns the band with the "-", but the lyrics.ovh api requires a space character instead. 

A solution to this would be to filter the artist name if it contains any of these characters. But without thorough testing I did not implement this - as it could break other artists.


Improvements
============

Although fully (as far as I have tested) functional - the module could be improved several ways.

Testing
-------

Implementing a thorough test suite using ``pytest`` and ``coverage`` would be beneficial. Changes to the way the module parses data could be made with confidence if testing were implemented. As the data returned from Musicbrainz publishes a schema, this could be used to implement tests to make sure the code is fully covered.

Code restructure
----------------

The :class:`musicbrainzapi.api.lyrics.concrete_builder.LyricsConcreteBuilder` class could be improved. Many of the methods defined in here no longer need to be present. Some of the functionality (url checking for example) could be removed and implemented in other ways (a Mixin is one solution).

If other ways of filtering were to be added (as opposed to the current default of just Albums) this class would be useful in constructing our :class:`musicbrainzapi.api.lyrics.Lyrics` objects consistently.



