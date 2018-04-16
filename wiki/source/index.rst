.. DjBurger documentation master file, created by
   sphinx-quickstart on Sun Nov 19 20:59:37 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DjBurger's documentation!
====================================

**DjBurger** -- framework for big Django projects.

What DjBurger do?

- Split Django views into steps for secure and clean code.
- Provide built-in objects for all steps.
- Integrates this many side libraries like Django REST Framework and Marshmallow.

DjBurger doesn't depend on Django. You can use it in any projects if you want.


.. toctree::
    :maxdepth: 1
    :caption: Main Info

    installation
    philosophy
    usage
    examples
    interfaces
    external

.. toctree::
    :maxdepth: 2
    :caption: API

    views
    parsers
    validators
    controllers
    renderers
