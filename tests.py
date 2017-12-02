# -*- coding: utf-8 -*-

# built-in
import json
import os
import sys
import unittest
# external
import marshmallow
from pyschemes import Scheme as PySchemes
import rest_framework
import yaml
# django
import django
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory


# for python2
if not hasattr(unittest.TestCase, 'subTest'):
    import unittest2 as unittest


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/example')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()


# import only after django.setup()
from django.contrib.auth.models import Group  # noQA
import djburger
from rest_framework import renderers as rest_framework_renderers


class TestValidators(unittest.TestCase):

    def test_type_validator(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.v.c.Type(int)
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.c.Type(int)
            v = v('3')
            self.assertFalse(v.is_valid())

        # BOOL
        with self.subTest(src_text='bool pass'):
            v = djburger.v.c.IsBool
            v = v(False)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='bool int not pass'):
            v = djburger.v.c.IsBool
            v = v(1)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='bool not pass'):
            v = djburger.v.c.IsBool
            v = v('1')
            self.assertFalse(v.is_valid())

        # INT
        with self.subTest(src_text='int pass'):
            v = djburger.v.c.IsInt
            v = v(3)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='int bool not pass'):
            v = djburger.v.c.IsInt
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='int not pass'):
            v = djburger.v.c.IsInt
            v = v('4')
            self.assertFalse(v.is_valid())

        # FLOAT
        with self.subTest(src_text='float pass'):
            v = djburger.v.c.IsFloat
            v = v(3.2)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='float bool not pass'):
            v = djburger.v.c.IsFloat
            v = v(True)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='float not pass'):
            v = djburger.v.c.IsFloat
            v = v(4)
            self.assertFalse(v.is_valid())

        # STR
        with self.subTest(src_text='str pass'):
            v = djburger.v.c.IsStr
            v = v('1')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str empty pass'):
            v = djburger.v.c.IsStr
            v = v('')
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.v.c.IsStr
            v = v(1)
            self.assertFalse(v.is_valid())

        # DICT
        with self.subTest(src_text='dict pass'):
            v = djburger.v.c.IsDict
            v = v({1: 2})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict empty pass'):
            v = djburger.v.c.IsDict
            v = v({})
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='dict not pass'):
            v = djburger.v.c.IsDict
            v = v([1, 2, 3])
            self.assertFalse(v.is_valid())

        # LIST
        with self.subTest(src_text='list pass'):
            v = djburger.v.c.IsList
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list empty pass'):
            v = djburger.v.c.IsList
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list tuple pass'):
            v = djburger.v.c.IsList
            v = v((1, 2, 3))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list not pass'):
            v = djburger.v.c.IsList
            v = v({})
            self.assertFalse(v.is_valid())

        # ITER
        with self.subTest(src_text='iter list pass'):
            v = djburger.v.c.IsList
            v = v([1, 2])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter tuple pass'):
            v = djburger.v.c.IsList
            v = v((1, 2))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter empty pass'):
            v = djburger.v.c.IsList
            v = v([])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='iter str not pass'):
            v = djburger.v.c.IsList
            v = v('123')
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter dict not pass'):
            v = djburger.v.c.IsList
            v = v({1: 2, 3: 4})
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='iter not pass'):
            v = djburger.v.c.IsList
            v = v(4)
            self.assertFalse(v.is_valid())

    def test_list_validator(self):
        with self.subTest(src_text='list int pass'):
            v = djburger.v.c.List(djburger.v.c.IsInt)
            v = v([1, 2, 3])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='list mixed not pass'):
            v = djburger.v.c.List(djburger.v.c.IsInt)
            v = v([1, '2', 3])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='list str pass'):
            v = djburger.v.c.List(djburger.v.c.IsStr)
            v = v(['1', '2', '3'])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='tuple str pass'):
            v = djburger.v.c.List(djburger.v.c.IsStr)
            v = v(('1', '2', '3'))
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='str not pass'):
            v = djburger.v.c.List(djburger.v.c.IsStr)
            v = v('123')
            self.assertFalse(v.is_valid())

        with self.subTest(src_text='list list str pass'):
            v = djburger.v.c.List(
                djburger.v.c.List(
                    djburger.v.c.IsStr
                )
            )
            v = v(data=[('1', '2'), ('3', '4', '5'), ('6', )])
            self.assertTrue(v.is_valid())

    def test_dict_mixed_validator(self):
        with self.subTest(src_text='dict int+str pass'):
            v = djburger.v.c.DictMixed(validators={
                'ping': djburger.v.c.IsInt,
                'pong': djburger.v.c.IsStr,
            })
            v = v(data={
                'ping': 3,
                'pong': 'test',
            })
            self.assertTrue(v.is_valid())

    def test_lambda_validator(self):
        with self.subTest(src_text='lambda int pass'):
            v = djburger.v.c.Lambda(key=lambda data: data > 0)
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='lambda int not pass'):
            v = djburger.v.c.Lambda(key=lambda data: data > 0)
            v = v(-4)
            self.assertFalse(v.is_valid())

    def test_chain_validator(self):
        with self.subTest(src_text='chain int pass'):
            v = djburger.v.c.Chain([
                djburger.v.c.IsInt,
                djburger.v.c.Lambda(key=lambda data: data > 0),
            ])
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='lambda int not pass'):
            v = djburger.v.c.Chain([
                djburger.v.c.IsInt,
                djburger.v.c.Lambda(key=lambda data: data > 0),
            ])
            v = v(-4)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='lambda str not pass'):
            v = djburger.v.c.Chain([
                djburger.v.c.IsInt,
                djburger.v.c.Lambda(key=lambda data: data > 0),
            ])
            v = v('4')
            self.assertFalse(v.is_valid())


class TestRenderers(unittest.TestCase):

    def test_json_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.r.JSON()(data=data).content
            self.assertEqual(content, b'"test"')
        with self.subTest(src_text='int'):
            data = -13
            content = djburger.r.JSON()(data=data).content
            self.assertEqual(content, b'-13')
        with self.subTest(src_text='dict'):
            data = {'data': 1516}
            content = djburger.r.JSON()(data=data).content
            self.assertEqual(content, b'{"data": 1516}')
        with self.subTest(src_text='list'):
            data = [1, 2, 3]
            content = djburger.r.JSON()(data=data).content
            self.assertEqual(content, b'[1, 2, 3]')
        with self.subTest(src_text='mixed'):
            data = {'data': [1, 2, 3]}
            content = djburger.r.JSON()(data=data).content
            self.assertEqual(content, b'{"data": [1, 2, 3]}')
        with self.subTest(src_text='non-flat'):
            data = 1516
            content = djburger.r.JSON(flat=False)(data=data).content
            self.assertEqual(content, b'{"data": 1516}')

    def test_yaml_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.r.YAML()(data=data).content
            self.assertEqual(yaml.load(content), {'data': data})
        with self.subTest(src_text='mixed'):
            data = [1, '2', [3, 4], {5: 6}]
            content = djburger.r.YAML(flat=True)(data=data).content
            self.assertEqual(yaml.load(content), data)

    def test_http_renderer(self):
        with self.subTest(src_text='str pass'):
            data = 'test'
            content = djburger.r.HTTP()(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='bytes pass'):
            data = b'test'
            content = djburger.r.HTTP()(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='int pass'):
            data = 123
            content = djburger.r.HTTP()(data=data).content
            self.assertEqual(content, b'123')
        with self.subTest(src_text='list pass'):
            data = [1, 2, '3']
            content = djburger.r.HTTP()(data=data).content
            self.assertEqual(content, b'123')
        with self.subTest(src_text='dict not pass'):
            data = {'test': 'me'}
            with self.assertRaises(ValueError):
                content = djburger.r.HTTP()(data=data)

    def test_redirect_renderer(self):
        with self.subTest(src_text='url by init: code'):
            data = '/login/'
            code = djburger.r.Redirect()(data=data).status_code
            self.assertEqual(code, 302)
        with self.subTest(src_text='url by init: url'):
            data = '/login/'
            url = djburger.r.Redirect()(data=data).url
            self.assertEqual(url, '/login/')

    def test_exception_renderer(self):
        with self.subTest(src_text='ValidationError'):
            with self.assertRaises(ValidationError):
                djburger.r.Exception()(data='test')
        with self.subTest(src_text='AssertionError'):
            with self.assertRaises(AssertionError):
                djburger.r.Exception(AssertionError)(data='test')

    def test_rest_framework_renderer(self):
        with self.subTest(src_text='str pass'):
            renderer = djburger.r.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = 'test'
            content = renderer(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='bytes pass'):
            renderer = djburger.r.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = b'test'
            content = renderer(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='int pass'):
            renderer = djburger.r.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = 123
            content = renderer(data=data).content
        with self.subTest(src_text='list pass'):
            renderer = djburger.r.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = [1, 2, '3']
            content = renderer(data=data).content
            self.assertEqual(content, b'123')

    def test_tablib_renderer(self):
        with self.subTest(src_text='table csv'):
            data = [[1,2,3], [4,5,6]]
            content = djburger.r.Tablib('csv')(data=data).content
            self.assertEqual(content.split(), [b'1,2,3', b'4,5,6'])
        with self.subTest(src_text='table json'):
            data = [[1,2,3], [4,5,6]]
            content = djburger.r.Tablib('json')(data=data).content
            self.assertEqual(json.loads(content.decode('utf-8')), data)


class TestControllers(unittest.TestCase):

    def test_objects_controllers(self):
        # PREPARE
        name = 'TEST_IT'
        name2 = 'TEST_IT_FIX'
        Group.objects.filter(name=name).delete()
        Group.objects.filter(name=name2).delete()
        # ADD
        with self.subTest(src_text='add'):
            controller = djburger.c.Add(model=Group)
            response = controller(request=None, data={'name': name})
            self.assertEqual(response.name, name)
        # EDIT
        with self.subTest(src_text='edit'):
            controller = djburger.c.Edit(model=Group)
            response = controller(request=None, data={'name': name2}, name=name)
            self.assertEqual(response.name, name2)
        # LIST
        with self.subTest(src_text='list'):
            controller = djburger.c.List(model=Group)
            response = controller(request=None, data={})
            names = response.values_list('name', flat=True)
            self.assertIn(name2, names)
        with self.subTest(src_text='list filter'):
            controller = djburger.c.List(model=Group)
            response = controller(request=None, data={'name': name2})
            names = response.values_list('name', flat=True)
            self.assertIn(name2, names)
        # INFO
        with self.subTest(src_text='info'):
            controller = djburger.c.Info(model=Group)
            response = controller(request=None, data={}, name=name2)
            self.assertEqual(response.name, name2)
        # DELETE
        with self.subTest(src_text='delete'):
            controller = djburger.c.Delete(model=Group)
            response = controller(request=None, data={}, name=name2)
            self.assertEqual(response, 1)

    def test_wrapper(self):
        def base(request, **kwargs):
            data = request.GET.copy()
            data.update(request.POST)
            data.update(kwargs)
            data = list(data.items())
            data.sort()
            return HttpResponse(data)

        factory = RequestFactory()
        controller = djburger.c.ViewAsController(base)

        with self.subTest(src_text='get'):
            request = factory.get('/some/url/', {'test': 'me'})
            response = controller(request=request, data=request.GET)
            self.assertEqual(response, b"('test', 'me')")
        with self.subTest(src_text='get'):
            request = factory.post('/some/url/', {'test': 'me'})
            response = controller(request=request, data=request.POST)
            self.assertEqual(response, b"('test', 'me')")
        with self.subTest(src_text='kwargs'):
            request = factory.get('/some/url/')
            response = controller(request=request, data=request.GET, test='me')
            self.assertEqual(response, b"('test', 'me')")


class TestSideValidators(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        Wrapped = djburger.v.w.Marshmallow(Base)
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
        Wrapped = djburger.v.w.RESTFramework(Base)
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
                {'name': str, 'permissions': [], 'id': int},
                policy='drop'
            )
            v = v(request=None, data=self.obj)
            v.is_valid()
            self.assertTrue(v.is_valid())


if __name__ == '__main__':
    unittest.main()
