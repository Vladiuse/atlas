from django import forms

class LandingPreviewForm(forms.Form):
    landing_id = forms.IntegerField()
    product_name = forms.CharField()
