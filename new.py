import logging
import datetime
from datetime import date
import pyotp
from collections import OrderedDict
import numpy as np
import pandas as pd  # To read the CSV file
from NorenRestApiPy.NorenApi import NorenApi
from api_helper import ShoonyaApiPy
import time
import os
import Shoonya as shoon

# Function to attempt an API call with retries
def api_try(call_func, max_retries=5, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            result = call_func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"Error on attempt {attempt + 1} for {call_func.__name__}: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # Wait a bit before retrying

# Start of our program
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')

# Initialize the API
api = ShoonyaApiPy()

# Credentials
user = ''
pwd = ''
vc = ''
app_key = ''
imei = ''
token = ''

# Login
ret = api_try(api.login, 5, userid=user, password=pwd, twoFA=pyotp.TOTP(token).now(), vendor_code=vc, api_secret=app_key, imei=imei)
print("Login Response:", ret['stat'])

file_path_variables = 'variables.csv'
variables_df = pd.read_csv(file_path_variables)

START_H = int(variables_df[variables_df['VARIABLE'] == 'START_H']['VALUE'].values[0])
START_M = int(variables_df[variables_df['VARIABLE'] == 'START_M']['VALUE'].values[0])
SELL_H = int(variables_df[variables_df['VARIABLE'] == 'SELL_H']['VALUE'].values[0])
SELL_M = int(variables_df[variables_df['VARIABLE'] == 'SELL_M']['VALUE'].values[0])
TARGET_H = int(variables_df[variables_df['VARIABLE'] == 'STOP_H']['VALUE'].values[0])
TARGET_M = int(variables_df[variables_df['VARIABLE'] == 'STOP_M']['VALUE'].values[0])

# Current time and target times
current_time = datetime.datetime.now()
target_time = datetime.datetime(
    year=current_time.year, month=current_time.month, day=current_time.day, hour=TARGET_H, minute=TARGET_M, second=0)
start_time = datetime.datetime(
    year=current_time.year, month=current_time.month, day=current_time.day, hour=START_H, minute=START_M, second=00)
time_buy = datetime.datetime(
    year=current_time.year, month=current_time.month, day=current_time.day, hour=SELL_H, minute=SELL_M, second=0)

# initialising active order book
file_name_aob = f"ActiveOrderBook.csv"
file_path_aob = file_name_aob

if not os.path.exists(file_path_aob):
    # Create the file if it doesn't exist
    with open(file_path_aob, 'w'):
        pass

aob = pd.DataFrame(columns= ['Token', 'Symbol', 'OrderNo', 'Time Of Order', 'No of lots', 'Price'])
aob = aob.drop(aob.index)
aob.to_csv(file_path_aob, index=False)
aob = pd.read_csv(file_path_aob) 

def round_to_nearest_fifty(price):
    return round(price / 50.0) * 50

def round_to_nearest_hundred(price):
    return round(price / 100.0) * 100

feed_opened = False
token_percentage_dict = {}  # Dictionary to store tokens and their respective percentages

def event_handler_feed_update(tick_data):
    # Check if 'pc' is in the tick data
    if 'pc' in tick_data:
        token = tick_data.get('tk', None)
        pc = float(tick_data['pc'])
        if token:
            token_percentage_dict[token] = pc  # Update the dictionary
            # print(f"[{token}, {pc}]")  # Print the token and percentage change

def event_handler_order_update(tick_data):
    print(f"Order update: {tick_data}")

def open_callback():
    global feed_opened
    feed_opened = True
    print("WebSocket connection opened")

def LotSize(input_str):
    if input_str[0] == 'N':
        return 25
    elif input_str[0] == 'B':
        return 15
    elif input_str[0] == 'F':
        return 25
    
def calculate_entry_price(token, percentage):
    if token in token_close:
        entry_price = token_close[token] * (1 + percentage / 100)
        rounded_price = round(entry_price / 0.05) * 0.05
        formatted_price = round(rounded_price, 2)  # Round to 2 decimal places
        return formatted_price
    else:
        return None

def buy_price_calc(input_value, reduction_percent):
    reduction_factor = float(reduction_percent / 100)
    result = float(input_value - (reduction_factor * input_value))
    return round(round(result / 0.05) * 0.05 , 2)
    
# Read the CSV file
# Load the CSV file
token_data = pd.read_csv('token_symbols.csv')

# Create the dictionaries for Bank Nifty, Nifty, and token to close price
nifty_dict = {}
nifty_nw_dict = {}
bank_nifty_dict = {}
bank_nifty_nw_dict = {}
fin_nifty_dict = {}
fin_nifty_nw_dict = {}
token_close = {}

# Load data from DataFrame
entry_limit = 121
dicts = [nifty_dict, nifty_nw_dict, bank_nifty_dict, bank_nifty_nw_dict, fin_nifty_dict, fin_nifty_nw_dict]

# Fill dictionaries sequentially with 121 entries each
for i, row in token_data.iterrows():
    symbol = row['Symbol']
    token = row['Token']
    strike = row['Strike']
    close_price = row['Close Price']

    dict_index = i // entry_limit
    if dict_index < len(dicts):
        dicts[dict_index][token] = strike
    
    token_close[token] = close_price

# Print the dictionaries
print("Nifty Dictionary:")
print(nifty_dict)
print("Nifty NW Dictionary:")
print(nifty_nw_dict)
print("Bank Nifty Dictionary:")
print(bank_nifty_dict)
print("Bank Nifty NW Dictionary:")
print(bank_nifty_nw_dict)
print("Fin Nifty Dictionary:")
print(fin_nifty_dict)
print("Fin Nifty NW Dictionary:")
print(fin_nifty_nw_dict)
print("Token to Close Price Dictionary:")
print(token_close)

# Create the subscription list
subscription_list = [f'NFO|{token}' for token in token_data['Token']]
# print(subscription_list)

# Start WebSocket
api_try(api.start_websocket, 5,
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_feed_update,
        socket_open_callback=open_callback)

# Wait for WebSocket connection to open
while not feed_opened:
    time.sleep(0.1)

# Subscribe to tokens from CSV
subscription_response = api_try(api.subscribe, 5, subscription_list)
print("Subscription Response:", subscription_response)

def filter_dict_by_percentage(data_dict, threshold):
    return {k: v for k, v in data_dict.items() if v > threshold}

while current_time<start_time:
    print('waiting...')
    current_time = datetime.datetime.now()

count = 1
traded_keys = set()
while start_time < datetime.datetime.now() < target_time:
    time.sleep(.5)
    print(f"Count: {count}")
    count += 1
    variables_df = pd.read_csv(file_path_variables)
    ENTRY_PERCENTAGE = int(variables_df[variables_df['VARIABLE'] == 'ENTRY_PERCENTAGE']['VALUE'].values[0])
    TARGET_PERCENTAGE = int(variables_df[variables_df['VARIABLE'] == 'TARGET_PERCENTAGE']['VALUE'].values[0])
    MAX_POSITIONS = int(variables_df[variables_df['VARIABLE'] == 'MAX_POSITIONS']['VALUE'].values[0])
    MAX_STRIKES = int(variables_df[variables_df['VARIABLE'] == 'MAX_STRIKES']['VALUE'].values[0])
    NIFTY_ENTRY_HL = int(variables_df[variables_df['VARIABLE'] == 'NIFTY_ENTRY_HL']['VALUE'].values[0])
    BN_ENTRY_HL = int(variables_df[variables_df['VARIABLE'] == 'BN_ENTRY_HL']['VALUE'].values[0])
    FINNIFTY_ENTRY_HL = int(variables_df[variables_df['VARIABLE'] == 'FINNIFTY_ENTRY_HL']['VALUE'].values[0])
    STRIKE_DIFF_N_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_N_UL']['VALUE'].values[0])
    STRIKE_DIFF_N_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_N_LL']['VALUE'].values[0])
    STRIKE_DIFF_FN_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_FN_UL']['VALUE'].values[0])
    STRIKE_DIFF_FN_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_FN_LL']['VALUE'].values[0])
    STRIKE_DIFF_BN_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_BN_UL']['VALUE'].values[0])
    STRIKE_DIFF_BN_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_BN_LL']['VALUE'].values[0])
    STRIKE_DIFF_N_NW_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_N_NW_UL']['VALUE'].values[0])
    STRIKE_DIFF_N_NW_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_N_NW_LL']['VALUE'].values[0])
    STRIKE_DIFF_FN_NW_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_FN_NW_UL']['VALUE'].values[0])
    STRIKE_DIFF_FN_NW_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_FN_NW_LL']['VALUE'].values[0])
    STRIKE_DIFF_BN_NW_UL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_BN_NW_UL']['VALUE'].values[0])
    STRIKE_DIFF_BN_NW_LL = int(variables_df[variables_df['VARIABLE'] == 'STRIKE_DIFF_BN_NW_LL']['VALUE'].values[0])
    STRIKE_LOW_EXCLUDE = float(variables_df[variables_df['VARIABLE'] == 'STRIKE_LOW_EXCLUDE']['VALUE'].values[0])

    # Get quotes for Nifty 50
    open_n = api_try(api.get_quotes, 5, exchange='NSE', token='26000')
    close_n = open_n['c']
    lp_n = open_n['lp']
    lp_n = float(lp_n)  # Convert to float
    atm_n = round_to_nearest_fifty(lp_n)

    # Get quotes for Fin Nifty 
    open_fn = api_try(api.get_quotes, 5, exchange='NSE', token='26037')
    close_fn = open_fn['c']
    lp_fn = open_fn['lp']
    lp_fn = float(lp_fn)  # Convert to float
    atm_fn = round_to_nearest_fifty(lp_fn)

    # Get quotes for Bank Nifty
    open_bn = api_try(api.get_quotes, 5, exchange='NSE', token='26009')
    close_bn = open_bn['c']
    lp_bn = open_bn['lp']
    lp_bn = float(lp_bn)  # Convert to float
    atm_bn = round_to_nearest_hundred(lp_bn)

    # Calculate the absolute difference for Bank Nifty
    entry_bn = abs(float(close_bn) - lp_bn)
    entry_bn_nw = abs(float(close_bn) - lp_bn)

    # Calculate the absolute difference for Nifty 50
    entry_n = abs(float(close_n) - lp_n)
    entry_n_nw = abs(float(close_n) - lp_n)

    # Calculate the absolute difference for Fin Nifty 
    entry_fn = abs(float(close_fn) - lp_fn)
    entry_fn_nw = abs(float(close_fn) - lp_fn)

    fortrade = {}
    final = {}

    if entry_bn < BN_ENTRY_HL:
        lower_bound = atm_bn - STRIKE_DIFF_BN_UL
        upper_bound = atm_bn + STRIKE_DIFF_BN_LL

        # Filter Bank Nifty strikes
        for token, strike in bank_nifty_dict.items():
            if strike < lower_bound or strike > upper_bound:
                fortrade[token] = strike
    
    if entry_bn_nw < BN_ENTRY_HL:
        lower_bound = atm_bn - STRIKE_DIFF_BN_NW_UL
        upper_bound = atm_bn + STRIKE_DIFF_BN_NW_LL

        # Filter Bank Nifty strikes
        for token, strike in bank_nifty_nw_dict.items():
            if strike < lower_bound or strike > upper_bound:
                fortrade[token] = strike

    if entry_n < NIFTY_ENTRY_HL:
        lower_bound_n = atm_n - STRIKE_DIFF_N_UL
        upper_bound_n = atm_n + STRIKE_DIFF_N_LL

        # Filter Nifty 50 strikes
        for token, strike in nifty_dict.items():
            if strike < lower_bound_n or strike > upper_bound_n:
                fortrade[token] = strike
    
    if entry_n_nw < NIFTY_ENTRY_HL:
        lower_bound_n = atm_n - STRIKE_DIFF_N_NW_UL
        upper_bound_n = atm_n + STRIKE_DIFF_N_NW_LL

        # Filter Nifty 50 strikes
        for token, strike in nifty_nw_dict.items():
            if strike < lower_bound_n or strike > upper_bound_n:
                fortrade[token] = strike
    
    if entry_fn < FINNIFTY_ENTRY_HL:
        lower_bound_fn = atm_fn - STRIKE_DIFF_FN_UL
        upper_bound_fn = atm_fn + STRIKE_DIFF_FN_LL

        # Filter Fin Nifty strikes
        for token, strike in fin_nifty_dict.items():
            if strike < lower_bound_fn or strike > upper_bound_fn:
                fortrade[token] = strike
    
    if entry_fn_nw < FINNIFTY_ENTRY_HL:
        lower_bound_fn = atm_fn - STRIKE_DIFF_FN_NW_UL
        upper_bound_fn = atm_fn + STRIKE_DIFF_FN_NW_LL

        # Filter Fin Nifty strikes
        for token, strike in fin_nifty_nw_dict.items():
            if strike < lower_bound_fn or strike > upper_bound_fn:
                fortrade[token] = strike

    print("Combined Trades Dictionary (fortrade):", fortrade)

    filtered_dict = filter_dict_by_percentage(token_percentage_dict, ENTRY_PERCENTAGE)
    filtered_dict = {int(token): percentage for token, percentage in filtered_dict.items()}
    print("Filtered Dictionary (filtered_dict):", filtered_dict)

    # Create final dictionary with tokens common in fortrade and filtered_dict
    for token in fortrade:
        if token in filtered_dict:
            final[token] = filtered_dict[token]
    
    # Filter out tokens with close price less than 1
    final = {token: percentage for token, percentage in final.items() if token_close.get(token, 0) >= STRIKE_LOW_EXCLUDE}
    final = dict(sorted(final.items(), key=lambda item: item[1], reverse=True))

    print("Final Dictionary (final):", final)
    symbol_names = {}
    for index, row in token_data.iterrows():
        token = int(row['Token'])  # Convert token to integer for matching
        if token in final:
            symbol_names[token] = row['Symbol']
    for token, symbol in symbol_names.items():
        print(f"Token: {token}, Symbol: {symbol}")
    
    aob = pd.read_csv(file_path_aob)
    if current_time>start_time and current_time<time_buy:
        for key in symbol_names:
            total_sum = int(aob['No of lots'].sum())
            if key not in traded_keys and total_sum < MAX_STRIKES:
                print('sell')
                price = calculate_entry_price(key, ENTRY_PERCENTAGE)
                print(price)
                symbol = token_data.loc[token_data['Token'] == key, 'Symbol'].values[0]
                print(symbol)
                lotsize = int(LotSize(symbol))
                lotsize = lotsize * MAX_POSITIONS
                print(lotsize)
                sell = shoon.sellMarket(str(symbol), int(lotsize), float(price))  # Direct API call without api_try
                if sell[0] == 'COMPLETE':
                    print('buy')
                    avgprc = sell[2]
                    print(avgprc)
                    price_buy = buy_price_calc(float(avgprc) , TARGET_PERCENTAGE)
                    print(symbol)
                    print(price_buy)
                    print(lotsize)
                    buy = shoon.buyMarket_LMT_DAY(str(symbol), int(lotsize), float(price_buy))  # Direct API call without api_try
                    aob.loc[len(aob)] = [str(key), str(symbol), 1111, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), MAX_POSITIONS, price]
                    aob.to_csv(file_path_aob,index=False)
                    traded_keys.add(key)
                else:
                    print('failed order')
    
    current_time = datetime.datetime.now()

print("Time range ended, exiting the loop.") 
