from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from requests.exceptions import RequestException

from common.request_sender import RequestSender

from .form_checker import HtmlChecker
from .form_checker.exceptions import HtmlTagNotFound
from .forms import CheckFormsByUrlForm

html_checker = HtmlChecker(request_sender=RequestSender())


def index(request):
    return HttpResponse("123")


class CheckFormView(LoginRequiredMixin, View):
    template_name = "form_checker/check_form.html"
    result_template_name = "form_checker/check_result.html"

    def get(self, request):
        form = CheckFormsByUrlForm()
        content = {
            "form": form,
        }
        return render(request, self.template_name, content)

    def post(self, request):
        form = CheckFormsByUrlForm(request.POST)
        if form.is_valid():
            try:
                html = form.cleaned_data["html"]
                url = form.cleaned_data["url"]
                preset_name = form.cleaned_data["preset_name"]
                check_result = html_checker.check(preset_name=preset_name, html=html, url=url)
                content = {
                    "check_result": check_result,
                }
                return render(request, self.result_template_name, content)
            except RequestException as e:
                message = f"Не удалось загрузить сайт: {e}"
                form.add_error(None, str(message))
            except HtmlTagNotFound as e:
                form.add_error(None, str(e))
        content = {
            "form": form,
        }
        return render(request, self.template_name, content)
