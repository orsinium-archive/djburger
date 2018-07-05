# built-in
from __main__ import unittest
from .validators.djpost import postvalidators as validators
# external
from django.test import TestCase
from django.contrib.auth.models import Group


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

    def test_obj_serializing(self):
        for validator in validators:
            with self.subTest(validator=validator.__class__.__name__):
                v = validator(request=True, data=self.obj)
                self.assertTrue(v.is_valid())
                self.assertFalse(v.errors)
                self.assertIn('id', v.cleaned_data)
                self.assertIn('name', v.cleaned_data)
                self.assertEqual(v.cleaned_data['name'], 'TEST_IT')
