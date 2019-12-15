from decimal import Decimal

class Calc:    
    @classmethod
    def unit_price(cls, price, total_qty):
        """
        Returns price per 'kg', 'litre', or 'unit/SNGL' depending on unit of measure.

        Args:
            param1 (Decimal): price value
            param2 (Decimal): total quantity of product (e.g. 200 [kg] or 1.5 [L])
        """
        if price and total_qty:
            return price / total_qty
        else:
            return None


    @classmethod
    def price_per_protein(cls, price_per_unit, protein, qty, uom):
        """ 
        Calculates and returns price per 1g of protein 

        Args:
            param1 (float): price per standard unit (1kg, 1litre, or 1unit)
            param2 (float): protein content per 'qty' (param3)
            param3 (float): see param2
            param4 (str): unit of measurement (e.g. g, kg, ml, l, SNGL)

        Equation:
            price per 1g protein = price per unit / protein per unit
            protein per unit = protein * multiplier
            multiplier = 1 / qty (converted to standard unit)
        """
        print('========', price_per_unit, protein, qty, uom)
        
        multiplier = cls.std_unit_multiplier(cls, qty, uom)
        protein_per_unit = protein * multiplier
        return price_per_unit / protein_per_unit


    def std_unit_multiplier(self, qty, uom):
        """ 
        Given a qty value and it's unit of measurement, return multiplier value
        to standardise qty value to either 1kg, 1L, or 1unit (SNGL)

        Example:
             100g * x = 1kg
            0.1kg * x = 1kg
                    x = 1 / 0.1

               3L * x = 1L
                    x = 1 / 3
        """
        uom = uom.lower()
        if uom in ('g', 'ml'):
            unit_multiplier = 0.001  #  g * multiplier = kg
        elif uom in ('kg', 'l', 'sngl'):
            unit_multiplier = 1      # kg * multiplier = kg
        return Decimal(1 / (qty * unit_multiplier))

