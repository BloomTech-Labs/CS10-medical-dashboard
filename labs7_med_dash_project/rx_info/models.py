from django.db import models
from django_pandas.managers import DataFrameManager


# Model for individual rx_claims--used in views.py and to create original SQLite db
class rx_claim(models.Model):
    PBMVendor = models.CharField(max_length = 200)
    PharmacyID = models.CharField(max_length = 200)
    DrugShortName = models.CharField(max_length = 200)
    UnitCost = models.FloatField()
    PharmacyName = models.CharField(max_length = 200)
    PharmacyStreetAddress1 = models.CharField(max_length = 200)
    PharmacyCity = models.CharField(max_length = 200)
    PharmacyZip = models.CharField(max_length = 5)
    PharmZip = models.CharField(max_length = 3)
    DrugLabelName = models.CharField(max_length = 200)

    # Allows SQLite query sets to be transformed to pandas objects
    objects = DataFrameManager()