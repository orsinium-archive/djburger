import djburger


class GroupInputValidator(djburger.v.b.Form):
    name = djburger.f.CharField(label='Name', max_length=80)
