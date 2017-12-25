# built-in
from __main__ import unittest
# external
from django.contrib.auth.models import Group
import marshmallow
from pyschemes import Scheme as PySchemes
import rest_framework
# project
import djburger


class TestSideValidators(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Group.objects.filter(name='TEST_IT').delete()
        Group.objects.filter(name='TEST_IT_2').delete()

        cls.obj = Group.objects.create(name='TEST_IT')
        Group.objects.create(name='TEST_IT_2')
        cls.qs = Group.objects.all()

    @classmethod
    def tearDownClass(cls):
        Group.objects.get(name='TEST_IT').delete()
        Group.objects.get(name='TEST_IT_2').delete()

    def test_pyschemes_validator(self):
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
        # WRAPPER
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

    def test_marshmallow_validator(self):
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

        # WRAPPER
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

    def test_rest_framework_validator(self):
        # BASE
        class Base(djburger.v.b.RESTFramework):
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

        # WRAPPER
        class Base(rest_framework.serializers.Serializer):
            name = rest_framework.serializers.CharField(max_length=20)
            mail = rest_framework.serializers.EmailField()
        Wrapped = djburger.v.w.RESTFramework(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())

    def test_form_validator(self):
        # BASE
        class Base(djburger.v.b.Form):
            name = djburger.f.CharField(max_length=20)
            mail = djburger.f.EmailField()
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Base(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Base(request=None, data=data)
            self.assertFalse(v.is_valid())

        # WRAPPER
        class Base(djburger.f.Form):
            name = djburger.f.CharField(max_length=20)
            mail = djburger.f.EmailField()
        Wrapped = djburger.v.w.Form(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())

    def test_model_serialization(self):
        with self.subTest(src_text='pyschemes'):
            v = djburger.v.c.PySchemes(
                {'name': str, 'id': int},
                policy='drop'
            )
            v = v(request=None, data=self.obj)
            self.assertTrue(v.is_valid())

        with self.subTest(src_text='marshmallow base'):
            class Base(djburger.v.b.Marshmallow):
                name = marshmallow.fields.Str()
            v = Base(request=None, data=self.obj)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='marshmallow wrapper'):
            class Base(marshmallow.Schema):
                name = marshmallow.fields.Str()
            Wrapped = djburger.v.w.Marshmallow(Base) # noQA
            v = Wrapped(request=None, data=self.obj)
            self.assertTrue(v.is_valid())

        with self.subTest(src_text='rest framework base'):
            class Base(djburger.v.b.RESTFramework):
                name = rest_framework.serializers.CharField(max_length=20)
            v = Base(request=None, data=self.obj)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='rest framework wrapper'):
            class Base(rest_framework.serializers.Serializer):
                name = rest_framework.serializers.CharField(max_length=20)
            Wrapped = djburger.v.w.RESTFramework(Base) # noQA
            v = Wrapped(request=None, data=self.obj)
            self.assertTrue(v.is_valid())
