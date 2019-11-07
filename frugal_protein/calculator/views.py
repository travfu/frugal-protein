from django.views.generic import TemplateView
from calculator.forms import ProteinCalcInput

class ProteinCalculator(TemplateView):
    template_name = 'calculator/calc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProteinCalcInput
        return context
    
    def post(self, request):
        form = ProteinCalcInput(request.POST, request.FILES)
        context = self.get_context_data()
        if form.is_valid():
            unit_price, protein_price = self.calc_prices(form.cleaned_data)
            context['unit_price'] = unit_price
            protein_amount = 10  # int value in 'price per 10g protein'
            context['protein_price'] = protein_amount * protein_price
        return self.render_to_response(context)

    def calc_prices(self, data_dict):
        """ 
        Calculates and returns 'price per unit' and 'price per 10g protein'.
        'Price per unit' is the price per kg, litre, or unit.

        Args:
            param2 (dict): form.cleaned_data that has been standardised to 
                           kg, litre, or unit
        """
        price_value = data_dict['price_value']
        qty_value = data_dict['qty_value']                  # kg/litre/unit
        protein_value = data_dict['protein_value']          # grams
        protein_per_value = data_dict['protein_per_value']  # kg/litre/unit

        # Calculate price per 1 unit (e.g. per kg, litre, or unit)
        unit_price = price_value / qty_value

        # Calculate price per 1g protein
        protein_price = unit_price * protein_per_value * (1 / protein_value)

        return (unit_price, protein_price)