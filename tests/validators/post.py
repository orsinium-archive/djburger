from __main__ import djburger
import marshmallow
import pyschemes


class PostMarshmallowBase(djburger.validators.bases.Marshmallow):
    name = marshmallow.fields.Str(required=True)
    mail = marshmallow.fields.Email(required=True)
    count = marshmallow.fields.Int(required=True)


@djburger.validators.wrappers.Marshmallow
class PostMarshmallowWrapped(marshmallow.Schema):
    name = marshmallow.fields.Str(required=True)
    mail = marshmallow.fields.Email(required=True)
    count = marshmallow.fields.Int(required=True)


scheme = {
    'name': str,
    'mail': str,
    'count': int,
}
PostPySchemesConstructed = djburger.validators.constructors.PySchemes(scheme)
PostPySchemesWrapped = djburger.validators.wrappers.PySchemes(pyschemes.Scheme(scheme))


postvalidators = [
    PostMarshmallowBase,
    PostMarshmallowWrapped,
    PostPySchemesConstructed,
    PostPySchemesWrapped,
]
