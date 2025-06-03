from django import forms
from django.core.exceptions import ValidationError

from form_checker.form_checker.presets import PRESETS_MAP

choices = [(preset_name, preset_name) for preset_name in PRESETS_MAP]


class CheckFormsByUrlForm(forms.Form):
    preset_name = forms.ChoiceField(choices=choices)
    url = forms.URLField(required=False)
    html = forms.CharField(required=False)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        html = cleaned_data.get("html")
        if not any([url, html]):
            raise ValidationError("Должно быть заполнено одно из полей")
        if all([url, html]):
            raise ValidationError("2 поля заполнять нельзя")
        return cleaned_data
