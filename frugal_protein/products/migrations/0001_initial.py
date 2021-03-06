# Generated by Django 2.2.6 on 2019-10-05 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brands',
            fields=[
                ('brand_id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('pid', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255)),
                ('qty', models.DecimalField(decimal_places=5, max_digits=8, null=True)),
                ('num_of_units', models.DecimalField(decimal_places=1, max_digits=4, null=True)),
                ('total_qty', models.DecimalField(decimal_places=5, max_digits=8, null=True)),
                ('unit_of_measurement', models.CharField(max_length=4, null=True)),
                ('header', models.CharField(max_length=255, null=True)),
                ('kcal', models.DecimalField(decimal_places=1, max_digits=5, null=True)),
                ('fat', models.DecimalField(decimal_places=1, max_digits=5, null=True)),
                ('carb', models.DecimalField(decimal_places=1, max_digits=5, null=True)),
                ('protein', models.DecimalField(decimal_places=1, max_digits=5, null=True)),
                ('barcode', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('tesco', models.CharField(blank=True, max_length=9, null=True, unique=True)),
                ('iceland', models.CharField(blank=True, max_length=5, null=True, unique=True)),
                ('tesco_base_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('tesco_sale_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('tesco_offer_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('tesco_offer_text', models.CharField(max_length=255, null=True)),
                ('iceland_base_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('iceland_sale_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('iceland_offer_price', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('iceland_offer_text', models.CharField(max_length=255, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='products.Brands')),
            ],
        ),
    ]
