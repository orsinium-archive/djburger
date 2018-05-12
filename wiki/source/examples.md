# Examples

## Views

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            controller=lambda request, data, **kwargs: 'Hello, World!',  # controller
            postvalidator=djburger.validators.c.IsStr,                           # post-validator
            postrenderer=djburger.renderers.Exception(),                       # post-renderer
            renderer=djburger.renderers.Template(template_name='index.html'),  # renderer
        ),
    }
```

Minimum info:

```python
class ExampleView(djburger.ViewBase):
    default_rule = djburger.rule(
        controller=lambda request, data, **kwargs: 'Hello, World!',
        renderer=djburger.renderers.Template(template_name='index.html'),
    ),
```

All requests without the method defined in the ``rules`` will use the rule from ``default_rule``.

Example:

```python
class UsersView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            decorators=[login_required, csrf_exempt],
            prevalidator=SomeValidator,
            controller=djburger.controllers.List(model=User),
            postvalidator=djburger.validators.c.QuerySet,
            postrenderer=djburger.renderers.Exception(),
            renderer=djburger.renderers.JSON(),
        ),
        'put': djburger.rule(
            decorators=[csrf_exempt],
            p=djburger.p.JSON(),
            prevalidator=SomeOtherValidator,
            controller=djburger.controllers.Add(model=User),
            renderer=djburger.renderers.JSON(),
        ),
    }
```


## Validators

Simple base validator:

```python
class GroupInputValidator(djburger.validators.b.Form):
    name = djburger.f.CharField(label='Name', max_length=80)
```

`djburger.f` is just alias for `django.forms`.

Simple wrapper:

```python
import djburger
from django import forms

class GroupInputForm(forms.Form):
    name = forms.CharField(label='Name', max_length=80)

Validator = djburger.validators.w.Form(GroupInputForm)
```

See [usage](usage.html) for more examples and explore [example project](https://github.com/orsinium/djburger/tree/master/example).
