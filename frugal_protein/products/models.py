from django.db import models
from .helper.price_calc import calc_price_per_qty, calc_price_per_protein

class Brands(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=255)

class ProductInfo(models.Model):
    pid = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    brand = models.ForeignKey(Brands, on_delete=models.PROTECT, null=True)

    # Quantity info
    qty = models.DecimalField(max_digits=8, decimal_places=5, null=True)
    num_of_units = models.DecimalField(max_digits=4, decimal_places=1, null=True)       
    total_qty = models.DecimalField(max_digits=8, decimal_places=5, null=True)            
    unit_of_measurement = models.CharField(max_length=4, null=True)

    # Nutritional info
    header = models.CharField(max_length=255, null=True)
    kcal = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    fat = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    carb = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    protein = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    # Store-specific pids
    barcode = models.CharField(max_length=20, unique=True, null=True, blank=True)
    tesco = models.CharField(max_length=9, unique=True, null=True, blank=True)
    iceland = models.CharField(max_length=5, unique=True, null=True, blank=True)

    # Price - Tesco
    tesco_base_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tesco_sale_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tesco_offer_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tesco_offer_text = models.CharField(max_length=255, null=True)

    # Price - Iceland
    iceland_base_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    iceland_sale_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    iceland_offer_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    iceland_offer_text = models.CharField(max_length=255, null=True)

    # Image
    img = models.ImageField(default='/product_images/default.png', upload_to='product_images')

    def price_table(self):
        """ Returns a nested dict of prices for price table in product page """
        # Check if value exists for qty and nutrition
        if self.total_qty is None or self.protein is None:
            return None
        
        # Get list of stores within this model class
        stores = [store.replace('_base_price', '') for store in dir(self) if store.endswith('_base_price')]

        base_suffix = '_base_price'
        sale_suffix = '_sale_price'
        offer_suffix = '_offer_price'
        offer_txt_suffix = '_offer_text'

        # For each store, wrap price data in a dict
        prices = {}
        for store in stores:
            price_values = {
                'base': getattr(self, store + base_suffix),
                'sale': getattr(self, store + sale_suffix),
                'offer': getattr(self, store + offer_suffix)
            }
            if price_values['base'] is None:
                continue

            price_col = {**price_values}
            price_col['offer'] = getattr(self, store + offer_txt_suffix)
            per_unit_col = {k: calc_price_per_qty(v, self.total_qty) for k, v in price_values.items()}
            per_protein_col = {k: calc_price_per_protein(v, self.protein, self.unit_of_measurement) for k, v in price_values.items()}

            price_col['class'] = 'col2'
            per_unit_col['class'] = 'col3'
            per_protein_col['class'] = 'col4'

            prices[store] = [price_col, per_unit_col, per_protein_col]

        return prices