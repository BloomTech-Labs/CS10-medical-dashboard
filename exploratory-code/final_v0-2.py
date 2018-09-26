
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import re

pd.set_option('display.max_rows', 25)
pd.set_option('display.max_columns', 42)
pd.set_option('display.max_colwidth', 100)


# In[2]:


upload1 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161101.csv.csv', sep='|', na_values=['nan', ' ', '  '])


# In[3]:


upload2 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161108.csv.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload4 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161116.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload5 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161122.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload6 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161129.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload7 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20161206.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload8 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170110.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload9 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170116.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload10 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170117.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload11 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170124.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload12 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170131.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload13 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170207.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload14 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170214.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload15 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170221.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)
upload16 = pd.read_csv('G:\datasets\Rx_Claims\Rx_BenefitPlan_20170301.csv', sep='|', na_values=['nan', ' ', '  '], low_memory=False)


# In[4]:


data = pd.concat([upload1, upload2, upload4, upload5, upload6, 
                  upload7, upload8, upload9, upload10, upload11, 
                  upload12, upload13, upload14, upload15, upload16])


# In[5]:


data.head()


# In[6]:


data.columns


# In[7]:


data = data.drop(axis=1, columns=['AHFSTherapeuticClassCode', 'ClaimID', 'CoInsurance',
       'CompoundDrugIndicator', 'Copay', 'DAWCode', 'DateFilled', 'DaysSupply',
       'Deductible', 'FillNumber',
       'FormularyStatus', 'GroupNumber',
       'MemberID', 'MultisourceIndicator', 
       'PaidOrAdjudicatedDate',
       'PharmacyNPI', 'PharmacyNumber',
       'PharmacyStreetAddress2',
       'PharmacyTaxId', 'PrescriberFirstName', 'PrescriberID',
       'PresriberLastName', 'RxNumber', 'SeqNum', 'UnitMeasure',
       'punbr_grnbr'])
data.columns


# In[8]:


data.shape


# In[9]:


data = data.dropna(subset=['PharmacyZip', 'ClaimStatus', 'PharmacyState', 'PharmacyStreetAddress1'])


# In[10]:


data.shape


# In[11]:


data = data[(data['MailOrderPharmacy'] != 3) & (data['MailOrderPharmacy'] != 'Y')
           & (data['MailOrderPharmacy'] != '3') & (data['MailOrderPharmacy'] != '01')
           & (data['MailOrderPharmacy'] != '06') & (data['MailOrderPharmacy'] != '08')
           & (data['MailOrderPharmacy'] != '05') & (data['MailOrderPharmacy'] != 'U')]


# In[12]:


data['MailOrderPharmacy'].unique()


# In[13]:


data['MailOrderPharmacy'].isnull().sum()


# In[14]:


data.shape


# In[15]:


data = data[(data['ClaimStatus'] == 'P')]
data.shape


# In[16]:


data.isnull().sum()


# In[17]:


# Feature Engineering by Joanne
# Calculate TotalCost in order to calculate UnitCost

def get_total(row):
    if row['IngredientCost'] and row['DispensingFee']:
        cost1 = float(row['IngredientCost']) + float(row['DispensingFee'])
    elif row['IngredientCost']:
        cost1 = float(row['IngredientCost'])
    else:
        cost1 = 0
        
    cost2 = float(row['OutOfPocket']) + float(row['PaidAmount'])
    
    return max(cost1, cost2)

data['TotalCost'] = data.apply(lambda row: get_total(row), axis=1)


# In[18]:


data.head()


# In[19]:


# Use TotalCost to calculate UnitCost

def get_unit_cost(row):
    if float(row['Quantity']) > 0:
        return float(row['TotalCost'])/float(row['Quantity'])
    else:
        return row['TotalCost']
    
data['UnitCost'] = data.apply(lambda row: get_unit_cost(row), axis=1)
data.head()


# In[20]:


# Strip white space before and after Zip, truncate to first 5 digits

data['PharmacyZip'] = data['PharmacyZip'].str.strip()
data['PharmacyZip'] = data['PharmacyZip'].str[:5]
data.head()


# In[21]:


# Add back in the leading zeroes for some zip codes

def add_zero(row):
    if len(str(row['PharmacyZip'])) < 5:
        return '0' + row['PharmacyZip']
    else:
        return row['PharmacyZip']
    
data['PharmacyZip'] = data.apply(lambda row: add_zero(row), axis=1)
print(data.shape)
data['PharmacyZip'].nunique()


# In[22]:


# Remove white space before and after Street and Name of Pharmacies

data['PharmacyStreetAddress1'] = data['PharmacyStreetAddress1'].str.strip()
data['PharmacyName'] = data['PharmacyName'].str.strip()


# In[23]:


print(data['PharmacyStreetAddress1'].value_counts())


# In[24]:


print(data['PharmacyName'].value_counts())


# In[25]:


print(data['PharmacyState'].value_counts())


# In[26]:


data['PharmacyState'].nunique()


# In[27]:


# Feature Engineer a new PharmacyID using Street and Zip

def get_id(row):
    no_spaces = str(row['PharmacyStreetAddress1'].replace(' ', ''))
    return no_spaces + row['PharmacyZip']

data['PharmacyID'] = data.apply(lambda row: get_id(row), axis=1)
print(data.shape)
data.head()


# In[28]:


data['PharmacyID'].value_counts()


# In[29]:


data = data.drop(axis=1, columns=['ClaimStatus', 'DispensingFee', 
                                  'IngredientCost', 'MailOrderPharmacy', 
                                  'OutOfPocket', 'PaidAmount', 'Quantity'])
data.head()


# In[30]:


data.isnull().sum()


# In[31]:


# Removing all whitespace from DrugLabelName

data['DrugLabelName'] = data['DrugLabelName'].str.strip()
data['DrugLabelName'] = data['DrugLabelName'].apply(lambda drug: ' '.join(drug.split()))
data['DrugLabelName'].value_counts()


# In[32]:


# Checking for correlation between counts of Name and NDC Code
# Not a 1 to 1 correlation, indicating that sometimes the doseage 
# may not be included in the Name

data['NDCCode'].value_counts()


# In[33]:


# Remove whitespace from PBMVendor to make it more useful.

data['PBMVendor'] = data['PBMVendor'].str.strip()
print(data.shape)
data.head()


# In[34]:


# Generate a drug name with no dosage and a "Regional" Zip

data['DrugShortName'] = data.apply(lambda row: row.DrugLabelName.split()[0], axis=1)
data['PharmZip'] = data.apply(lambda row: row.PharmacyZip[:3], axis=1)


# In[35]:


print(data.shape)
data.head()


# In[36]:


data.columns


# In[37]:


# Dropping columns not necessary for MVP, reordering columns in dataset

data = data.drop(axis=1, columns=['Generic', 'NDCCode',
       'PharmacyState', 'TotalCost'])
data = data[['PBMVendor', 'PharmacyID', 'DrugShortName', 
             'UnitCost', 'PharmacyName', 'PharmacyStreetAddress1', 
             'PharmacyCity', 'PharmacyZip', 'PharmZip', 'DrugLabelName']]
print(data.shape)
data.columns


# In[38]:


data.isnull().sum()


# In[39]:


data.info()


# In[40]:


# Zip codes behave better as strings.

data[['PharmacyZip', 'PharmZip']] = data[['PharmacyZip', 'PharmZip']].astype(str)
data.info()


# In[ ]:


data.to_csv('G:\\datasets\\Rx_Claims\\final_data_v0-2.csv', index=False)
