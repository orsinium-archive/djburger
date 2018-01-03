# built-in
from __main__ import unittest, djburger
# external
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.test import RequestFactory


class DjangoControllersTest(unittest.TestCase):

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
            self.assertEqual(response.replace(b"u'", b"'"), b"('test', 'me')")
        with self.subTest(src_text='get'):
            request = factory.post('/some/url/', {'test': 'me'})
            response = controller(request=request, data=request.POST)
            self.assertEqual(response.replace(b"u'", b"'"), b"('test', 'me')")
        with self.subTest(src_text='kwargs'):
            request = factory.get('/some/url/')
            response = controller(request=request, data=request.GET, test='me')
            self.assertEqual(response.replace(b"u'", b"'"), b"('test', 'me')")

    def test_subcontroller(self):
        with self.subTest(src_text='pre pass'):
            c = djburger.c.subcontroller(
                prev=djburger.v.c.IsStr,
                c=lambda data, request, **kwargs: data,
            )
            data = 'lol'
            result = c(data=data)
            self.assertEqual(result, data)
        with self.subTest(src_text='post pass'):
            c = djburger.c.subcontroller(
                c=lambda data, request, **kwargs: data,
                postv=djburger.v.c.IsStr,
            )
            data = 'lol'
            result = c(data=data)
            self.assertEqual(result, data)
        with self.subTest(src_text='pre not pass'):
            c = djburger.c.subcontroller(
                prev=djburger.v.c.IsStr,
                c=lambda data, request, **kwargs: data,
            )
            data = 123
            with self.assertRaises(djburger.e.SubValidationError):
                result = c(data=data)
