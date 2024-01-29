import json
from datetime import datetime
# from utilities import log_message
import utilities

def read_last_pull_timestamp(data_type, key, base_dir):
    utilities.log_message("We are inside the read_last_pull_timestamp()",console_output=False)
    try:
        last_pull_file = utilities.resource_path('last_pull.json', base_dir)

        with open(last_pull_file, "r") as file:
            data = json.load(file)
            return data.get(data_type, {}).get(key)
            
    except (FileNotFoundError, json.JSONDecodeError):
        update_last_pull_timestamp(data_type, key, base_dir)
        return None

def update_last_pull_timestamp(data_type, key, base_dir):
    utilities.log_message("We are inside the update_last_pull_timestamp()",console_output=False)

    current_timestamp = datetime.now().isoformat()
    
    utilities.log_message(f"The current timestamp is {current_timestamp}",console_output=False)
    
    try:
        last_pull_file = utilities.resource_path('last_pull.json', base_dir)

        with open(last_pull_file, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if data_type not in data:
        utilities.log_message("We are inside the 'if data_type not in data' block of update_last_pull_timestamp, because the data type is not equal to nunll",console_output=False)
        
        data[data_type] = {}
    
    data[data_type][key] = current_timestamp
    utilities.log_message(f"the timestamp update for this data pull is {data[data_type][key]}",console_output=False)
    
    last_pull_file = utilities.resource_path('last_pull.json', base_dir)

    with open(last_pull_file, "w") as file:
        utilities.log_message(f"This is the data that is being posted to the last_pull.json file:\n\n\n{data}\n\n\n",console_output=False)
        json.dump(data, file)

def check_last_pull_was_today(data_type, key, base_dir):
    utilities.log_message("We are inside the check_last_pull_was_today()",console_output=False)

    # Read the last pull timestamp
    last_pull_timestamp = read_last_pull_timestamp(data_type, key, base_dir)
    utilities.log_message(f"The last pull timestamp for {data_type} is {last_pull_timestamp}",console_output=False)
    
    if last_pull_timestamp is None:
        # No timestamp found (assume it was not pulled today)
        utilities.log_message("We should be making it here when the value is null/none ",console_output=False)
        
        return False
    
    # Convert the timestamp to a datetime object    
    last_pull_datetime = datetime.fromisoformat(last_pull_timestamp)
    utilities.log_message(f"After conversion of last_pull_datetime to isoformat {last_pull_datetime}",console_output=False)
    
    # Get the current date
    current_date = datetime.now().date()
    
     # Compare the dates
    if last_pull_datetime.date() == current_date:
        # The data was pulled today
        return True
    else:
        # The data was not pulled today
        return False
    
def save_api_keys(api_key, api_key_type, base_dir, settings_path="settings.json", frame=None):
    # Update the settings.json file with the new API key and hide the input frame

    try:
        the_settings_path = utilities.resource_path(settings_path, base_dir)

        with open(the_settings_path, 'r+') as file:
            settings = json.load(file)
            if api_key_type == 'fred':
                settings['fred_api_key'] = api_key
            elif api_key_type == 'trader_made':
                settings['trader_made_api_key'] = api_key
            file.seek(0)
            json.dump(settings, file, indent=4)
            file.truncate()
        utilities.log_message(f"{api_key_type.replace('_', ' ').title()} API key saved.")
        if frame:
            frame.pack_forget()  # Hide the input frame
    except Exception as e:
        utilities.log_message(f"Error saving {api_key_type.replace('_', ' ').title()} API key: {e}")

def check_all_economic_data_pulled_today(json_file_path, base_dir):
    try:
        absolute_file_path = utilities.resource_path(json_file_path, base_dir)
        # Read the JSON file
        with open(absolute_file_path, 'r') as file:
            data = json.load(file)

        # Assuming the JSON structure is something like: 
        # {"economic_data": {"data1": "2024-01-26", "data2": "2024-01-26", ...}}

        # Get the current date
        current_date = datetime.now().date()

        for last_pull_date in data.get("Economic Data", {}).values():
            if datetime.fromisoformat(last_pull_date).date() != current_date:
                # print("Did nott equal last pull date...")
                return False
        return True

    except Exception as e:
        print(f"Error checking data pull dates: {e}")
        return False