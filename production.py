# Necessary imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
import statistics as stats


# Importing the files as pandas dataframes
df_1 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161101.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_2 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161108.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_3 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161116.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_4 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161122.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_5 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161129.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_6 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20161206.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_7 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170110.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_8 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170116.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_9 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170117.csv', 
                   sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_10 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170124.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_11 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170131.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_12 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170207.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_13 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170214.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_14 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170221.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])
df_15 = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/Rx_BenefitPlan_20170301.csv', 
                    sep='|', index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])


# Tracking which file each dataframe came from
df_1["OriginalDataset"] = 1
df_2["OriginalDataset"] = 2
df_3["OriginalDataset"] = 3
df_4["OriginalDataset"] = 4
df_5["OriginalDataset"] = 5
df_6["OriginalDataset"] = 6
df_7["OriginalDataset"] = 7
df_8["OriginalDataset"] = 8
df_9["OriginalDataset"] = 9
df_10["OriginalDataset"] = 10
df_11["OriginalDataset"] = 11
df_12["OriginalDataset"] = 12
df_13["OriginalDataset"] = 13
df_14["OriginalDataset"] = 14
df_15['OriginalDataset'] = 0


# Combining all dataframes into one
df = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8, df_9, df_10, 
                df_11, df_12, df_13, df_14, df_15])


# Filtering the dataframe to only include processed ('P') claims
df_P = df[df.ClaimStatus=='P']


# Defining a function to engineer the total cost of a prescription based on 4 available 
# cost metrics--not all of which are provided for each claim
def get_total(row):
    if row['IngredientCost'] and row['DispensingFee']:
        cost1 = float(row['IngredientCost']) + float(row['DispensingFee'])
    elif row['IngredientCost']:
        cost1 = float(row['IngredientCost'])
    else:
        cost1 = 0
        
    cost2 = float(row['OutOfPocket']) + float(row['PaidAmount'])
        
    return max(cost1, cost2)

# Implementing the above function to engineer a new feature for the dataframe
df_P['TotalCost'] = df_P.apply(lambda row: get_total(row), axis=1)


# Some prescriptions resulted in a total cost of less than a dollar. Because this is not 
# consistent with real-world applications and transactions, this is assumed clerical error. 
# Data is filtered for realistic costs
df_pos = df_P[df_P.TotalCost > 5]


# Deleting commonly empty, corrupt, or unnecessary fields, and dropping rows with 
# unavailable drug information
rx_info = df_pos.drop(columns=['PharmacyStreetAddress2', 'PrescriberFirstName', 'PresriberLastName', 
                               'ClaimStatus']).dropna(subset=['DrugLabelName'])


# Define a function to engineer a secondary cost metric to be used in analysis
def get_unit_cost(row):
    if float(row['Quantity']) > 0:
        return float(row['TotalCost'])/float(row['Quantity'])
    else:
        return row['TotalCost']

# Applying the function to the dataframe to engineer a cost per dose or Unit Cost feature
rx_info['UnitCost'] = rx_info.apply(lambda row: get_unit_cost(row), axis=1)


# Some zip codes are the 9 digit zip code while others are the more common 5 digit.
# Defining a function to ensure all zip codes are the 5 digit version
def get_zip(row):
    if len(str(row['PharmacyZip'])) > 5:
        return str(row['PharmacyZip'])[:5]
    else:
        return row['PharmacyZip']

# Implementing the function to create a second zip code column
rx_info['PharmacyZipCode'] = rx_info.apply(lambda row: get_zip(row), axis=1)

# Define a second drug name code column in the dataframe
# to get rid of dosage info
rx_info['DrugShortName'] = rx_info.apply(lambda row: row.DrugLabelName.split()[0])

# Define a second pharmacy zip code column in the dataframe
# to include a larger area
rx_info['PharmZip'] = rx_info.apply(lambda row: str(row.PharmacyZip)[:3])



# Mail order pharmacies are not restricted to specific zip codes, so we encode them
# with nonexistent zip codes
def mail_order_pharm(row):
    if row['MailOrderPharmacy']=='Y':
        return 99999
    else:
        return row['PharmacyZipCode']

# Drop the old (now redundant) PharmacyZip column so we can overwrite it and implement
# the above function
rx_info.drop(columns=['PharmacyZip'], inplace=True)
rx_info['PharmacyZip'] = rx_info.apply(lambda row: mail_order_pharm(row), axis=1)

# Drop the old (now redundant) PharmacyZipCode column
drug_names = rx_info.drop(columns=['PharmacyZipCode'])


# Fix random white space
def rid_whitespace(value):
    if type(value) == str:
        return ' '.join(value.split())
    else:
        return value
    

# Get rid of erroneous white space in DrugLabelName
drug_names.DrugLabelName = drug_names.DrugLabelName.apply(lambda drug: rid_whitespace(drug))
drug_names.PharmacyNPI = drug_names.PharmacyNPI.apply(lambda NPI: rid_whitespace(NPI))
drug_names.PharmacyName = drug_names.PharmacyName.apply(lambda name: rid_whitespace(name))
drug_names.PharmacyStreetAddress1 = drug_names.PharmacyStreetAddress1.apply(lambda address: rid_whitespace(address))
drug_names.PharmacyCity = drug_names.PharmacyCity.apply(lambda city: rid_whitespace(city))




# Columns: ['AHFSTherapeuticClassCode', 'CoInsurance', 'CompoundDrugIndicator',
# 'Copay', 'DAWCode', 'DateFilled', 'DaysSupply', 'Deductible',
# 'DispensingFee', 'DrugLabelName', 'FillNumber', 'FormularyStatus',
# 'Generic', 'GroupNumber', 'IngredientCost', 'MailOrderPharmacy',
# 'MemberID', 'MultisourceIndicator', 'NDCCode', 'OriginalDataset',
# 'OutOfPocket', 'PBMVendor', 'PaidAmount', 'PaidOrAdjudicatedDate',
# 'PharmacyCity', 'PharmacyNPI', 'PharmacyName', 'PharmacyNumber',
# 'PharmacyState', 'PharmacyStreetAddress1', 'PharmacyTaxId',
# 'PrescriberID', 'Quantity', 'RxNumber', 'SeqNum', 'UnitMeasure',
# 'punbr_grnbr', 'TotalCost', 'UnitCost', 'PharmacyZip']



# Helper function for get_best_options/get_df to return a sorted dataframe of
# a specified number of entries based on price
def _cheapest(df, n, pharm_type='local'):
    # Group the input dataframe by pharmacy
    pharmacies = table.groupby(['PharmacyName']).mean()
    
    # Get indices corresponding to pharmacies sorted from lowest unit
    # cost to highest unit cost
    idx_sort = np.argsort(np.array(pharmacies.UnitCost.values))
    
    # If there are more than n entries, limit the output to n, with specified
    # columns
    if len(idx_sort) > n:
        # Specify which columns to output based on whether the pharmacy is local
        # or mail order
        if pharm_type = 'local':
            return pd.DataFrame(pharmacies).loc(columns=['PharmacyName', 
                                                         'PharmacyStreetAddress1',
                                                         'PharmacyCity',
                                                         'UnitCost']).iloc[idx_sort[:n]]
        else:
            return pd.DataFrame(pharmacies).loc(columns=['PharmacyName', 
                                                         'UnitCost']).iloc[idx_sort[:n]]
    # Else, return all results in order with specified columns
    else:
        # Specify which columns to output based on whether the pharmacy is local
        # or mail order
        if pharm_type = 'local':
            return pd.DataFrame(pharmacies).loc(columns=['PharmacyName',
                                                         'PharmacyStreetAddress1',
                                                         'PharmacyCity',
                                                         'UnitCost']).iloc[idx_sort]
        else:
            return pd.DataFrame(pharmacies).loc(columns=['PharmacyName',
                                                         'UnitCost']).iloc[idx_sort]

# Helper function to return the desirable dataframe given the medication and parent df
def _get_df(df, drug, drug_basic):
    # Check if drug name exists in the pharmacy data, if yes
    # filter the dataset based on that drug name
    if drug in set(df.DrugLabelName.values):
        df = df[df.DrugLabelName==drug]
        return df
    # Else, check if broader drug name exists in dataset, if yes
    # filter based on the shorter name
    elif drug_basic in set(df.DrugShortName):
        df = df[df.DrugShortName==drug_basic]
        return df
    else:
        return pd.DataFrame()

# Function to retrieve information in the form of data tables with the cheapest
# pharmacies locally and by mail order
def get_best_options(zipcode, drug, number, df):
    # Ensure unit cost is considered a float
    df['UnitCost'] = df.apply(lambda row: float(row.UnitCost), axis=1)
        
    # Separate the dataframe into mail order pharmacies and local pharmacies
    mail_order = df[df.PharmacyZip=='MailOrder']
    zip_codes = df[df.PharmacyZip!='MailOrder']

    # Define variables from the input zip code and drug name to match the
    # two engineered columns
    zipcode_short = str(zipcode)[:3]
    drug_basic = drug.split()[0]
    
    # MAIL ORDER PHARMACIES
    # Attempt to get cheapest pharmacies for drug
    mail_order_options = _get_df(mail_order, drug, drug_basic)
    if not mail_order_options.empty:
        mail_order_top = _cheapest(mail_order_options, 5, 'mail order')
        mail_order_top['EstimatedPrice'] = mail_order_top.apply(lambda row: '${0:.2f}'.format(number*row.UnitCost),
                                                                axis=1)
        mail_order_top.drop(columns = ['UnitCost'], inplace=True)
    else:
        # Make a list of unique mail order pharmacy names
        mail_order_pharm = mail_order.PharmacyName.unique()
        
        # Count number of prescriptions filled by each pharmacy and create
        # a dataframe with the 5 most common
        m_o_pharm_freqs = []
        for pharmacy in mail_order_pharm:
            m_o_pharm_freqs.append(mail_order.PharmacyName.tolist().count(pharmacy))
        mail_order_args = np.sort(np.array(m_o_pharm_freqs))
        mail_order_top = pd.Series(mail_order_pharm[mail_order_args][:5])

    
    # LOCAL PHARMACIES
    # Check if zip code is in the data, then filter by zip code
    if str(zipcode) in set(zip_codes.PharmacyZip.values):
        zip_codes = zip_codes[zip_codes.PharmacyZip==zipcode]
    # Check if broader zip code is in the data, then filter
    elif zipcode_short in set(zip_codes.PharmZip.values):
        zip_codes = zip_codes[zip_codes.PharmZip == zipcode_short]
    else:
        zip_codes = pd.DataFrame()
    # Attempt to get cheapest pharmacies for drug
    local_options = _get_df(zip_codes, drug, drug_basic)
    if not local_options.empty:
        local_top = _cheapest(local_options, 5, 'local')
        local_top['EstimatedPrice'] = local_top.apply(lambda row: '${0:.2f}'.format(number*row.UnitCost),
                                                        axis=1)
        local_top.drop(columns = ['UnitCost'], inplace=True)
    # Make series of string to display
    else:
        local_top = pd.Series(data='Unfortunately, we can\'t find any pharmacies in your area, you can always try one of the mail order pharmacies.')


    return local_top, mail_order_top    
    

# Function to get best PBM for certain medication
def best_pbm_for_med(drug, df):
    # Define variable from the input drug name to match the engineered column
    drug_basic = drug.split()[0]
    
    pbm_options = _get_df(df, drug, drug_basic)
    if not pbm_options.empty:
        pbms = pbm_options.groupby(['PharmacyName']).mean()
        idx_sort = np.argsort(np.array(pbms.UnitCost.values))
        return pd.DataFrame(pbms).loc(columns=['PBMVendor', 'UnitCost']).iloc[idx_sort]
    else:
        return pd.Series('We\'re sorry. No PMBs in our records have filled a prescription for this drug.')


    
    
    
### Clayton's Code
# Effective exploratory code
#
print(df_1.PBMVendor.unique())
print(df_1.DrugLabelName.nunique())
df_1.groupby(['PBMVendor'], as_index=False)['UnitCost'].mean()
df_1.groupby(['PBMVendor','DrugLabelName'], as_index=False)['UnitCost'].mean()

# 5x for top 5 most common drugs
#
most_common = df_1[df_1.DrugLabelName != 'PROAIR HFA AER']
most_common['DrugLabelName'].value_counts().idxmax()

# Find the 5 most common druglabelnames in the dataset
# 1- LISINOPRIL
# 2- PROAIR HFA AER
# 3- FLUTICASONE SPR 50MCG
# 4- OMEPRAZOLE CAP 20MG
# 5- SIMVASTATIN

print(drug1LISIN.PBMVendor.unique())
print(drug2PRO.PBMVendor.unique())
print(drug3FLUT.PBMVendor.unique())
print(drug4OMEP.PBMVendor.unique())
print(drug5SIMVAS.PBMVendor.unique())

# PBM results
# ['MedImpact' 'Medco' 'CVSPAL4000']
# ['CVSPAL4000' 'Welldyne' 'National' 'Envision']
# ['CVSPAL4000' 'Welldyne' 'Envision']
# ['CVSPAL4000' 'Welldyne' 'Envision']
# ['MedImpact' 'Medco' 'CVSPAL4000']
#
col_list = ['PBMVendor', 'DrugLabelName']
top5drugs = df_1[col_list]

# Unique PBMs of top5drugs DF
#
top5drugs.PBMVendor.unique()

# 5 DFs for each of 5 most common drugs
drug1PRO = top5drugs.loc[top5drugs['DrugLabelName'] == 'PROAIR HFA AER']
drug2HYDRO = top5drugs.loc[top5drugs['DrugLabelName'] == 'HYDROCHLOROT TAB 25MG']
drug3AZIT = top5drugs.loc[top5drugs['DrugLabelName'] == 'AZITHROMYCIN TAB 250MG']
drug4OMEP = top5drugs.loc[top5drugs['DrugLabelName'] == 'OMEPRAZOLE CAP 20MG']
drug5LISI = top5drugs.loc[top5drugs['DrugLabelName'] == 'LISINOPRIL TAB 10MG']

# Bar Graphs for each Drug and their PBMs
drug1LISIN_2=drug1LISIN.groupby(['PBMVendor','DrugLabelName']).size()
drug1LISIN_2=drug1LISIN_2.unstack()
drug1LISIN_2.plot(kind='bar')

drug2PRO_2=drug2PRO.groupby(['PBMVendor','DrugLabelName']).size()
drug2PRO_2=drug2PRO_2.unstack()
drug2PRO_2.plot(kind='bar')

drug3FLUT_2=drug3FLUT.groupby(['PBMVendor','DrugLabelName']).size()
drug3FLUT_2=drug3FLUT_2.unstack()
drug3FLUT_2.plot(kind='bar')

drug4OMEP_2=drug4OMEP.groupby(['PBMVendor','DrugLabelName']).size()
drug4OMEP_2=drug4OMEP_2.unstack()
drug4OMEP_2.plot(kind='bar')

drug5SIMVAS_2=drug5SIMVAS.groupby(['PBMVendor','DrugLabelName']).size()
drug5SIMVAS_2=drug5SIMVAS_2.unstack()
drug5SIMVAS_2.plot(kind='bar')
