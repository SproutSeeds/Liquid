import requests
import pandas as pd
# from utilities import log_message
import utilities
# from json_handler import update_last_pull_timestamp, read_last_pull_timestamp, check_last_pull_was_today
import json_handler
import os
from datetime import datetime

def fetch_economic_data(api_key, data_type, base_dir):
    series_id = None
    utilities.log_message(f"this is inside the final fetch economic data, this is the API KEY for FRED {api_key}", console_output=False)
    
    if not api_key:
        print("API key is missing. Please enter an API key.")
        return None
    
    utilities.log_message(f"data_type = {data_type}",console_output=False)
    utilities.log_message(f"data_type TYPE is {type(data_type)}",console_output=False)
    
    utilities.log_message(f"data_type is equal to Federal Funds Rate {data_type=='Federal Funds Interest Rate'}", console_output=False)
     
        
    if data_type == "Federal Funds Interest Rate":
        series_id = "FEDFUNDS"  # Series ID for Non-Farm Employment Change
    elif data_type == "Non-Farm Employees":
        series_id = "PAYEMS"  # Series ID for Unemployment Rate
    elif data_type == "Unemployment Rate":
        series_id = "UNRATE"  # Series ID for Federal Funds Rate
    elif data_type == "GDP Reports":
        series_id = "GDP"
    elif data_type == "Inflation Data (CPI)":
        series_id = "CPIAUCSL"
    
    utilities.log_message(f"Series ID variable is {series_id} after the else if statements in api_interaction.py", console_output=False)
    
    if not json_handler.check_last_pull_was_today("Economic Data", data_type, base_dir):
        url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'
        response = requests.get(url)

        if response.status_code == 200:
            #update the last pull timestamp
            json_handler.update_last_pull_timestamp("Economic Data",f"{data_type}", base_dir)
            
            utilities.log_message(f"success! Retrieving data now...", console_output=True)
            
            
            data = response.json()
            observations = data.get('observations', [])
            
            if observations:
                df = pd.DataFrame(observations)
                
                first_row = df.iloc[0] if not df.empty else "No data available"
                utilities.log_message(f"Data Example:\n{first_row}", console_output=True)
                
                csv_file_name = f"Historical_Data\\{data_type}_history.csv"
                absolute_file_path = utilities.resource_path(csv_file_name, base_dir)

                df.to_csv(absolute_file_path, index=False)
                utilities.log_message(f"Data saved in the Historical folder as {absolute_file_path}", console_output=True)
            else:
                utilities.log_message("No data found.",console_output=True)
        else:
            utilities.log_message(f"Error fetching data: {response.status_code}", console_output=True)
    else:
        utilities.log_message(f"Data for {data_type} was already pulled today. Skipping API request.", console_output=True)
    
def fetch_yearly_data(api_key, currency_pair, start_date, end_date, base_dir):
    utilities.log_message(f"Fetching year of data for {currency_pair}. {start_date} to {end_date}", console_output=True)

    url = f"https://marketdata.tradermade.com/api/v1/timeseries?currency={currency_pair}&api_key={api_key}&start_date={start_date}&end_date={end_date}&format=records"
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = response.json()
        if "quotes" in json_data:
            json_handler.update_last_pull_timestamp("Currency Pairs",f"{currency_pair}", base_dir)
            return json_data["quotes"]
        else:
            print(f"No data found for {start_date} to {end_date}")
            return []
    else:
        print(f"Error fetching data for {start_date} to {end_date}: {response.status_code}")
        return []
        
def fetch_historical_currency_data(api_key, currency_pair, base_dir):
    if not json_handler.check_last_pull_was_today("Currency Pairs", currency_pair, base_dir):
        current_year = datetime.now().year
        today_date = datetime.now().strftime("%Y-%m-%d")
        all_data = []

        for year in range(current_year, 1994, -1):  # Assuming 1995 as the earliest year
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31" if year != current_year else today_date

            yearly_data = fetch_yearly_data(api_key, currency_pair, start_date, end_date, base_dir)
            if yearly_data:
                all_data.extend(yearly_data)
            else:
                print(f"No more data available for {year}")
                break

        if all_data:
            df = pd.DataFrame(all_data)
            
            columns_order = ['date', 'open', 'high', 'low', 'close']
            df = df[columns_order]

            # Convert 'date' column to datetime format
            df['date'] = pd.to_datetime(df['date'])

            # Sorting DataFrame by 'date' from oldest to newest
            df.sort_values('date', inplace=True)

            # Resetting the index 
            df.reset_index(drop=True, inplace=True)
            
            # Construct the file path
            file_path = os.path.join("Historical_Data", f"{currency_pair}_historical_data.csv")
            absolute_file_path = utilities.resource_path(file_path, base_dir)
            df.to_csv(absolute_file_path, index=False)
            print(f"Data saved for {currency_pair} from 1995 to {current_year} in '{absolute_file_path}'")
        else:
            print("No data found.")
    else:
        utilities.log_message(f"Data for {currency_pair} was already pulled today. Skipping API request.", console_output=True)


def fetch_all_currency_pairs_data(global_currency_list, api_key):
    # List of all currency pairs you want to fetch data for
    currency_pairs = global_currency_list  # Add all pairs here
    
    for pair in currency_pairs:
            
            # Call the function to fetch data for the current pair
            fetch_historical_currency_data(api_key, pair)

    print("All data fetched.")