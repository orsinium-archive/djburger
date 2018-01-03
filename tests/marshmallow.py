# built-in
from __main__ import unittest, djburger
# external
import marshmallow


class MarshmallowValidatorsTest(unittest.TestCase):

    def test_base_validator(self):
        # BASE
        class Base(djburger.v.b.Marshmallow):
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

        Wrapped = djburger.v.w.Marshmallow(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())
