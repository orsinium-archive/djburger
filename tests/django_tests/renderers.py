# built-in
import json
from __main__ import unittest, djburger
# external
import bson
from django.core.exceptions import ValidationError
import yaml


# import only after django.setup()
from rest_framework import renderers as rest_framework_renderers # noQA


class DjangoRenderersTest(unittest.TestCase):

    def test_json_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.renderers.JSON()(data=data).content
            self.assertEqual(content, b'"test"')
        with self.subTest(src_text='int'):
            data = -13
            content = djburger.renderers.JSON()(data=data).content
            self.assertEqual(content, b'-13')
        with self.subTest(src_text='dict'):
            data = {'data': 1516}
            content = djburger.renderers.JSON()(data=data).content
            self.assertEqual(content, b'{"data": 1516}')
        with self.subTest(src_text='list'):
            data = [1, 2, 3]
            content = djburger.renderers.JSON()(data=data).content
            self.assertEqual(content, b'[1, 2, 3]')
        with self.subTest(src_text='mixed'):
            data = {'data': [1, 2, 3]}
            content = djburger.renderers.JSON()(data=data).content
            self.assertEqual(content, b'{"data": [1, 2, 3]}')
        with self.subTest(src_text='non-flat'):
            data = 1516
            content = djburger.renderers.JSON(flat=False)(data=data).content
            self.assertEqual(content, b'{"data": 1516}')

    def test_bson_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.renderers.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='int'):
            data = -13
            content = djburger.renderers.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='dict'):
            data = {'lol': 1516}
            content = djburger.renderers.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='list'):
            data = [1, 2, 3]
            content = djburger.renderers.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='mixed'):
            data = {'data': [1, 2, 3]}
            content = djburger.renderers.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='flat'):
            data = {'lol': 1516}
            content = djburger.renderers.BSON(flat=True)(data=data).content
            self.assertEqual(bson.loads(content), data)

    def test_yaml_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.renderers.YAML(flat=False)(data=data).content
            self.assertEqual(yaml.load(content), {'data': data})
        with self.subTest(src_text='mixed'):
            data = [1, '2', [3, 4], {5: 6}]
            content = djburger.renderers.YAML(flat=True)(data=data).content
            self.assertEqual(yaml.load(content), data)

    def test_http_renderer(self):
        with self.subTest(src_text='str pass'):
            data = 'test'
            content = djburger.renderers.HTTP()(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='bytes pass'):
            data = b'test'
            content = djburger.renderers.HTTP()(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='int pass'):
            data = 123
            content = djburger.renderers.HTTP()(data=data).content
            self.assertEqual(content, b'123')
        with self.subTest(src_text='list pass'):
            data = [1, 2, '3']
            content = djburger.renderers.HTTP()(data=data).content
            self.assertEqual(content, b'123')
        with self.subTest(src_text='dict not pass'):
            data = {'test': 'me'}
            with self.assertRaises(ValueError):
                content = djburger.renderers.HTTP()(data=data)

    def test_redirect_renderer(self):
        with self.subTest(src_text='url by init: code'):
            data = '/login/'
            code = djburger.renderers.Redirect()(data=data).status_code
            self.assertEqual(code, 302)
        with self.subTest(src_text='url by init: url'):
            data = '/login/'
            url = djburger.renderers.Redirect()(data=data).url
            self.assertEqual(url, '/login/')

    def test_exception_renderer(self):
        with self.subTest(src_text='ValidationError'):
            with self.assertRaises(ValidationError):
                djburger.renderers.Exception()(data='test')
        with self.subTest(src_text='AssertionError'):
            with self.assertRaises(AssertionError):
                djburger.renderers.Exception(AssertionError)(data='test')

    def test_rest_framework_renderer(self):
        with self.subTest(src_text='str pass'):
            renderer = djburger.renderers.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = 'test'
            content = renderer(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='bytes pass'):
            renderer = djburger.renderers.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = b'test'
            content = renderer(data=data).content
            self.assertEqual(content, b'test')
        with self.subTest(src_text='int pass'):
            renderer = djburger.renderers.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = 123
            content = renderer(data=data).content
        with self.subTest(src_text='list pass'):
            renderer = djburger.renderers.RESTFramework(
                renderer=rest_framework_renderers.StaticHTMLRenderer()
            )
            data = [1, 2, '3']
            content = renderer(data=data).content
            self.assertEqual(content, b'123')

    def test_tablib_renderer(self):
        with self.subTest(src_text='table csv'):
            data = [[1, 2, 3], [4, 5, 6]]
            content = djburger.renderers.Tablib('csv')(data=data).content
            self.assertEqual(content.split(), [b'1,2,3', b'4,5,6'])
        with self.subTest(src_text='table json'):
            data = [[1, 2, 3], [4, 5, 6]]
            content = djburger.renderers.Tablib('json')(data=data).content
            self.assertEqual(json.loads(content.decode('utf-8')), data)
