from django import forms

# Form for cheapest pharmacy in zipcode for certain medication--used in pharmacy_info.html
# and in views.pharmacy_info
class pharmacyForm(forms.Form):
    zip_code = forms.CharField(label="Zip Code", max_length=5)
    drug = forms.CharField(label='Name of Medication', max_length=200)
    quantity = forms.IntegerField(label="Quantity Prescribed")
