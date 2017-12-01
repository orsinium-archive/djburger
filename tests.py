# -*- coding: utf-8 -*-

# built-in
import os
import sys
import unittest
# external
from pyschemes import Scheme as PySchemes
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
            v = djburger.v.c.Chain(validators=[
                djburger.v.c.IsInt,
                djburger.v.c.Lambda(key=lambda data: data > 0),
            ])
            v = v(4)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='lambda int not pass'):
            v = djburger.v.c.Chain(validators=[
                djburger.v.c.IsInt,
                djburger.v.c.Lambda(key=lambda data: data > 0),
            ])
            v = v(-4)
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='lambda str not pass'):
            v = djburger.v.c.Chain(validators=[
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

    def test_pyschemes(self):
        # BASE
        with self.subTest(src_text='base pass'):
            v = djburger.v.b.PySchemes([str, 2, int])
            v = v(request=None, data=['3', 2, 4])
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            v = djburger.v.b.PySchemes([str, 2, int])
            v = v(request=None, data=[1, 2, 4])
            self.assertFalse(v.is_valid())
        with self.subTest(src_text='base int data'):
            v = djburger.v.b.PySchemes(int)
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


if __name__ == '__main__':
    unittest.main()
