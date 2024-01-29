import json
import utilities

def load_settings(file_path):
    try:
        absolute_file_path = utilities.resource_path(file_path)
        with open(absolute_file_path, 'r') as file:
            settings = json.load(file)
            return settings
    except FileNotFoundError:
        print(f"Settings file not found: {absolute_file_path}.")
        return {}

def save_settings(file_path, settings):
    absolute_file_path = utilities.resource_path(file_path)
    with open(absolute_file_path, 'w') as file:
        json.dump(settings, file)

# Example usage
# settings = load_settings('settings.json')
# save_settings('settings.json', settings)
 
