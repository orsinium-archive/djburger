DjBurger
========

Documentation on other languages:

-  `Russian <README.ru.md>`__

**DjBurger** -- patched views format for big projects on Django.

Key principes:

1. Validation only before main logic.
2. Reusable logic for many views.
3. Reusable input and output data formats.
4. More clear views.

Dataflow:

1. **Decorators** (``d``).
2. **Parser** (``p``). Parse request body.
3. **PreValidator** (``prev``). Validate and clear request.
4. **PreRenderer** (``prer``). Render and return PreValidation errors.
5. **Controller** (``c``). Main logic: do some things.
6. **PostValidator** (``postv``). Validate and clear response.
7. **PostRenderer** (``postr``). Render and return PostValidation
   errors.
8. **Renderer** (``r``). Render successfull response.

.. figure:: scheme.png
   :alt: Scheme

   Scheme

Required only Controller and Renderer.

Installation
------------

STABLE
~~~~~~

.. code:: bash

    pip install djburger

DEV
~~~

Using pip:

.. code:: bash

    sudo pip install -e git+https://github.com/orsinium/djburger.git#egg=djburger

In ``requirements.txt``:

.. code:: bash

    -e git+https://github.com/orsinium/djburger.git#egg=djburger

Components
----------

Main components:

1. **Validators** (``djburger.v``). Can be used as ``prev`` and
   ``postv``.

   1. **Bases** (``djburger.v.b``).
   2. **Constructors** (``djburger.v.c``).
   3. **Wrappers** (``djburger.v.w``)

2. **Controllers** (``djburger.c``). Can be used as ``c``.
3. **Renderer** (``djburger.r``). Can be used as ``prer``, ``postr`` and
   ``r``.

Some additional components:

1. ``djburger.exceptions`` -- useful exceptions.

Interfaces
----------

1. **Decorator**. Any decorator which can wrap Django view
2. **Validator**. Have same interfaces as Django Forms, but get
   ``request`` by initialization:

   1. ``.__init__()``

      -  ``request`` -- Request object
      -  ``data`` -- data from user (prev) or controller (postv)
      -  ``**kwargs`` -- any keyword arguments for validator

   2. ``.is_valid()`` -- return True if data is valid False otherwise.
   3. ``.errors`` -- errors if data is invalid.
   4. ``.cleaned_data`` -- cleaned data if input data is valid.

3. **Controller**. Any callable object. Kwargs:

   1. ``request`` -- Request object.
   2. ``data`` -- validated request data. 3 ``**kwargs`` -- kwargs from
      url.

4. **Renderer**. Any callable object. Kwargs:

   1. ``request`` -- Request object.
   2. ``data`` -- validated controller data (only for ``r``).
   3. ``validator`` -- validator which not be passed (only for ``prer``
      and ``postr``).
   4. ``status_code`` -- HTTP status code if validator raise
      ``djburger.e.StatusCodeError``.

Usage example
-------------

View definition:

.. code:: python

    import djburger

    class ExampleView(djburger.ViewBase):
        rules = {
            'get': djburger.rule(
                c=lambda request, data, **kwargs: 'Hello, World!',
                postv=djburger.v.c.IsStrValidator,
                postr=djburger.s.ExceptionSerializer,
                r=djburger.r.Template(template_name='index.html'),
            ),
        }

External libraries support
--------------------------

-  `Django REST Framework <django-rest-framework.org>`__

   -  ``djburger.v.b.RESTFramework``
   -  ``djburger.v.w.RESTFramework``
   -  ``djburger.r.RESTFramework``

-  `Marshmallow <https://github.com/marshmallow-code/marshmallow>`__

   -  ``djburger.v.b.Marshmallow``
   -  ``djburger.v.w.Marshmallow``

-  `PySchemes <https://github.com/shivylp/pyschemes>`__

   -  ``djburger.v.c.PySchemes``
   -  ``djburger.v.w.PySchemes``

-  `PyYAML <https://github.com/yaml/pyyaml>`__

   -  ``djburger.r.YAML``

-  `Tablib <https://github.com/kennethreitz/tablib>`__

   -  ``djburger.r.Tablib``

-  `BSON <https://github.com/py-bson/bson>`__

   -  ``djburger.p.BSON``
   -  ``djburger.r.BSON``
