from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .forms import CheckFormsByUrlForm
from .form_checker.main import HtmlChecker
from html_checker.exceptions import FormNotFound
from requests.exceptions import RequestException

html_form_checker = HtmlChecker()

def index(request):
    return HttpResponse("123")


class CheckFormView(LoginRequiredMixin, View):

    template_name = 'form_checker/check_form.html'
    result_template_name = 'form_checker/check_result.html'
    def get(self, request):
        form = CheckFormsByUrlForm()
        content = {
            'form': form,
        }
        return render(request, self.template_name, content)

    def post(self, request):
        form = CheckFormsByUrlForm(request.POST)
        if form.is_valid():
            try:
                html = form.cleaned_data['html']
                url = form.cleaned_data['url']
                team = form.cleaned_data['team']
                check_results = html_form_checker.check(html=html, url=url, team=team)
                content = {
                    'check_results': check_results,
                }
                return render(request, self.result_template_name, content)
            except RequestException as e:
                message = f'Не удалось загрузить сайт: {e}'
                form.add_error(None, str(message))
            except FormNotFound as e:
                form.add_error(None, str(e))
        content = {
            "form": form,
        }
        return render(request, self.template_name, content)
