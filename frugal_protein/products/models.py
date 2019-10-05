from django.db import models

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