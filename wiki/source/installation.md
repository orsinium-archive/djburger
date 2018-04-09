# Installation

## STABLE

```bash
pip install djburger
```

## DEV

Using pip:

```bash
sudo pip install -e git+https://github.com/orsinium/djburger.git#egg=djburger
```

In `requirements.txt`:

```bash
-e git+https://github.com/orsinium/djburger.git#egg=djburger
```

## Dependencies

DjBurger has no dependencies except [six](https://github.com/benjaminp/six). Yeah, DjBurger is Django independed and can be used in any python projects. For example, you can use DjBurger with [deal](https://github.com/orsinium/deal) for design by contract with side schemes usage. More info into [deal docs](https://github.com/orsinium/deal#validators).

But DjBurger doesn't support `Django<1.7` and `DjangoRESTFramework<3.5`. You can pass constraints from DjBurger to pip:

```python
pip install -c constraints.txt ...
```
