from django.shortcuts import render
from . import forms
from .models import rx_claim
import pandas as pd

#from .models import rx_claim, CSVrxData

# Home page
def home(request):
    return render(request, 'rx_info/home.html', {})

# Background code page
def background(request):
    return render(request, 'rx_info/background.html', {})

# Local pharmay search page
def pharmacy_info(request):
    form = forms.pharmacyForm()
    return render(request, 'rx_info/pharmacy_info.html', {"form": form})

# PBM search page
def PBM_info(request):
    return render(request, 'rx_info/PBM_info.html', {})

# Pharmacy results page
def pharmacy_results(request):
    # Get the input from the form from the pharmacy_info page
    zipcode = request.GET.get('zip_code')
    drug = request.GET.get('drug')
    quantity = request.GET.get('quantity')

    # force the characters in the drug string to upper case to match database
    drug = drug.upper()
    # Define variables from the input zip code and drug name to match the
    # two engineered columns
    drug = drug.upper()
    zipcode_short = str(zipcode)[:3]
    drug_basic = drug.split()[0]
    # Make sure quantity is read as an integer
    quantity = int(quantity)

    # Get the most specific non-empty query set first trying to filter by the full
    # zipcode and drug name, then by the full zipcode and broader drug name,
    # finally by the zipcode area (first 3 numbers) and shortened drug name
    if rx_claim.objects.filter(PharmacyZip=zipcode).filter(DrugLabelName=drug):
        qs = rx_claim.objects.filter(PharmacyZip=zipcode).filter(DrugLabelName=drug)
    elif rx_claim.objects.filter(PharmacyZip=zipcode).filter(DrugShortName=drug_basic):
        qs = rx_claim.objects.filter(PharmacyZip=zipcode).filter(DrugShortName=drug_basic)
    elif rx_claim.objects.filter(PharmZip=zipcode_short).filter(DrugShortName=drug_basic):
        qs = rx_claim.objects.filter(PharmZip=zipcode_short).filter(DrugShortName=drug_basic)
    # If all queries come back empty, display the no results page
    else:
        return render(request, 'rx_info/no_pharmacy_resuults.html', {})
    
    # Convert the query set to a pandas dataframe with the relevant columns
    df = qs.to_dataframe(['PharmacyID', 'DrugShortName', 'UnitCost', 'PharmacyName', 'PharmacyStreetAddress1',
                            'PharmacyCity', 'PharmacyZip', 'PharmZip', 'DrugLabelName'], index='id')
    # Make sure UnitCost is read as a float
    df.UnitCost = df.UnitCost.apply(lambda value: float(value))

    # Find average unit cost by pharmacy id and sort in ascending order
    pharmacies = df.groupby(['PharmacyID'], as_index=False).mean()  
    sorted_cost = pharmacies.sort_values(by='UnitCost', ascending=True)

    # Convert groupby object to a dataframe
    sorted_df = pd.DataFrame(sorted_cost, columns=['PharmacyID', 'UnitCost'])
    
    # Limit to 5 results
    if sorted_df.shape[0] > 5:
        sorted_df = sorted_df[:5]

    # Create estimated price column by multiplying quanity prescribed (user input)
    # by unit cost
    sorted_df['EstimatedPrice'] = sorted_df.apply(lambda row: '${0:.2f}'.format(quantity*row['UnitCost']), axis=1)
    # Refer back to original dataframe to get human readable, relevant pharmacy info from pharmacy ID
    sorted_df['PharmacyName'] = sorted_df.apply(lambda row: df.PharmacyName[df.PharmacyID == row.PharmacyID].iloc[0], axis=1)
    sorted_df['PharmacyStreetAddress1'] = sorted_df.apply(lambda row: df.PharmacyStreetAddress1[df.PharmacyID == row.PharmacyID].iloc[0], axis=1)
    sorted_df['PharmacyZip'] = sorted_df.apply(lambda row: df.PharmacyZip[df.PharmacyID == row.PharmacyID].iloc[0], axis=1)
    sorted_df['PharmacyCity'] = sorted_df.apply(lambda row: (df.PharmacyCity[df.PharmacyID == row.PharmacyID].iloc[0]).strip(), axis=1)
    # Drop (now) unnecessary columns
    sorted_df.drop(columns = ['UnitCost', 'PharmacyID'], inplace=True)
    # Reset index
    sorted_df.reset_index(drop=True, inplace=True)

    # Convert dataframe to html so it can be read into the pharmacy_results.html template
    data_html = sorted_df.to_html()
    context = {'loaded_data': data_html}
    return render(request, 'rx_info/pharmacy_results.html', context)

def PBM_results(request):
    # Get the input from the form from the pharmacy_info page
    drug = request.GET.get('drug')
    # force the characters in the drug string to upper case to match database
    drug = drug.upper()    
    # Define broader drug name to match engineered DrugShortName column
    drug_basic = drug.split()[0]

    # Get the most specific non-empty query set first trying to filter by the full
    # drug name, then by shortened drug name
    if rx_claim.objects.filter(DrugLabelName=drug):
        qs = rx_claim.objects.filter(DrugLabelName=drug)
    elif rx_claim.objects.filter(DrugShortName=drug_basic):
        qs = rx_claim.objects.filter(DrugShortName=drug_basic)
    # If all queries come back empty, display the no results page
    else:
        return render(request, 'rx_info/no_PBM_results.html', {})
    
    # Convert the query set to a pandas dataframe with the relevant columns
    df = qs.to_dataframe(['PBMVendor', 'DrugShortName', 'UnitCost', 'DrugLabelName'], index='id')
    # Make sure UnitCost is read as a float
    df.UnitCost = df.apply(lambda row: float(row['UnitCost']), axis=1)

    # Find average unit cost by PBM Vendor and sort in ascending order
    pbms = df.groupby(['PBMVendor'], as_index=False).mean()

    # Convert groupby object to pandas dataframe
    pbms = pd.DataFrame(pbms)
    # Sort by ascending unitcosts
    sorted_pbms = pbms.sort_values(by='UnitCost', ascending=True)
    # Reset index
    sorted_pbms.reset_index(drop=True, inplace=True)

    # Convert dataframe to html so it can be read into the pharmacy_results.html template
    data_html = sorted_pbms.to_html()
    context = {'loaded_data': data_html}
    return render(request, 'rx_info/PBM_results.html', context)
