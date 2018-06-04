#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pandas>=0.20.3', 'numpy>=1.13.3', 'gym>=0.9.4',
    'click>=6.0', 'btfx-trader>=0.1.3', 'pybeehive>=0.1.4',
    'twilio>=6.9.1'
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Djordje Pepic",
    author_email='djordje.m.pepic@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Minimal library for autotrading cryptocurrencies on Bitfinex",
    entry_points={
        'console_scripts': [
            'flashcrashed=flashcrashed.cli:main',
            'flashtest=flashcrashed.cli:performance',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='flashcrashed',
    name='flashcrashed',
    packages=find_packages(include=['flashcrashed', 'flashcrashed.market']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/sentrip/flashcrashed',
    version='0.1.2',
    zip_safe=False,
)
