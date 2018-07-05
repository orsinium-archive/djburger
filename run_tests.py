#! /usr/bin/env python

import os
import sys

import unittest
# for python2
if not hasattr(unittest.TestCase, 'subTest'):
    import unittest2 as unittest


testing_type = ' '.join(sys.argv) if len(sys.argv) > 1 else ''


try:
    import django
except ImportError:
    pass
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/example')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()

    try:
        from django.test.runner import setup_databases
    except ImportError:
        from django.test.utils import setup_databases
    setup_databases(0, False)


import djburger  # noQA


if not testing_type:
    from tests.main_tests import *
    from tests.django_tests import *
    from tests.djside_tests import *
    from tests.rest_tests import *
    from tests.side_tests import *
else:
    if 'main_tests' in testing_type:
        from tests import main_tests
    if 'django_tests' in testing_type:
        from tests import django_tests
    if 'djside_tests' in testing_type:
        from tests import djside_tests
    if 'rest_tests' in testing_type:
        from tests import rest_tests
    if ' side_tests' in testing_type or testing_type.startswith('side_tests'):
        from tests import side_tests


if __name__ == '__main__':
    unittest.main()
