from django.views.generic import TemplateView
from calculator.forms import ProteinCalcInput

class ProteinCalculator(TemplateView):
    template_name = 'calculator/calc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProteinCalcInput
        return context