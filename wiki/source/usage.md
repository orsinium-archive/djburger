# Usage

## Components structure

DjBurger modules:

+ `djburger.parsers`. Parsers. Can be used as `parser`.
+ `djburger.validators`. Can be used as `prevalidator` and `postvalidator`.
  + `djburger.validators.bases`. Validators that can be used as base class for your own validators.
  + `djburger.validators.constructors`. Validators that can be used as constructors for simple validators.
  + `djburger.validators.wrappers`. Validators that can be used as wrappers for external validators.
+ `djburger.controllers`. Can be used as `controller`.
+ `djburger.renderers`. Can be used as `prerenderer`, `postrenderer` and `renderer`.
+ `djburger.exceptions`.

Keyword arguments for `djburger.rule`:

1. `decorators` -- decorators list. Optional.
1. `parser` -- parser. `djburger.parsers.Default` by default.
1. `prevalidator` -- pre-validator. Optional.
1. `prerenderer` -- renderer for pre-validator. If missed then `r` will be used for pre-validation errors rendering.
1. `controller` -- controller. Required.
1. `postvalidator` -- post-validator. Optional.
1. `postrenderer` -- renderer for post-validator. If missed then `r` will be used for post-validation errors rendering.
1. `renderer` -- renderer for success response. Required.


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
            controller=lambda request, data, **kwargs: 'Hello, World!',
            postvalidator=djburger.validators.constructors.IsStr,
            postrenderer=djburger.renderers.Exception(),
            renderer=djburger.renderers.Template(template_name='index.html'),
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
decorators=[csrf_exempt]
```


## Parsers

Parser get `request` and return `data` which will be passed as is into pre-validator. Usually `data` has `dict` or [QueryDict](https://docs.djangoproject.com/en/2.0/ref/request-response/#django.http.QueryDict) interface. DjBurger use `djburger.parsers.Default` as default parser. See list of built-in parsers into [parsers API](parsers.html).

```python
parser=djburger.parsers.JSON()
```


## Validators

Validators get data and validate it. They have Django Forms-like interface. See [interfaces](interfaces.html) and [interface API](validators.html#djburger.validators.bases.IValidator) for details.

[Base validators](validators.html#module-djburger.validators.bases) - base class for your schemes:

```python
from django import forms

class Validator(djburger.validators.bases.Form):
    name = forms.CharField(max_length=20)

...
prevalidator=Validator
...
```

[Wrappers](validators.html#module-djburger.validators.wrappers) wrap external validators for DjBurger usage:

```python
from django import forms

class DjangoValidator(forms.Form):
    name = forms.CharField(max_length=20)

...
prevalidator=djburger.validators.wrappers.Form(DjangoValidator)
...
```

And [constructors](validators.html#module-djburger.validators.constructors) for quick constructing simple validators. You can validate anything with constructors, but recommended case - one-line validators.


```python
prevalidator=djburger.validators.constructors.IsDict
```


How to choose validator type:

1. `djburger.validators.constructors` -- for one-line simple validation.
1. `djburger.validators.wrappers` -- for using validators which also used into non-DjBurger components.
1. `djburger.validators.bases` -- for any other cases.


## Controllers

Controller -- any callable object which get `request` object, `data` and `**kwargs` from URL resolver and return any `data`. Usually you will use your own controllers.

```python
def echo_controller(request, data, **kwargs):
    return data

...
controller=echo_controller
...
```

Additionally DjBurger have [built-in controllers](controllers.html) for simple cases.

```python
controller=djburger.controllers.Info(model=User)
```


## Renderers

Renderer get errors or cleaned data from validator and return [HttpResponse](https://docs.djangoproject.com/en/2.0/ref/request-response/#httpresponse-objects) or any other view result.

```python
postrenderer=djburger.renderers.JSON()
```


## Exceptions

Raise `djburger.exceptions.StatusCodeError` from validator if you want stop validation and return `errors`.

```python
from django import forms

class Validator(djburger.validators.bases.Form):
    name = forms.CharField(max_length=20)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name == 'admin':
            self.errors = {'__all__': ['User not found']}
            raise djburger.exceptions.StatusCodeError(404)
        return name

...
prevalidator=Validator
...
```


## SubControllers

If you need to validate data in controller, better use `djburger.controllers.subcontroller`:

```python
def get_name_controller(request, data, **kwargs):
    return data['name']

def echo_controller(request, data, **kwargs):
    subc = djburger.controllers.subcontroller(
        prevalidator=djburger.controllers.IsDict,
        controller=get_name_controller,
        postvalidator=djburger.controllers.IsStr,
    )
    return subc(request, data, **kwargs)

...
controller=echo_controller
...
```

If data passed to subcontroller is invalid then `djburger.exceptions.SubValidationError` will be immediately raised. View catch error and pass error to `postrenderer`.
