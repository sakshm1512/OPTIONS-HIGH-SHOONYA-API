import datetime
import pandas as pd


file_path_variables = 'variables.csv'
# Reading from variables.csv
variables_df = pd.read_csv(file_path_variables)
N_HOLIDAY = int(variables_df[variables_df['VARIABLE'] == 'N_HOLIDAY']['VALUE'].values[0])
BN_HOLIDAY = int(variables_df[variables_df['VARIABLE'] == 'BN_HOLIDAY']['VALUE'].values[0])
BN_HOLIDAY_NW = int(variables_df[variables_df['VARIABLE'] == 'BN_HOLIDAY_NW']['VALUE'].values[0])
FN_HOLIDAY = int(variables_df[variables_df['VARIABLE'] == 'FN_HOLIDAY']['VALUE'].values[0])
FN_HOLIDAY_NW = int(variables_df[variables_df['VARIABLE'] == 'FN_HOLIDAY_NW']['VALUE'].values[0])
N_HOLIDAY_NW = int(variables_df[variables_df['VARIABLE'] == 'N_HOLIDAY_NW']['VALUE'].values[0])




def generate_nifty_token_symbols(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()

    # Calculate the nearest Thursday expiry date
    days_until_expiry = ((3 - today.weekday() + 7)-N_HOLIDAY) % 7  # 3 is Thursday

    expiry_date = today + datetime.timedelta(days=days_until_expiry)

    # If today is after the calculated expiry date, move to the next week
    if today >= expiry_date:
        expiry_date += datetime.timedelta(days=days_until_expiry)

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"NIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols

def generate_nifty_token_symbols_next_week(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()

    # Calculate days until next week's Thursday
    days_until_next_thursday = ((7 - today.weekday() + 3) % 7) + 7  # 3 is Thursday

    expiry_date = today + datetime.timedelta(days=days_until_next_thursday)

    # Adjust for holidays
    if N_HOLIDAY_NW > 0:
        expiry_date -= datetime.timedelta(days=N_HOLIDAY_NW)  # Move back by N_HOLIDAY days

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"NIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols

def generate_bank_nifty_token_symbols(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()

    # Calculate the nearest Wednesday expiry date
    days_until_expiry = ((2 - today.weekday() + 7)-BN_HOLIDAY) % 7  # 2 is Wednesday

    expiry_date = today + datetime.timedelta(days=days_until_expiry)
    # If today is after the calculated expiry date, move to the next week
    if today >= expiry_date:
        expiry_date += datetime.timedelta(days=days_until_expiry)

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"BANKNIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols

def generate_bank_nifty_token_symbols_next_week(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()

    # Calculate days until next week's Wednesday
    days_until_next_wednesday = ((7 - today.weekday() + 2) % 7) + 7  # 2 is Wednesday

    expiry_date = today + datetime.timedelta(days=days_until_next_wednesday)

    # Adjust for holidays
    if BN_HOLIDAY_NW > 0:
        expiry_date -= datetime.timedelta(days=BN_HOLIDAY_NW)  # Move back by BN_HOLIDAY days

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"BANKNIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols

def generate_fin_nifty_token_symbols(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()

    # Calculate the nearest Thursday expiry date
    days_until_expiry = ((1 - today.weekday() + 7)-FN_HOLIDAY) % 7  # 1 is Tuesday

    expiry_date = today + datetime.timedelta(days=days_until_expiry)

    # If today is after the calculated expiry date, move to the next week
    if today >= expiry_date:
        expiry_date += datetime.timedelta(days=days_until_expiry)

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"FINNIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols

def generate_fin_nifty_token_symbols_next_week(atm, strikes):
    # today = datetime.date(2024, 7, 18)
    today = datetime.date.today()
    
    # Calculate days until next week's Tuesday
    days_until_next_tuesday = ((7 - today.weekday() + 1) % 7) + 7  # 1 is Tuesday

    expiry_date = today + datetime.timedelta(days=days_until_next_tuesday)

    # Adjust for holidays
    if FN_HOLIDAY_NW > 0:
        expiry_date -= datetime.timedelta(days=FN_HOLIDAY_NW)  # Move back by fn_holiday_nw days

    expiry_str = expiry_date.strftime('%d%b%y').upper()
    token_symbols = []
    for strike in strikes:
        option_type = 'P' if strike < atm else 'C'
        token_symbol = f"FINNIFTY{expiry_str}{option_type}{strike}"
        token_symbols.append(token_symbol)

    return token_symbols