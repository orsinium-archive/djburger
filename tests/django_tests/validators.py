# built-in
from __main__ import unittest, djburger
# external
from django.contrib.auth.models import Group


class DjangoFormValidatorsTest(unittest.TestCase):

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

    def test_base_validator(self):
        class Base(djburger.validators.bases.Form):
            name = djburger.forms.CharField(max_length=20)
            mail = djburger.forms.EmailField()
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Base(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Base(request=None, data=data)
            self.assertFalse(v.is_valid())

    def test_wrapper_validator(self):
        class Base(djburger.forms.Form):
            name = djburger.forms.CharField(max_length=20)
            mail = djburger.forms.EmailField()
        Wrapped = djburger.validators.wrappers.Form(Base) # noQA
        with self.subTest(src_text='base pass'):
            data = {'name': 'John Doe', 'mail': 'test@gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertTrue(v.is_valid())
        with self.subTest(src_text='base not pass'):
            data = {'name': 'John Doe', 'mail': 'test.gmail.com'}
            v = Wrapped(request=None, data=data)
            self.assertFalse(v.is_valid())
