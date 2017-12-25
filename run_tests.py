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



from tests.controllers import * # noQA
from tests.parsers import * # noQA
from tests.renderers import * # noQA
from tests.side_validators import * # noQA
from tests.validators import * # noQA
from tests.views import * # noQA


if __name__ == '__main__':
    unittest.main()
