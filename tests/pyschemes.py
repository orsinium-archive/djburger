# built-in
from __main__ import unittest, djburger
# external
from pyschemes import Scheme as PySchemes


class PySchemesValidatorsTest(unittest.TestCase):

    def test_base_validator(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.v.c.PySchemes([str, 2, int])
            v = v(request=None, data=['3', 2, 4])
            v.is_valid()
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.c.PySchemes([str, 2, int])
            v = v(request=None, data=[1, 2, 4])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='base int data'):
            v = djburger.v.c.PySchemes(int)
            v = v(request=None, data=3)
            v.is_valid()
            self.assertEqual(v.cleaned_data, 3)

    def test_wrapper_validator(self):
        with self.subTest(src_text='base pass'):
            v = djburger.v.w.PySchemes(PySchemes([str, 2, int]))
            v = v(request=None, data=['3', 2, 4])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.w.PySchemes(PySchemes([str, 2, int]))
            v = v(request=None, data=[1, 2, 4])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='base int data'):
            v = djburger.v.w.PySchemes(PySchemes(int))
            v = v(request=None, data=3)
            v.is_valid()
            self.assertEqual(v.cleaned_data, 3)
