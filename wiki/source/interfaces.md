# Interfaces

1. **Decorator**. Any decorator which can wrap Django view.
2. **Parser**. Any callable object which get request object and return parsed data.
3. **Validator**. Have same interfaces as Django Forms, but get `request` by initialization:
    1. `.__init__()`
        * `request` -- Request object.
        * `data` -- data from user (`prevalidator`) or controller (`postvalidator`).
        * `**kwargs` -- any keyword arguments for validator.
    2. `.is_valid()` -- return True if data is valid False otherwise.
    3. `.errors` -- errors if data is invalid.
    4. `.cleaned_data` -- cleaned data if input data is valid.
4. **Controller**. Any callable object. Kwargs:
    1. `request` -- Request object.
    2. `data` -- validated request data.
    3 `**kwargs` -- kwargs from url.
5. **Renderer**. Any callable object. Kwargs:
    1. `request` -- Request object.
    2. `data` -- validated controller data (only for `r`).
    3. `validator` -- validator which not be passed (only for `prerenderer` and `postrenderer`).
    4. `status_code` -- HTTP status code if validator raise `djburger.exceptions.StatusCodeError`, None otherwise.
