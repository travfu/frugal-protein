from django import forms

class ProteinCalcInput(forms.Form):   
    """
    Form to receive inputs required to calculate prices relative
    to a unit (e.g. 1g or 1L) and relative to amount of protein
    """
    # dropdown choices format: (value, display text)
    UNITS = [('g', 'g'), ('kg', 'kg'), ('ml', 'ml'), ('l', 'litre'), ('sngl', 'unit')]
    
    # Sample input:
    # product A - £2.00, 1.5litre, 20g protein per 100ml
    #   price_value = 2.00
    #   qty_value = 1.5
    #   qty_unit = litre
    #   protein_value = 20
    #   protein_per_value = 100
    #   protein_per_unit = ml
    price_value = forms.DecimalField(min_value=0, decimal_places=2)
    qty_value = forms.DecimalField(min_value=0.001, decimal_places=3)
    qty_unit = forms.ChoiceField(choices=UNITS)
    protein_value = forms.DecimalField(min_value=0.1, decimal_places=1)
    protein_per_value = forms.DecimalField(min_value=0.001, decimal_places=3)
    protein_per_unit = forms.ChoiceField(choices=UNITS)
    
    def full_clean(self):
        """ 
        https://github.com/django/django/blob/58c1acb1d6054dfec29d0f30b1033bae6ef62aec/django/forms/forms.py#L360
        """
        super().full_clean()
        # Don't proceed if input data failed Django's in-built validation
        if self._errors:
            return
        self.standardise_data()

    def standardise_data(self):
        """
        Return bound form data that has been standardised to represent values
        in kg, litre, or unit. (i.e. Convert g to kg, and ml to litre)

        price_value and protein_value do not need to be standardised. Protein
        value has an assumed unit of grams.
        """
        # Input data that do not pass Django's form validation should not reach 
        # this point, thus, it can be assumed that all fields have valid data 
        # and have been cleaned and converted to Python types (e.g. Decimal).

        data = self.cleaned_data
        if data['qty_unit'] == 'g':
            data['qty_unit'] = 'kg'
            data['qty_value'] /= 1000

        elif data['qty_unit'] == 'ml':
            data['qty_unit'] = 'l'
            data['qty_value'] /= 1000
        
        if data['protein_per_unit'] == 'g':
            data['protein_per_unit'] = 'kg'
            data['protein_per_value'] /= 1000
        
        elif data['protein_per_unit'] == 'ml':
            data['protein_per_unit'] = 'l'
            data['protein_per_value'] /= 1000