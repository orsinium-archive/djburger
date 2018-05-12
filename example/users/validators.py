import djburger


class GroupInputValidator(djburger.validators.bases.Form):
    name = djburger.forms.CharField(label='Name', max_length=80)
