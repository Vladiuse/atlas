from django import forms
from django.core.exceptions import ValidationError


class CheckFormsByUrlForm(forms.Form):
    url = forms.URLField(required=False)
    html = forms.CharField(required=False)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        html = cleaned_data.get('html')
        if not any([url, html]):
            raise ValidationError('Должно быть заполнено одно из полей')
        return cleaned_data
