import djburger


class GroupInputValidator(djburger.validators.bases.Form):
    name = djburger.f.CharField(label='Name', max_length=80)
