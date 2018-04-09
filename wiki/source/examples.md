# Examples

## View

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
