from __main__ import unittest
from .validators.pre import prevalidators
from .validators.post import postvalidators


validators = prevalidators + postvalidators


class ValidatorsTest(unittest.TestCase):
    def test_valid(self):
        data = {
            'name': 'Max',
            'mail': 'test@example.ru',
            'count': 20,
        }
        for validator in validators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=data)
                self.assertTrue(v.is_valid())
                self.assertEqual(v.cleaned_data, data)

    def test_no_field(self):
        data = {
            'name': 'Max',
            'mail': 'test@example.ru',
        }
        for validator in validators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=data)
                self.assertFalse(v.is_valid())
                self.assertTrue(v.errors)

    def test_invalid_int(self):
        data = {
            'name': 'Max',
            'mail': 'test@example.ru',
            'count': 'lol',
        }
        for validator in validators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=data)
                self.assertFalse(v.is_valid())
                self.assertTrue(v.errors)


class PreValidatorsTest(unittest.TestCase):
    def test_types_converting(self):
        data = {
            'name': 'Max',
            'mail': 'test@example.ru',
            'count': '10',
        }
        for validator in prevalidators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=data)
                self.assertTrue(v.is_valid())
                self.assertFalse(v.errors)
                self.assertIn('count', v.cleaned_data)
                self.assertEqual(v.cleaned_data['count'], 10)

    def test_explicit_keys(self):
        data = {
            'name': 'Max',
            'mail': 'test@example.ru',
            'count': 10,
            'junk': 'test',
        }
        for validator in prevalidators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=data)
                self.assertTrue(v.is_valid())
                self.assertFalse(v.errors)
                self.assertNotIn('junk', v.cleaned_data)
