from django.shortcuts import render
from .forms import LandingPreviewForm
from django.http import HttpResponse

def index(request):
    form = LandingPreviewForm(request.GET)
    if form.is_valid():
        return HttpResponse(str(form.cleaned_data))
    return HttpResponse(str(form.errors))
