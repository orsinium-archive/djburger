# DjBurger

Documentation on other languages:

* [Russian](README.ru.md)

**DjBurger** -- patched views format for big projects on Django.


Key principles:

1. Validation only before main logic.
2. Reusable logic for many views.
3. Reusable input and output data formats.
4. More clear views.


Dataflow:

1. **Decorators** (`d`).
2. **Parser** (`p`). Parse request body.
3. **PreValidator** (`prev`). Validate and clear request.
4. **PreRenderer** (`prer`). Render and return PreValidation errors.
5. **Controller** (`c`). Main logic: do some things.
6. **PostValidator** (`postv`). Validate and clear response.
7. **PostRenderer** (`postr`). Render and return PostValidation errors.
8. **Renderer** (`r`). Render successfull response.

![Scheme](scheme.png)

Required only Controller and Renderer.


## Installation

### STABLE

```bash
pip install djburger
```

### DEV

Using pip:

```bash
sudo pip install -e git+https://github.com/orsinium/djburger.git#egg=djburger
```

In `requirements.txt`:

```bash
-e git+https://github.com/orsinium/djburger.git#egg=djburger
```

## Components

Main components:

1. **Parsers** (`djburger.p`).
2. **Validators** (`djburger.v`). Can be used as `prev` and `postv`.
    1. **Bases** (`djburger.v.b`).
    2. **Constructors** (`djburger.v.c`).
    3. **Wrappers** (`djburger.v.w`)
3. **Controllers** (`djburger.c`). Can be used as `c`.
4. **Renderers** (`djburger.r`). Can be used as `prer`, `postr` and `r`.


Some additional components:

1. `djburger.exceptions` -- useful exceptions.


## Interfaces

1. **Decorator**. Any decorator which can wrap Django view
2. **Parser**. Any callable object which get request object and return parsed data.
3. **Validator**. Have same interfaces as Django Forms, but get `request` by initialization:
    1. `.__init__()`
        * `request` -- Request object
        * `data` -- data from user (prev) or controller (postv)
        * `**kwargs` -- any keyword arguments for validator
    2. `.is_valid()` -- return True if data is valid False otherwise.
    3. `.errors` -- errors if data is invalid.
    4. `.cleaned_data` -- cleaned data if input data is valid.
4. **Controller**. Any callable object. Kwargs:
    1. `request` -- Request object.
    2. `data` -- validated request data.
    3 `**kwargs` -- kwargs from url.
5. **Renderer**. Any callable object. Kwargs:
    1. `request` -- Request object.
    2. `data` -- validated controller data (only for `r`).
    3. `validator` -- validator which not be passed (only for `prer` and `postr`).
    4. `status_code` -- HTTP status code if validator raise `djburger.e.StatusCodeError`.


## Usage example

View definition:

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            c=lambda request, data, **kwargs: 'Hello, World!',
            postv=djburger.v.c.IsStr,
            postr=djburger.r.Exception(),
            r=djburger.r.Template(template_name='index.html'),
        ),
    }
```

Minimum info:

```python
class ExampleView(djburger.ViewBase):
    default_rule = djburger.rule(
        c=lambda request, data, **kwargs: 'Hello, World!',
        r=djburger.r.Template(template_name='index.html'),
    ),
```

Rule from `default_rule` will be used as rule for all requests, which method not definited in `rules`.

Big example:

```python
class UsersView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            d=[login_required, csrf_exempt],
            prev=SomeValidator,
            c=djburger.c.List(model=User),
            postv=djburger.v.c.QuerySet,
            postr=djburger.r.Exception(),
            r=djburger.r.JSON(),
        ),
        'put': djburger.rule(
            d=[csrf_exempt],
            p=djburger.p.JSON(),
            prev=SomeOtherValidator,
            c=djburger.c.Add(model=User),
            r=djburger.r.JSON(),
        ),
    }
```


## External libraries support

* [BSON](https://github.com/py-bson/bson)
    * `djburger.p.BSON`
    * `djburger.r.BSON`
* [Django REST Framework](django-rest-framework.org)
    * `djburger.v.b.RESTFramework`
    * `djburger.v.w.RESTFramework`
    * `djburger.r.RESTFramework`
* [Marshmallow](https://github.com/marshmallow-code/marshmallow)
    * `djburger.v.b.Marshmallow`
    * `djburger.v.w.Marshmallow`
* [PySchemes](https://github.com/shivylp/pyschemes)
    * `djburger.v.c.PySchemes`
    * `djburger.v.w.PySchemes`
* [PyYAML](https://github.com/yaml/pyyaml)
    * `djburger.r.YAML`
* [Tablib](https://github.com/kennethreitz/tablib)
    * `djburger.r.Tablib`


## What's next?

1. Read [documentation](https://djburger.readthedocs.io/en/latest/), source code docstrings or just inspect djburger from python console (for example, `help('djburger.views')`).
2. See [example](example/) project.
3. If you have some questions then [view issues](https://github.com/orsinium/djburger/issues) or [create new](https://github.com/orsinium/djburger/issues/new).
4. If you found some mistakes then fix it and [create Pull Request](https://github.com/orsinium/djburger/compare). Contributors are welcome.
5. [Star this project on github](https://github.com/orsinium/djburger) :)
