# Usage

## Components structure

Use short notation from [dataflow](philosophy.html#dataflow).

DjBurger modules:

+ `djburger.p`. Parsers. Can be used as `p`.
+ `djburger.v`. Validators. Can be used as `prev` and `postv`.
  + `djburger.v.b`. Validators that can be used as **base** class for your own validators.
  + `djburger.v.c`. Validators that can be used as **constructors** for simple validators.
  + `djburger.v.w`. Validators that can be used as **wrappers** for external validators.
+ `djburger.c`. Controllers. Can be used as `c`.
+ `djburger.r`. Renderers. Can be used as `prer`, `postr` and `r`.
+ `djburger.e`. Exceptions.

Keyword arguments for `djburger.rule`:

1. `d` -- decorators list. Optional.
1. `p` -- parser. `djburger.p.Default` by default.
1. `prev` -- pre-validator. Optional.
1. `prer` -- renderer for pre-validator. If missed then `r` will be used for pre-validation errors rendering.
1. `c` -- controller. Required.
1. `postv` -- post-validator. Optional.
1. `postr` -- renderer for post-validator. If missed then `r` will be used for post-validation errors rendering.
1. `r` -- renderer for success response. Required.


## View

1. Extend `djburger.ViewBase`
1. Set `rules` with HTTP-request names as keys and `djburger.rule` as values.
1. Set up your `djburger.rule` by passing components as kwargs.

Example:

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

More info:

1. [Dataflow](philosophy.html#dataflow)
1. [View usage examples](examples.html#view)
1. [Example project](https://github.com/orsinium/djburger/tree/master/example)
1. Сheck [views API](views.html), but `rules` attribute are sufficient and redefinition of methods is not required.


## Decorators

You can use any Django decorators like `csrf_exempt`. `djburger.ViewBase` wraps into decorators view's `validate_request` method that get `request` object, `**kwargs` from URL resolver and returns renderer's result (usually Django HttpResponse).

```python
d=[csrf_exempt]
```


## Parsers

Parser get `request` and return `data` which will be passed as is into pre-validator. Usually `data` has `dict` or [QueryDict](https://docs.djangoproject.com/en/2.0/ref/request-response/#django.http.QueryDict) interface. DjBurger use `djburger.p.Default` as default parser. See list of built-in parsers into [parsers API](parsers.html).

```python
p=djburger.p.JSON()
```


## Validators

Validators get data and validate it. They have Django Forms-like interface. See [interfaces](interfaces.html) and [interface API](validators.html#djburger.validators.bases.IValidator) for details.

[Base validators](validators.html#module-djburger.validators.bases) - base class for your schemes:

```python
from django import forms

class Validator(djburger.v.b.Form):
    name = forms.CharField(max_length=20)

...
prev=Validator
...
```

[Wrappers](validators.html#module-djburger.validators.wrappers) wrap external validators for DjBurger usage:

```python
from django import forms

class DjangoValidator(forms.Form):
    name = forms.CharField(max_length=20)

...
prev=djburger.v.w.Form(DjangoValidator)
...
```

And [constructors](validators.html#module-djburger.validators.constructors) for quick constructing simple validators. You can validate anything with constructors, but recommended case - one-line validators.


```python
prev=djburger.v.c.IsDict
```


How to choose validator type:

1. `djburger.v.c` -- for one-line simple validation.
1. `djburger.v.w` -- for using validators which also used into non-DjBurger components.
1. `djburger.v.b` -- for any other cases.


## Controllers

Controller -- any callable object which get `request` object, `data` and `**kwargs` from URL resolver and return any `data`. Usually you will use your own controllers.

```python
def echo_controller(request, data, **kwargs):
    return data

...
c=echo_controller
...
```

Additionally DjBurger have [built-in controllers](controllers.html) for simple cases.

```python
c=djburger.c.Info(model=User)
```


## Renderers

Renderer get errors or cleaned data from validator and return [HttpResponse](https://docs.djangoproject.com/en/2.0/ref/request-response/#httpresponse-objects) or any other view result.

```python
postr=djburger.r.JSON()
```


## Exceptions

Raise `djburger.e.StatusCodeError` from validator if you want stop validation and return `errors`.

```python
from django import forms

class Validator(djburger.v.b.Form):
    name = forms.CharField(max_length=20)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name == 'admin':
            self.errors = {'__all__': ['User not found']}
            raise djburger.e.StatusCodeError(404, 'User not found')
        return name

...
prev=Validator
...
```


## SubControllers

If you need to validate data in controller, better use `djburger.c.subcontroller`:

```python
def get_name_controller(request, data, **kwargs):
    return data['name']

def echo_controller(request, data, **kwargs):
    subc = djburger.c.subcontroller(
        prev=djburger.c.IsDict,
        c=get_name_controller,
        postv=djburger.c.IsStr,
    )
    return subc(request, data, **kwargs)

...
c=echo_controller
...
```

If data passed to subcontroller is invalid then `djburger.e.SubValidationError` will be immediately raised. View catch error and pass error to `postr`.
