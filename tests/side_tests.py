# built-in
from __main__ import unittest, djburger
# external
import marshmallow
from pyschemes import Scheme as PySchemes


class MarshmallowValidatorsTest(unittest.TestCase):

    def test_base_validator(self):
        # BASE
        class Base(djburger.validators.b.Marshmallow):
            name = marshmallow.fields.Str()
            mail = marshmallow.fields.Email()
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Base(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Base(request=None, data=data)
            self.assertFalse(v.is_valid())

    def test_wrapper_validator(self):
        class Base(marshmallow.Schema):
            name = marshmallow.fields.Str()
            mail = marshmallow.fields.Email()

        Wrapped = djburger.validators.w.Marshmallow(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())


class PySchemesValidatorsTest(unittest.TestCase):

    def test_base_validator(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.validators.c.PySchemes([str, 2, int])
            v = v(request=None, data=['3', 2, 4])
            v.is_valid()
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.validators.c.PySchemes([str, 2, int])
            v = v(request=None, data=[1, 2, 4])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='base int data'):
            v = djburger.validators.c.PySchemes(int)
            v = v(request=None, data=3)
            v.is_valid()
            self.assertEqual(v.cleaned_data, 3)

    def test_wrapper_validator(self):
        with self.subTest(src_text='base pass'):
            v = djburger.validators.w.PySchemes(PySchemes([str, 2, int]))
            v = v(request=None, data=['3', 2, 4])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.validators.w.PySchemes(PySchemes([str, 2, int]))
            v = v(request=None, data=[1, 2, 4])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='base int data'):
            v = djburger.validators.w.PySchemes(PySchemes(int))
            v = v(request=None, data=3)
            v.is_valid()
            self.assertEqual(v.cleaned_data, 3)
