from __main__ import djburger
import cerberus
import wtforms


class PreWTFormsBase(djburger.validators.bases.WTForms):
    name = wtforms.StringField('Name', [
        wtforms.validators.DataRequired(),
    ])
    mail = wtforms.StringField('E-Mail', [
        wtforms.validators.DataRequired(), wtforms.validators.Email(),
    ])
    count = wtforms.IntegerField('Count', [
        wtforms.validators.DataRequired(), wtforms.validators.NumberRange(min=0),
    ])


@djburger.validators.wrappers.WTForms
class PreWTFormsWrapped(wtforms.Form):
    name = wtforms.StringField('Name', [
        wtforms.validators.DataRequired(),
    ])
    mail = wtforms.StringField('E-Mail', [
        wtforms.validators.DataRequired(), wtforms.validators.Email(),
    ])
    count = wtforms.IntegerField('Count', [
        wtforms.validators.DataRequired(), wtforms.validators.NumberRange(min=0),
    ])


scheme = dict(
    name=dict(type='string', required=True),
    mail=dict(
        type='string',
        required=True,
        # http://docs.python-cerberus.org/en/stable/validation-rules.html#regex
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    ),
    count=dict(type='integer', required=True, coerce=int),
)
PreCerberusConstructed = djburger.validators.constructors.Cerberus(scheme, purge_unknown=True)
CerberusWrapped = djburger.validators.wrappers.Cerberus(cerberus.Validator(scheme, purge_unknown=True))


prevalidators = [
    PreWTFormsBase,
    PreWTFormsWrapped,
    PreCerberusConstructed,
    CerberusWrapped,
]
