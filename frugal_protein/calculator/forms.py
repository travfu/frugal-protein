from django import forms

class ProteinCalcInput(forms.Form):   
    """
    Form to receive inputs required to calculate prices relative
    to a unit (e.g. 1g or 1L) and relative to amount of protein
    """
    # dropdown choices format: (value, display text)
    MEASUREMENTS = [('g', 'g'), ('kg', 'kg'), ('ml', 'ml'), ('l', 'litre'), ('sngl', 'unit')]
    
    # Sample input:
    # product A - £2.00, 1.5litre, 20g protein per 100ml
    #   price_value = 2.00
    #   qty_value = 1.5
    #   qty_unit = litre
    #   protein_value = 20
    #   protein_per_value = 100
    #   protein_per_unit = ml
    price_value = forms.DecimalField()
    qty_value = forms.DecimalField()
    qty_unit = forms.ChoiceField(choices=MEASUREMENTS)
    protein_value = forms.DecimalField()
    protein_per_value = forms.DecimalField()
    protein_per_unit = forms.ChoiceField(choices=MEASUREMENTS)
        