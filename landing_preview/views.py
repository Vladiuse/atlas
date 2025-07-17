from django.shortcuts import render
from .forms import LandingPreviewForm
from django.http import HttpResponse
from landing_preview.usecase import GetLandingHtmlWithProductUseCase

def index(request):
    form = LandingPreviewForm(request.GET)
    if form.is_valid():
        case = GetLandingHtmlWithProductUseCase()
        html = case.execute(landing_id="2962", product_name="dewalt_combo_kit")
        response =HttpResponse(html)
        response.set_cookie(
            key='session_id',
            value='65748be4',
            samesite='None',
            secure=True,
            httponly=True,  # по желанию
        )
        return response
    return HttpResponse(str(form.errors))
