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

    def test_bson_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.r.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='int'):
            data = -13
            content = djburger.r.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='dict'):
            data = {'lol': 1516}
            content = djburger.r.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='list'):
            data = [1, 2, 3]
            content = djburger.r.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='mixed'):
            data = {'data': [1, 2, 3]}
            content = djburger.r.BSON(flat=False)(data=data).content
            self.assertEqual(bson.loads(content), {'data': data})
        with self.subTest(src_text='flat'):
            data = {'lol': 1516}
            content = djburger.r.BSON(flat=True)(data=data).content
            self.assertEqual(bson.loads(content), data)

    def test_yaml_renderer(self):
        with self.subTest(src_text='str'):
            data = 'test'
            content = djburger.r.YAML(flat=False)(data=data).content
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
            data = [[1, 2, 3], [4, 5, 6]]
            content = djburger.r.Tablib('csv')(data=data).content
            self.assertEqual(content.split(), [b'1,2,3', b'4,5,6'])
        with self.subTest(src_text='table json'):
            data = [[1, 2, 3], [4, 5, 6]]
            content = djburger.r.Tablib('json')(data=data).content
            self.assertEqual(json.loads(content.decode('utf-8')), data)
