=============
Introduction
=============

.. image:: https://img.shields.io/readthedocs/panaetius?style=for-the-badge
.. image:: https://img.shields.io/github/v/tag/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/github/commit-activity/m/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/github/issues/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/github/license/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/github/languages/code-size/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/github/languages/top/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/requires/github/dtomlinson91/musicbrainzapi-cv-airelogic?style=for-the-badge
.. image:: https://img.shields.io/codacy/grade/f9517450400d48b0a7222a383c2e8fe2?style=for-the-badge

Summary
========

Musicbrainzapi is a Python module with a CLI that allows you to search for an artist and receive summary statistics on lyrics across all albums + tracks. 

The module can also generate and display a wordcloud from the lyrics.

In addition to basic statistics the module further allows you to save details of an artist. You can save album information, the lyrics themselves and track lists.

The module (currently) provides a simple CLI with some underlying assumptions:

- We are interested in albums only - no singles.
- We are interested in any album where the artist is listed as a primary artist on a release. This could include compilations or joint albums with other artists.
- Where an album has been released multiple times, in different regions, we take the album with the longest track list. 

These assumptions are not configurable in the current version - but this functionality could be added to the module if needed. 

Further information, and a brief summary of decisions taken and current caveats can be found in the documentation which is linked below.

Documentation
=============

The documentation for the module can be found at https://musicbrainzapi-cv-airelogic.readthedocs.io/en/latest/

Installation
============

You will need ``python>=3.7``. Installation to a python virtual environment is recommended.

PIP
---

Download the latest release ``.whl`` file from the `releases`_ page

.. _releases: https://github.com/dtomlinson91/musicbrainzapi-cv-airelogic/releases

In a virtual environment run:

.. code-block:: bash

    pip install -U musicbrainzapi.whl

Replacing ``musicbrainzapi.whl`` with the filename you downloaded.

setup.py
--------

Clone the repo:

.. code-block:: bash

    git clone https://github.com/dtomlinson91/musicbrainzapi-cv-airelogic.git

In the root of the repo in a virtual environment run:

.. code-block:: bash

    python ./setup.py install

Docker
------

.. note:: Using Docker will mean you cannot view a wordcloud, as the default behaviour is to show the plot interactively which the container cannot do.

If you don't have ``python>=3.7`` installed, or would rather use Docker, you can build a Docker image and run the module using Docker.

Clone the repo:

.. code-block:: bash

    git clone https://github.com/dtomlinson91/musicbrainzapi-cv-airelogic.git

In the root of the repo build the Docker image:

.. code-block:: bash

    docker build . -t musicbrainzapi

No entrypoint is provided in the ``Dockerfile`` - you will have to specify the command at runtime and run the container in interactive mode:

Using Docker run
^^^^^^^^^^^^^^^^

.. code-block:: bash

    docker run --rm -it --volume=$(pwd):/outputs \
    musicbrainzapi:latest musicbrainzapi --path /outputs \
    lyrics -a "Savage Garden" -c gb --show-summary all --save-output


Usage
=====

Once installed you can access the command running:

.. code-block:: bash

    musicbrainzapi

To see all options available you can run:

.. code-block:: bash

    musicbrainzapi --help

In the current release there is one command available ``lyrics``:

.. code-block:: bash

    musicbrainzapi lyrics --help

License information
===================

Released under the `MIT License`_ 

.. _MIT License: https://github.com/dtomlinson91/musicbrainzapi-cv-airelogic/blob/master/LICENSE
