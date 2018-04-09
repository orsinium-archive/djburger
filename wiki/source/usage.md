# Usage

## Components

Main components:

1. **Parsers** (`djburger.p`).
2. **Validators** (`djburger.v`). Can be used as `prev` and `postv`.
    1. **Bases** (`djburger.v.b`).
    2. **Constructors** (`djburger.v.c`).
    3. **Wrappers** (`djburger.v.w`)
3. **Controllers** (`djburger.c`). Can be used as `c`.
4. **Renderers** (`djburger.r`). Can be used as `prer`, `postr` and `r`.

Some additional useful components:

1. `djburger.exceptions` -- useful exceptions.


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
1. [example project](https://github.com/orsinium/djburger/tree/master/example) for more information.


## Components structure

Use everywhere short notation from [dataflow](philosophy.html#dataflow).

DjBurger modules:

1. `djburger.p`. Parsers.
1. `djburger.v`. Validators:
  1. `djburger.v.b`. Validators which can used as **base** class for your own validators.
  1. `djburger.v.c`. Validators which can used as **constructors** for simple validators.
  1. `djburger.v.w`. Validators which can used as **wrappers** for external validators.
1. `djburger.c`. Controllers.
1. `djburger.r`. Renderers.
1. `djburger.e`. Exceptions.

Keyword arguments for `djburger.rule`:

1. `d` -- decorators list.
1. `p` -- parser.
1. `prev` -- pre-validator.
1. `prer` -- renderer for pre-validator.
1. `c` -- controller.
1. `postv` -- post-validator.
1. `postr` -- renderer for post-validator.
1. `r` -- renderer for success response.


## Decorators

TODO

## Parsers

TODO

## Validators

TODO

## Controllers

TODO

## Renderers

TODO

## Exceptions

TODO
