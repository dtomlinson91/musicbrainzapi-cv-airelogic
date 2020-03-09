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

If other ways of filtering were to be added (as opposed to the current default of just Albums) then this class would be useful to build our :class:`musicbrainzapi.api.lyrics.Lyrics` objects consistently.

Additional functionality to the lyrics command
-----------------------------------------------

The command could be improved in a few ways:

Different aggregations
^^^^^^^^^^^^^^^^^^^^^^

The ability for the user to specify something other than album or year to group by. For artists with large libraries, it might be useful to see results aggregated by other types of releases.

Multiple artists
^^^^^^^^^^^^^^^^

Searching for multiple artists and comparing is certainly possible in the current iteration (click provides a nice way to accept multiple artists and then we create our ``Lyrics`` objects from these) this wasn't implemented. There are rate limiting factors which may slow down the program and in the current implementation it could increase runtime considerably.
  
Speed improvements
-------------------

The musicbrainz api isn't too slow, however, the lyrics.ovh api can be. 

One solution would be to implement threading - as we are waiting on HTTP requests this suggests threading could be a good candidate. An alternative to threading (if we are dealing with many requests) could be asyncio. 

This wasn't implemented primarily because of time - but threading could be implemented on each call we make to the API.

An alternative, and I believe an interesting solution, would be to use AWS Lambda (serverless).

There is a caveat to this solution and it is cost - threading is free but adds development time and increases complexity. AWS isn't free but allows you to scale the requests out.

A solution would be to use a module like `Zappa`_. I have used this module before and it is a great tool to create lambda functions quickly.

If more control was needed one solution could be:

- Generate UUID of the current instance
- For each request to the API, dispatch a lambda function (using ``boto3``) which will run against the api. This function should take the UUID from before.
- Once finished either

    + Save results in DynamoDB with the UUID
    + Send results to SQS/SNS (not desirable, the lyrics size could be large)

- As soon as the lambdas have been dispatched, the script could either poll from a queue, or read the events queue of the DynamoDB to retrieve the results. Processing the lyrics could then begin.

This requires the user to have an internet connection - which is a current requirement. Requests to the api could be made simultaneously - without adding the complexity that comes with threading. This would not solve any API rate limiting - we are required to provide an application user_agent to the api to identify the app.

An interesting solution, and one I did consider, was to have the program run entirely in lambda, requiring no depdencies and just a simple front end that sends requests, and uses ``boto3`` to retrieve. The simplicity of this, and the fact that AWS provide an SDK for many languages, means the cient code could run in any language.

An interface to AWS API Gateway would provide the entry point to the lambda.

Writing it in this manner (with an api backend) would mean a webapp of the program could be possible, with the frontend served with something like ``Vuejs`` or ``React``.

.. _Zappa: https://github.com/Miserlou/Zappa

Error catching
--------------

Handling missing data from both APIs is done with error catching (namely ``ValueError`` and ``TypeError``).

Although inelegant, and not guaranteed to capture the specific behaviour we want to catch (missing data etc.) it is a solution and appears to work quite well.

Musicbrainz provides a schema for their api. If this were to be placed in a production environment then readdressing this should be a priority - we should be checking the values returned, using the schema as a guide, and replacing missing values accordingly. We should not rely on ``try except`` blocks to do this as it can be unreliable and is prone to raise other errors.

