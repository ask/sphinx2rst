#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    raise
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import os
import codecs

# -*- Classifiers -*-

classes = """
    Development Status :: 5 - Production/Stable
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    License :: OSI Approved :: BSD License
    Intended Audience :: Developers
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

# -*- Long Description -*-

if os.path.exists('README.rst'):
    long_description = codecs.open('README.rst', 'r', 'utf-8').read()
else:
    long_description = 'See http://pypi.python.org/pypi/sphinx2rst'

# -*- Entry Points -*- #

# -*- %%% -*-


setup(
    name='sphinx2rst',
    version='1.1.0',
    description='Convert Sphinx to rst',
    author='Ask Solem',
    author_email='ask@celeryproject.org',
    url='https://github.com/ask/sphinx2rst',
    platforms=['any'],
    license='BSD',
    packages=['sphinx2rst'],
    zip_safe=False,
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'sphinx2rst = sphinx2rst.__main__:main',
        ],
    },
    long_description=long_description,
)
