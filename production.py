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


# Get rid of erroneous white space in DrugLabelName
drug_names['DrugLabelName'] = drug_names['DrugLabelName'].apply(lambda drug: ' '.join(drug.split()))

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



# Simple function to print the cheapest pharmacy for given drug in given zipcode from table.
# No checks for errors included, mail order drugs not compared.
def get_cheapest_pharm(zipcode, drug, table):
    # Filter table by zipcode then drug
    table = table[table.PharmacyZip==str(zipcode)]
    table = table[table.DrugLabelName==str(drug)]
    # Group remaining claims by Pharmacy then take mean of numeric values
    pharmacies = table.groupby(['PharmacyName']).mean()
    # Return pharmacy name for min unit cost
    pharmacy = pharmacies.UnitCost.idxmin()
    # Filter table by pharmacy name so we can print address and city with name
    table = table[table.PharmacyName==pharmacy]
    print('Pharmacy:\n{}\nAddress:\n{}\n{}'.format(table.PharmacyName.iloc[0],
                                                   table.PharmacyStreetAddress1.iloc[0],
                                                   table.PharmacyCity.iloc[0]))







### Clayton's Code
print(df_1.PBMVendor.unique())
print(df_1.DrugLabelName.nunique())

# Cheapest PBM Overall
#
#
# Create DF of ['PBMVendor', 'DrugShortName', 'UnitCost'] columns
col_list = ['PBMVendor', 'DrugShortName', 'UnitCost']
df_pbm_drug_cost = df_1[col_list]

# Separate DF in to 1 DF per PBM
df_MedImpact = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'MedImpact']
df_CVSPAL4000 = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'CVSPAL4000']
df_SouthernScripts = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'SouthernScripts']

df_Nemop = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'Nemop']
df_Magellan = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'Magellan']

# Welldyne 11,627 rows
df_Welldyne = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'Welldyne']

# National 1,286 rows
df_National = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'National']

# Envision 89,209 rows
df_Envision = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'Envision']
df_Medco = df_pbm_drug_cost[df_pbm_drug_cost.PBMVendor == 'Medco']

# Finds Intersection of DrugShortName for each PBM in df_1
all_drugs = (set(df_MedImpact.DrugShortName.values) and
             set(df_CVSPAL4000.DrugShortName.values) and
             set(df_SouthernScripts.DrugShortName.values) and
             set(df_Nemop.DrugShortName.values) and
             set(df_Magellan.DrugShortName.values) and
             set(df_Welldyne.DrugShortName.values) and
             set(df_National.DrugShortName.values) and
             set(df_Envision.DrugShortName.values) and
             set(df_Medco.DrugShortName.values));

# Filter so only those drugs exist in each PMB DF
df_MedImpact = df_MedImpact[df_MedImpact['DrugShortName'].isin(all_drugs)]
df_CVSPAL4000 = df_CVSPAL4000[df_CVSPAL4000['DrugShortName'].isin(all_drugs)]
df_SouthernScripts = df_SouthernScripts[df_SouthernScripts['DrugShortName'].isin(all_drugs)]

df_Nemop = df_Nemop[df_Nemop['DrugShortName'].isin(all_drugs)]
df_Magellan = df_Magellan[df_Magellan['DrugShortName'].isin(all_drugs)]
df_Welldyne = df_Welldyne[df_Welldyne['DrugShortName'].isin(all_drugs)]

df_National = df_National[df_National['DrugShortName'].isin(all_drugs)]
df_Envision = df_Envision[df_Envision['DrugShortName'].isin(all_drugs)]
df_Medco = df_Medco[df_Medco['DrugShortName'].isin(all_drugs)]

# For EACH drug, find PBM with lowest cost
# Average drug UnitCost for each drug per PBM
# UC = UnitCost
df_MedImpact_avg_UC = df_MedImpact.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_CVSPAL4000_avg_UC = df_CVSPAL4000.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_SouthernScripts_avg_UC = df_SouthernScripts.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()

df_Nemop_avg_UC = df_Nemop.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_Magellan_avg_UC = df_Magellan.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_Welldyne_avg_UC = df_Welldyne.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()

df_National_avg_UC = df_National.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_Envision_avg_UC = df_Envision.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()
df_Medco_avg_UC = df_Medco.groupby(['DrugShortName'], as_index=False)['UnitCost'].mean()

# UnitCost avg of all drugs PER PBM

# Total # of Rows: 3,660,707

# 393,816 rows with df_1.PBMVendor == MedImpact
df_MedImpact_avg_UC['UnitCost'].mean()
# DrugLabelName: 71.75219318813778
# DrugShortName: 64.44488749956898

# 2,455,032 rows with df_1.PBMVendor == CVSPAL4000
df_CVSPAL4000_avg_UC['UnitCost'].mean()
# DrugLabelName: 61.51118988815909
# DrugShortName: 89.12452585515857

# 15,225 rows with df_1.PBMVendor == SouthernScripts
df_SouthernScripts_avg_UC['UnitCost'].mean()
# DrugLabelName: 0.792625
# DrugShortName: 1.5449279328165377

# 4,657 rows with df_1.PBMVendor == Nemop
df_Nemop_avg_UC['UnitCost'].mean()
# DrugLabelName: 32.01
# DrugShortName: 9.555713468720821

# 95,969 rows with df_1.PBMVendor == Magellan
df_Magellan_avg_UC['UnitCost'].mean()
# DrugLabelName: 6.531493055555555
# DrugShortName: 47.544123990240315

# 11,627 rows with df_1.PBMVendor == Welldyne
df_Welldyne_avg_UC['UnitCost'].mean()
# DrugLabelName: nan
# DrugShortName: 203.62729668974353

# 1,286 rows with df_1.PBMVendor == National
df_National_avg_UC['UnitCost'].mean()
# DrugLabelName: nan
# DrugShortName: 11.161770536432297

# 89,209 rows with df_1.PBMVendor == Envision
df_Envision_avg_UC['UnitCost'].mean()
# DrugLabelName: nan
# DrugShortName: 95.13871288531323

# 593,886 rows with df_1.PBMVendor == Medco
df_Medco_avg_UC['UnitCost'].mean()
# DrugLabelName: 95.43536290363183
# DrugShortName: 100.33072460418295

dfff = pd.DataFrame({'PBMVendor':['MedImpact\n:Rows:393,816',
                                  'CVSPAL4000\n:Rows:2,455,032',
                                  'SouthernScripts\n:Rows:15,225',
                                  'Nemop\n:Rows:4,657',
                                  'Magellan\n:Rows:95,969',
                                  'Welldyne\n:Rows:11,627',
                                  'National\n:Rows:1,286',
                                  'Envision\n:Rows:89,209',
                                  'Medco\n:Rows:593,886'],
                    'AvgUnitCost':[64.42,
                                   89.12,
                                   1.54,
                                   9.55,
                                   47.54,
                                   203.62,
                                   11.16,
                                   95.13,
                                   100.32]})

dfff = dfff.reindex_axis(['PBMVendor','AvgUnitCost'], axis=1)
dfff

dfff.plot.bar(x='PBMVendor', y='AvgUnitCost', rot=45)
