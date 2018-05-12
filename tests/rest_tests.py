# built-in
from __main__ import unittest, djburger
# external
import rest_framework


class RestValidatorsTest(unittest.TestCase):
    def test_base_validator(self):
        # BASE
        class Base(djburger.validators.b.RESTFramework):
            name = rest_framework.serializers.CharField(max_length=20)
            mail = rest_framework.serializers.EmailField()
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Base(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Base(request=None, data=data)
            self.assertFalse(v.is_valid())

    def test_wrapper_validator(self):
        class Base(rest_framework.serializers.Serializer):
            name = rest_framework.serializers.CharField(max_length=20)
            mail = rest_framework.serializers.EmailField()
        Wrapped = djburger.validators.w.RESTFramework(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())
