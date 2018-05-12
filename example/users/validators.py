import djburger


class GroupInputValidator(djburger.validators.b.Form):
    name = djburger.f.CharField(label='Name', max_length=80)
