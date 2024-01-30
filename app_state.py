import json

class AppState:

    def __init__(self, config_file):
        self.load_default_settings(config_file)

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
        except FileNotFoundError:
            print(f"Configuration file not found: {file_path}")
            # Set some internal defaults if the file is missing
            self.training_start_date = None
            self.training_end_date = None
            self.testing_start_date = None
            self.testing_end_date = None
            self.graphing_start_date = None
            self.graphing_end_date = None


    def set_training_dates(self, start_date, end_date):
        self.training_start_date = start_date
        self.training_end_date = end_date
        
    def get_training_dates(self):
        return self.training_start_date, self.training_end_date

    def set_testing_dates(self, start_date, end_date):
        self.testing_start_date = start_date
        self.testing_end_date = end_date

    def get_testing_dates(self):
        return self.testing_start_date, self.testing_end_date
    
    def set_graphing_dates(self, start_date, end_date):
        self.graphing_start_date = start_date
        self.graphing_end_date = end_date

    def get_graphing_dates(self):
        return self.graphing_start_date, self.graphing_end_date