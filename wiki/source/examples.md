# Examples

## Views

```python
import djburger

class ExampleView(djburger.ViewBase):
    rules = {
        'get': djburger.rule(
            c=lambda request, data, **kwargs: 'Hello, World!',  # controller
            postv=djburger.v.c.IsStr,                           # post-validator
            postr=djburger.r.Exception(),                       # post-renderer
            r=djburger.r.Template(template_name='index.html'),  # renderer
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

All requests without the method defined in the ``rules`` will use the rule from ``default_rule``.

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


## Validators

Simple base validator:

```python
class GroupInputValidator(djburger.v.b.Form):
    name = djburger.f.CharField(label='Name', max_length=80)
```

`djburger.f` is just alias for `django.forms`.

Simple wrapper:

```python
import djburger
from django import forms

class GroupInputForm(forms.Form):
    name = forms.CharField(label='Name', max_length=80)

Validator = djburger.v.w.Form(GroupInputForm)
```

See [usage](usage.html) for more examples and explore [example project](https://github.com/orsinium/djburger/tree/master/example).
