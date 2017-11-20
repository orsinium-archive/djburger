# DjBurger

Documentation on other languages:
* [Russian](README.ru.md)

**DjBurger** -- patched views format for big projects on Django.

Dataflow:
1. **Decorators**.
2. **Validator**.
3. **ErrorSerializer**.
4. **Controller**.
5. **PostValidator**.
7. **Serializer**.

Required only Controller and Serializer.

Rules format:

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
    'get': djburger.rule(
        decorators=[login_required],
            validators=[
                SomeDjangoForm,	            # Validator
                djburger.v.IsStrValidator,  # PostValidator
            ],
            controller=lambda request, data, **kwargs: 'Hello, World!',
            serializers=[
                djburger.s.JSONSerializer,          # ErrorSerializer
                djburger.s.ExceptionSerializer,     # ErrorResponseSerializer
                djburger.s.TemplateSerializer(      # Serializer
                    template_name='index.html',
                ),
            ]
        ),
    }
```
Or more strict format by `Rule` object:

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
        'get': djburger.Rule(
            decorators=[login_required],
            validator=SomeDjangoForm,
            controller=lambda request, data, **kwargs: 'Hello, World!',
            post_validator=djburger.v.IsStrValidator,
            error_serializer=djburger.s.JSONSerializer,
            response_error_serializer=djburger.s.ExceptionSerializer,
            serializer=djburger.s.TemplateSerializer(template_name='index.html'),
        ),
    }
```

Or shorter:

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
        'get': djburger.Rule(
            [login_required],
            SomeDjangoForm,
            lambda request, data, **kwargs: 'Hello, World!',
            djburger.v.IsStrValidator,
            djburger.s.JSONSerializer,
            djburger.s.ExceptionSerializer,
            djburger.s.TemplateSerializer(template_name='index.html'),
        ),
    }
```

## Installation

By pip:

```bash
sudo pip install -e git+https://github.com/orsinium/djburger.git#egg=djburger
```

Or add into `requirements.txt`:

```bash
-e git+https://github.com/orsinium/djburger.git#egg=djburger
```

And then run `sudo pip install -r requirements.txt`


## More info

1. View [example project](example) or [tests](tests.py)
2. Full documentation for all components into [source](djburger) docstrings.
