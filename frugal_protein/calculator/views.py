from django.views.generic import TemplateView

class ProteinCalculator(TemplateView):
    template_name = 'calculator/calc.html'