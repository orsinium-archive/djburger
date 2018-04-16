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

DjBurger only dependency is [six](https://github.com/benjaminp/six). DjBurger doesn't depend on Django.

But DjBurger doesn't support `Django<1.7` and `DjangoRESTFramework<3.5`. You can pass constraints from DjBurger in pip:

```python
pip install -c constraints.txt ...
```
