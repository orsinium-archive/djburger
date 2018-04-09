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
