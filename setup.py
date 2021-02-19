#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for ISalt
'''
import codecs
from setuptools import setup, find_packages

__author__ = 'Mircea Ulinic <ping@mirceaulinic.net>'

with codecs.open('README.rst', 'r', encoding='utf8') as file:
    long_description = file.read()

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name='isalt',
    version='2021.2.2',
    namespace_packages=['isalt'],
    packages=find_packages(),
    author='Mircea Ulinic',
    author_email='ping@mirceaulinic.net',
    description='ISalt: Interactive Salt Programming',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Utilities',
        'Topic :: System :: Shells',
        'Topic :: System :: Systems Administration',
        'Framework :: IPython',
        'Programming Language :: Python',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
    ],
    url='https://github.com/mirceaulinic/isalt',
    license="Apache License 2.0",
    keywords=('Salt', ' Interactive', ' Interpreter', 'Shell', 'Embedding'),
    include_package_data=True,
    install_requires=reqs,
    extras_require={'sproxy': ['salt-sproxy']},
    entry_points={'console_scripts': ['isalt=isalt.scripts:main']},
    data_files=[('man/man1', ['docs/man/isalt.1'])],
)
