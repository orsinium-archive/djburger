# Philosophy


## Key principles

1. Validation only before main logic.
2. Reusable logic for many views.
3. Reusable input and output data formats.
4. More clear views.


## Dataflow

1. **Decorators** (`d`). Feel free to use any side Django decorators like `csrf_exempt`.
2. **Parser** (`p`). Parse request body.
3. **PreValidator** (`prev`). Validate and clear request.
4. **PreRenderer** (`prer`). Render and return PreValidation errors.
5. **Controller** (`c`). Main logic: do some things.
6. **PostValidator** (`postv`). Validate and clear response.
7. **PostRenderer** (`postr`). Render and return PostValidation errors.
8. **Renderer** (`r`). Render successful response.

![Scheme](imgs/scheme.png)

Required only Controller and Renderer.


## Related conceptions

+ [Design by contract](https://en.wikipedia.org/wiki/Design_by_contract). DjBurger use pre-validation and post-validation as contracts for web interfaces and between controllers. For non-web projects you can use [deal](https://github.com/orsinium/deal) powered pure design by contract with DjBurger validators. More info into [deal documentation](https://github.com/orsinium/deal#validators).
+ [SOLID](https://en.wikipedia.org/wiki/SOLID_(object-oriented_design)). DjBurger support this conceptions for projects:
  + [SRP](https://en.wikipedia.org/wiki/Single_responsibility_principle). This is main DjBurger idea. If you have many API for one business logic you must made only one controller and many views with different parsers, validators and renderers.
  + [OCP](https://en.wikipedia.org/wiki/Open/closed_principle). All DjBurger components are extendable and do not use any global variables such as Django settings.
  + [LSP](https://en.wikipedia.org/wiki/Liskov_substitution_principle). You can use any callable object as parser, validator, controller or renderer if it is match to [interface](interfaces.html).
  + [ISP](https://en.wikipedia.org/wiki/Interface_segregation_principle). DjBurger made simpler interface creation and main logic reusing.
  + [DIP](https://en.wikipedia.org/wiki/Dependency_inversion_principle). Parsers, validators, controllers and renderers is are mutually independent.
+ [Cohesion & Coupling](https://stackoverflow.com/a/3085419/8704691). DjBurger created for simplifying modules structure,
high cohesion and low coupling. This is main idea how DjBurger help you make good, readable and extendable code for big projects.
+ [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) by support [state codes](usage.html#exceptions), any external [decorators](usage.html#decorators) and [Django REST Framework](external.html). You can effective use DjBurger for building REST API. But DjBurger doesn't force this conception, and you can use it for any views as user interface rendering.
+ [MVC](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller). Django use [MTV](https://djangobook.com/model-view-controller-design-pattern/) conception, and views manipulates models and render templates. This is simple but dirty. DjBurger split view to parser, validator and renderer (this is all view from MVC) and controller for low coupling and clean code. And DjBurger render template only from renderer.
+ [The Clean Architecture](https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html). DjBurger hard isolate UI from Presenters. This is main clean architecture conception.
