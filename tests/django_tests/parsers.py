# built-in
import json
from __main__ import unittest, djburger
# external
import bson
from django.test import RequestFactory


class DjangoParsersTest(unittest.TestCase):

    def test_dict_parser(self):
        factory = RequestFactory()
        with self.subTest(src_text='mixed'):
            data = {
                'name': 'John Doe',
                'mail': 'example.gmail.com',
                'themes': ['1', '2', '4'],
            }
            request = factory.get('/some/url/', data)
            p = djburger.parsers.DictMixed()
            parsed_data = p(request)
            self.assertEqual(parsed_data, data)

    def test_json_parser(self):
        factory = RequestFactory()
        with self.subTest(src_text='mixed'):
            data = {
                'name': 'John Doe',
                'mail': 'example.gmail.com',
                'themes': ['1', '2', '4'],
            }
            request = factory.post(
                '/some/url/',
                data=json.dumps(data),
                content_type='application/json',
            )
            p = djburger.parsers.JSON()
            parsed_data = p(request)
            self.assertEqual(parsed_data, data)

    def test_bson_parser(self):
        factory = RequestFactory()
        with self.subTest(src_text='mixed'):
            data = {
                'name': 'John Doe',
                'mail': 'example.gmail.com',
                'themes': ['1', '2', '4'],
            }
            request = factory.post(
                '/some/url/',
                data=bson.dumps(data),
                content_type='application/json',
            )
            p = djburger.parsers.BSON()
            parsed_data = p(request)
            self.assertEqual(parsed_data, data)
