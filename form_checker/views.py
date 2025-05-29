from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .forms import CheckFormsByUrlForm


def index(request):
    return HttpResponse("123")


class CheckFormView(LoginRequiredMixin, View):

    template_name = 'form_checker/check_form.html'

    def get(self, request):
        form = CheckFormsByUrlForm()
        content = {
            'form': form,
        }
        return render(request, self.template_name, content)

    def post(self, request):
        form = CheckFormsByUrlForm(request.POST)
        if form.is_valid():
            text = str(form)
            return HttpResponse(text)
        content = {
            "form": form,
        }
        return render(request, self.template_name, content)
