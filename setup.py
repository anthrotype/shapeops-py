#!/usr/bin/env python

import io
import sys

import setuptools


with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []
needs_wheel = {'bdist_wheel'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []

name = 'shapeops'
description = 'Boolean operations and overlap removal for curves'
url = 'https://github.com/anthrotype/shapeops-py'

requirements = [
    "fonttools>=3.1.2",
    "pyclipper>=1.0.5",
]

setup_params = dict(
    name=name,
    use_scm_version=True,
    author="Cosimo Lupo",
    author_email="cosimo.lupo@daltonmaag.com",
    description=description,
    long_description=long_description,
    url=url,
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    include_package_data=True,
    license="Apache Software License 2.0",
    install_requires=requirements,
    extras_require={
    },
    setup_requires=[
        'setuptools_scm>=1.15.0',
    ] + pytest_runner + wheel,
    tests_require=[
        'pytest>=3.0.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
    ],
)


if __name__ == '__main__':
    setuptools.setup(**setup_params)
