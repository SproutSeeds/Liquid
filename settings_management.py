import json
import os
import tempfile
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
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=os.path.dirname(absolute_file_path),
                                         prefix='.settings-', delete=False) as file:
            temporary_path = file.name
            file.write(json.JSONEncoder().encode(settings))
        os.replace(temporary_path, absolute_file_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)

# Example usage
# settings = load_settings('settings.json')
# save_settings('settings.json', settings)
 
