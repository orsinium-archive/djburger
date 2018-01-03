#! /usr/bin/env python

import os
import sys
import django

import unittest
# for python2
if not hasattr(unittest.TestCase, 'subTest'):
    import unittest2 as unittest


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/example')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()


import djburger  # noQA


from tests.django import * # noQA
from tests.django_and_other import * # noQA
from tests.main import * # noQA
from tests.marshmallow import * # noQA
from tests.pyschemes import * # noQA
from tests.rest import * # noQA


if __name__ == '__main__':
    unittest.main()
