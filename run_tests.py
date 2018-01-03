#! /usr/bin/env python

import os
import sys

import unittest
# for python2
if not hasattr(unittest.TestCase, 'subTest'):
    import unittest2 as unittest


testing_type = sys.argv[1] if len(sys.argv) > 1 else ''


if not testing_type or testing_type in ('django', 'djside'):
    import django
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/example')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()


import djburger  # noQA


from tests import main
if not testing_type or testing_type == 'django':
    from tests import django
if not testing_type or testing_type == 'djside':
    from tests import djside
if not testing_type or testing_type == 'rest':
    from tests import rest
if not testing_type or testing_type == 'marshmallow':
    from tests import marshmallow
if not testing_type or testing_type == 'pyschemes':
    from tests import pyschemes


if __name__ == '__main__':
    unittest.main()
