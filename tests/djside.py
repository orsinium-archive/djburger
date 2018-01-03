# built-in
from __main__ import unittest, djburger
# external
from django.contrib.auth.models import Group
import marshmallow
from pyschemes import Scheme as PySchemes
import rest_framework


class DjangoOtherValidatorsTest(unittest.TestCase):

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

    def test_pyschemes(self):
        with self.subTest(src_text='pyschemes'):
            v = djburger.v.c.PySchemes(
                {'name': str, 'id': int},
                policy='drop'
            )
            v = v(request=None, data=self.obj)
            self.assertTrue(v.is_valid())

    def test_marshmallow(self):
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

    def test_rest(self):
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
