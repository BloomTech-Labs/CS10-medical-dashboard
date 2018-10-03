from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import rx_claim
# admin
# labs7meddash

@admin.register(rx_claim)
class PersonAdmin(ImportExportModelAdmin):
    pass

