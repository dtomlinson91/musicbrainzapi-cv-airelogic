# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['musicbrainzapi',
 'musicbrainzapi.api',
 'musicbrainzapi.api.lyrics',
 'musicbrainzapi.cli',
 'musicbrainzapi.cli.commands',
 'musicbrainzapi.wordcloud',
 'musicbrainzapi.wordcloud.resources']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.2.1,<3.0.0',
 'beautifultable>=0.8.0,<0.9.0',
<<<<<<< HEAD
=======
 'click>=7.0,<8.0',
>>>>>>> develop
 'multidict>=4.7.5,<5.0.0',
 'musicbrainzngs>=0.7.1,<0.8.0',
 'numpy>=1.18.1,<2.0.0',
 'progress>=1.5,<2.0',
 'requests>=2.23.0,<3.0.0',
 'wordcloud>=1.6.0,<2.0.0']

entry_points = \
{'console_scripts': ['musicbrainzapi = musicbrainzapi.cli.cli:cli']}

setup_kwargs = {
    'name': 'musicbrainzapi',
    'version': '1.0.0',
<<<<<<< HEAD
    'description': '',
    'long_description': None,
=======
    'description': 'Python module to calculate statistics and generate a wordcloud for a given artist. Uses the Musicbrainz API and the lyrics.ovh API.',
    'long_description': '',
>>>>>>> develop
    'author': 'dtomlinson',
    'author_email': 'dtomlinson@panaetius.co.uk',
    'maintainer': None,
    'maintainer_email': None,
<<<<<<< HEAD
    'url': None,
=======
    'url': 'https://github.com/dtomlinson91/musicbrainzapi-cv-airelogic',
>>>>>>> develop
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
