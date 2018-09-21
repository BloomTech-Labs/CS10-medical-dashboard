import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd

df = pd.read_csv('/Users/joannejordan/Desktop/RxClaims/09_20_SelectColumnsOnly.csv',
index_col='ClaimID', dtype=str, na_values=['nan', '  ', ' '])

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
        if pharm_type == 'local':
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
        if pharm_type == 'local':
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

def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))]
    )


app = dash.Dash()


app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Pharmacy Information for Patients', children=[
            html.Div([
                dcc.Markdown(d("""
                    **Save Your Money!**

                    Enter the name of your medication and the amount you are prescribed.
                    Then enter your current zip code. 
                    We'll shop around for you to see where you can get the best deal! 
                    Mail order pharmacies even come to you!

                    _prices are estimates and may not always be up to date_
                """)),
            ]),
            html.Div([
                dcc.Input(
                    id='input-1a', 
                    placeholder='name of medication',
                    type="text", 
                    value=''),
                dcc.Input(
                    id='input-2a', 
                    placeholder='quantity (e.g. number of pills, or grams)',
                    type='number', 
                    value=''),
                dcc.Input(
                    id='input-3a', 
                    placeholder='zip code',
                    type='number', 
                    value=''),
                html.Button(id='submit-button', n_clicks=0, children='Submit'),
                html.Div(id='output-a'),
            ])
        ]),
        dcc.Tab(label='Pharmacy Benefits Manager Information', children=[
            html.Div([
                dcc.Markdown(d("""
                    **Which Pharmacy Benefits Managers Work for You?**

                    Enter the name of a medication and we'll let you know which
                    Pharmacy Benefits Managers tend to negotiate the best prices.

                    _prices are estimates and may not always be up to date_
                """)),
            ]),
            html.Div([
                dcc.Input(
                    id='input-1b', 
                    placeholder='name of medication',
                    type="text", 
                    value=''),
                html.Button(id='submit-button', n_clicks=0, children='Submit'),
                html.Div(id='output-b'),
            ]),
            html.Div([
                ##Clayton must work on this...
            ]),
        ]),
    ])
])

@app.callback(
    Output('output-a', 'children'),
        [Input('submit-button', 'n_clicks')],
        [State('input-1a', 'value'),
        State('input-2a', 'value'),
        State('input-3a', 'value'),
    ])
def update_output(n_clicks, input1, input2, input3):
    local_top, mail_order_top = get_best_options(input3, input1, input2, df)
    return html.Div([
            html.Div(children=[
                html.H4(children='Local Pharmacies'),
                generate_table(local_top),
            ])
            html.Div(children=[
                html.H4(children='Mail Order Pharmacies'),
                generate_table(mail_order_top),
            ])



@app.callback(
    Output('output-b', 'children'),
        [Input('submit-button', 'n_clicks')],
        [State('input-1b', 'value'),
def update_output(n_clicks, input1):
    return html.Div(children=[
        html.H4(children='Pharmacy Benefit Managers Ranked by Price'),
        generate_table(best_pbm_for_med(input1, df)),
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
         
