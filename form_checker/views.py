from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .forms import CheckFormsByUrlForm
from form_checker.form_checker import HtmlChecker
from form_checker.form_checker.exceptions import FormNotFound

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
                check_results = html_form_checker.check(html=html)
                content = {
                    'check_results': check_results,
                }
                return render(request, self.result_template_name, content)
            except FormNotFound as e:
                form.add_error(None, str(e))
        content = {
            "form": form,
        }
        return render(request, self.template_name, content)
