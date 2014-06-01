#!/usr/bin/env python

from setuptools import setup
setup(name='ttc',
    version='0.1',
	packages=['typetalkcli'],
	install_requires=['requests', 'termcolor'],
	author = 'Shoji Nakahara',
	description='Typetalk cli',
	keywords = 'typetalk',
	entry_points={
  		'console_scripts':['ttc = typetalkcli.ttc:main']
		}
	)
