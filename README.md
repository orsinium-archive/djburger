# DjBurger

![DjBurger logo](wiki/source/imgs/logo.png)

[![Build Status](https://travis-ci.org/orsinium/djburger.svg?branch=master)](https://travis-ci.org/orsinium/djburger) [![Documentation](https://readthedocs.org/projects/djburger/badge/)](https://djburger.readthedocs.io/en/latest/) [![PyPI version](https://img.shields.io/pypi/v/djburger.svg)](https://pypi.python.org/pypi/djburger) [![Status](https://img.shields.io/pypi/status/djburger.svg)](https://pypi.python.org/pypi/djburger) [![Code size](https://img.shields.io/github/languages/code-size/orsinium/djburger.svg)](https://github.com/orsinium/djburger) [![License](https://img.shields.io/pypi/l/djburger.svg)](LICENSE)

**DjBurger** -- framework for big Django projects.

What DjBurger do?

* Split Django views into steps for secure and clean code.
* Provide built-in objects for all steps.
* Integrates this many side libraries like Django REST Framework and Marshmallow.

DjBurger doesn't depend on Django. You can use it in any projects if you want.

Read more into [documentation](https://djburger.readthedocs.io/en/latest/).

## Key principles

1. Validation logic is separate from the main logic.
2. Reusable logic for many views.
3. Reusable input and output data formats.
4. More clean views.


## Dataflow

1. **Decorators** (`d`). Feel free to use any side Django decorators like `csrf_exempt`.
2. **Parser** (`p`). Parse request body.
3. **PreValidator** (`prev`). Validate and clear request.
4. **PreRenderer** (`prer`). Render and return PreValidation errors.
5. **Controller** (`c`). Main logic: do some things.
6. **PostValidator** (`postv`). Validate and clear response.
7. **PostRenderer** (`postr`). Render and return PostValidation errors.
8. **Renderer** (`r`). Render successful response.

![Scheme](wiki/source/imgs/scheme.png)

Required only Controller and Renderer.

## Explore

1. Read [documentation](https://djburger.readthedocs.io/en/latest/).
1. See [example](example/) project.
1. For quick help just inspect djburger from python console (for example, `help('djburger.views')`).
1. If you have some questions then [view issues](https://github.com/orsinium/djburger/issues) or [create new](https://github.com/orsinium/djburger/issues/new).
1. If you found some mistakes then fix it and [create Pull Request](https://github.com/orsinium/djburger/compare). Contributors are welcome.
1. [Star this project on github](https://github.com/orsinium/djburger) :)
