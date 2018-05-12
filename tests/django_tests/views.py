# built-in
from __main__ import unittest
# external
from django.test import RequestFactory
# project
import djburger # noQA


class DjangoViewsTest(unittest.TestCase):

    def test_controller(self):
        class Base(djburger.ViewBase):
            default_rule = djburger.rule(
                controller=lambda request, data, **kwargs: data,
                renderer=lambda data, **kwargs: data,
            )

        view = Base.as_view()
        factory = RequestFactory()
        data = {'test': 'me', 'list': ['1', '2', '3']}
        request = factory.get('/some/url/', data)
        response = view(request)
        self.assertEqual(response, data)

    def test_validator(self):
        class Validator(djburger.validators.b.Form):
            name = djburger.f.CharField(max_length=20)
            mail = djburger.f.EmailField()
            themes = djburger.f.MultipleChoiceField(choices=(
                (1, 'one'),
                (2, 'two'),
                (3, 'three'),
            ))

        class Base(djburger.ViewBase):
            default_rule = djburger.rule(
                prevalidator=Validator,
                controller=lambda request, data, **kwargs: data,
                renderer=lambda **kwargs: kwargs,
            )

        view = Base.as_view()
        factory = RequestFactory()
        with self.subTest(src_text='form pass'):
            data = {
                'name': 'John Doe',
                'mail': 'example@gmail.com',
                'themes': ['1', '2'],
            }
            request = factory.get('/some/url/', data)
            response = view(request)
            self.assertEqual(response['data'], data)
        with self.subTest(src_text='form not pass'):
            data = {
                'name': 'John Doe',
                'mail': 'example.gmail.com',
                'themes': ['1', '2', '4'],
            }
            request = factory.get('/some/url/', data)
            response = view(request)
            errors = set(response['validator'].errors.keys())
            self.assertEqual(errors, {'themes', 'mail'})

    def test_postvalidator(self):
        class Validator(djburger.validators.b.Form):
            name = djburger.f.CharField(max_length=20)
            mail = djburger.f.EmailField()
            themes = djburger.f.MultipleChoiceField(choices=(
                (1, 'one'),
                (2, 'two'),
                (3, 'three'),
            ))

        class Base(djburger.ViewBase):
            default_rule = djburger.rule(
                controller=lambda request, data, **kwargs: data,
                postvalidator=Validator,
                renderer=lambda **kwargs: kwargs,
            )

        view = Base.as_view()
        factory = RequestFactory()
        with self.subTest(src_text='form pass'):
            data = {
                'name': 'John Doe',
                'mail': 'example@gmail.com',
                'themes': ['1', '2'],
            }
            request = factory.get('/some/url/', data)
            response = view(request)
            self.assertEqual(response['data'], data)
        with self.subTest(src_text='form not pass'):
            data = {
                'name': 'John Doe',
                'mail': 'example.gmail.com',
                'themes': ['1', '2', '4'],
            }
            request = factory.get('/some/url/', data)
            response = view(request)
            errors = set(response['validator'].errors.keys())
            self.assertEqual(errors, {'themes', 'mail'})
