from django import forms


class CheckFormsByUrlForm(forms.Form):
    url = forms.URLField()