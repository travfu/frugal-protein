def calc_price_per_qty(price, total_qty):
    """
    Returns price per 'kg', 'litre', or 'unit/SNGL' depending on unit of measure.

    Args:
        param1 (Decimal): price value
        param2 (Decimal): total quantity of product (e.g. 200 [kg] or 1.5 [L])
    """
    if price is not None:
        return price / total_qty
    else:
        return None


def calc_price_per_protein(price_qty, protein, uom):
    """
    Returns price per 10g protein.
    Returns None if unit of measurement is 'SNGL'.

    Args:
        param1 (Decimal): price per kg/litre/item(SNGL)
        param2 (Decimal): protein content per 100g
        param3 (str): unit of measurement

    Equation = PricePerKg * (10g / ProteinPerKg)
        PricePerKg == param1
        ProteinPerKg == param2 * 10 (if unit of measure is kg/litre)
    
    TODO: implement equation if unit of measure is SNGL after sorting
          out logic for parsing nutritional info for SNGL products. 
          For now, return None
    """
    if uom == 'SNGL':
        return None
    elif protein is not None and protein != 0 and price_qty is not None:
        multiplier = 10 / (protein * 10)   
        return price_qty * multiplier
    else:
        return None