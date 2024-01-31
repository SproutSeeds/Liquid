import json
import os
import pandas as pd

class AppState:

    def __init__(self, config_file, base_dir):
        self.config_file = config_file
        self.processed_dataframe = None
        self.training_dataframe = None
        self.load_default_settings(config_file)
        self.load_processed_dataframe(base_dir)
        self.load_training_dataframe(base_dir)
    
    def load_training_dataframe(self, base_dir):
        csv_file_path = os.path.join(base_dir, 'Training_Data/1_training_data.csv')
        try:
            self.training_dataframe = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            print(f" CSV file not found at {csv_file_path}")
        except Exception as e:
            print(f"An errorr occurred while loading the CSV file: {e}")

    def load_processed_dataframe(self, base_dir):
        csv_file_path = os.path.join(base_dir, 'Transform_Data_db/output', '4_processed_stationary_data.csv')
        try:
            self.processed_dataframe = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            print(f"CSV file not found at {csv_file_path}")
        except Exception as e:
            print(f"An error occurred while loading the CSV file: {e}")

    def load_default_settings(self, file_path):
        try:
            with open(file_path, 'r') as file:
                settings = json.load(file)
                self.training_start_date = settings.get('training_start_date')
                self.training_end_date = settings.get('training_end_date')
                self.testing_start_date = settings.get('testing_start_date')
                self.testing_end_date = settings.get('testing_end_date')
                self.graphing_start_date = settings.get('graphing_start_date')
                self.graphing_end_date = settings.get('graphing_end_date')
                self.trader_made_api_key = settings.get('trader_made_api_key')
                self.fred_api_key = settings.get('fred_api_key')
                self.normalization = settings.get('normalization')
                self.standardization = settings.get('standardization')
                
        except FileNotFoundError:
            print(f"Configuration file not found: {file_path}")
            # Set some internal defaults if the file is missing
            self.training_start_date = None
            self.training_end_date = None
            self.testing_start_date = None
            self.testing_end_date = None
            self.graphing_start_date = None
            self.graphing_end_date = None
            self.trader_made_api_key = None
            self.fred_api_key = None
            self.normalization = None
            self.standardization = None

    def save_state(self):
        # Create a copy of the object's dictionary
        state_dict = self.__dict__.copy()

        # List of keys (attributes) to omit
        keys_to_omit = ['processed_dataframe', 'training_dataframe']

        # Remove the unwanted keys from the copy of the dictionary
        for key in keys_to_omit:
            state_dict.pop(key, None)  # The use of .pop() with None ensures no error if the key doesn't exist

        # Serialize and save the modified state
        with open(self.config_file, 'w') as file:
            json.dump(state_dict, file)

    def set_training_dates(self, start_date, end_date):
        self.training_start_date = start_date
        self.training_end_date = end_date
        self.save_state()
        
    def get_training_dates(self):
        return self.training_start_date, self.training_end_date

    def set_testing_dates(self, start_date, end_date):
        self.testing_start_date = start_date
        self.testing_end_date = end_date
        self.save_state()

    def get_testing_dates(self):
        return self.testing_start_date, self.testing_end_date
    
    def set_graphing_dates(self, start_date, end_date):
        self.graphing_start_date = start_date
        self.graphing_end_date = end_date
        self.save_state()

    def get_graphing_dates(self):
        return self.graphing_start_date, self.graphing_end_date
    
    def set_trader_made_api_key(self, api_key):
        self.trader_made_api_key = api_key
        self.save_state()
    
    def get_trader_made_api_key(self):
        return self.trader_made_api_key

    def set_fred_api_key(self, api_key):
        self.fred_api_key = api_key
        self.save_state()

    def get_fred_api_key(self):
        return self.fred_api_key
    
    def set_normalization(self, normal_bool):
        self.normalization = normal_bool
        self.save_state()
    
    def get_normalization(self):
        return self.normalization

    def set_standardization(self, standard_bool):
        self.standardization = standard_bool
        self.save_state()

    def get_standardization(self):
        return self.standardization
    
    def set_processed_dataframe(self, df):
        self.processed_dataframe = df

    def get_processed_dataframe(self):
        return self.processed_dataframe
    
    def set_training_dataframe(self, df):
        self.training_dataframe = df
    
    def get_training_dataframe(self):
        return self.training_dataframe