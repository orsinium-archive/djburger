from __main__ import djburger
import marshmallow
import rest_framework


class PostMarshmallowBase(djburger.validators.bases.Marshmallow):
    id = marshmallow.fields.Int(required=True)
    name = marshmallow.fields.Str(required=True)


@djburger.validators.wrappers.Marshmallow
class PostMarshmallowWrapped(marshmallow.Schema):
    id = marshmallow.fields.Int(required=True)
    name = marshmallow.fields.Str(required=True)


class PostRESTFrameworkBase(djburger.validators.bases.RESTFramework):
    id = rest_framework.serializers.IntegerField()
    name = rest_framework.serializers.CharField(max_length=20)


@djburger.validators.wrappers.RESTFramework
class PostRESTFrameworkWrapped(rest_framework.serializers.Serializer):
    id = rest_framework.serializers.IntegerField()
    name = rest_framework.serializers.CharField(max_length=20)


postvalidators = [
    PostMarshmallowBase,
    PostMarshmallowWrapped,
    PostRESTFrameworkBase,
    PostRESTFrameworkWrapped,
]
