from django import forms
from django.core.exceptions import ValidationError
from common.constants import TEAMS_CHOICES, ATLAS_TEAM


class CheckFormsByUrlForm(forms.Form):
    team = forms.ChoiceField(choices=TEAMS_CHOICES, initial=(ATLAS_TEAM,ATLAS_TEAM))
    url = forms.URLField(required=False)
    html = forms.CharField(required=False)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        html = cleaned_data.get('html')
        if not any([url, html]):
            raise ValidationError('Должно быть заполнено одно из полей')
        if all([url, html]):
            raise ValidationError('2 поля заполнять нельзя')
        return cleaned_data
