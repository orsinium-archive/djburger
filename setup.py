#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='djburger',
    version='0.10.1',

    author='orsinium',
    author_email='master_fess@mail.ru',

    description='Framework for views in big projects on Django.',
    long_description=open('README.rst').read(),
    keywords='djburger framework django contracts pre post validation',

    packages=['djburger', 'djburger.validators'],
    requires=['six'],

    url='https://github.com/orsinium/djburger',
    download_url='https://github.com/orsinium/djburger/tarball/master',

    license='GNU Lesser General Public License v3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python',
    ],
)
