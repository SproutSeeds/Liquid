import sys
import os
import datetime
import shutil

def resource_path(relative_path, base_dir=None):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if base_dir is None:
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


def current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Example of a logging function
def log_message(message, log_file="app_log.txt", console_output=True):
    timestamp = current_timestamp()

    absolute_file_path = resource_path(log_file)

    with open(absolute_file_path, "a") as file:
        file.write(f"[{timestamp}] {message}\n")
    
    if console_output:
        print(message)

def create_missing_files_and_folders(base_dir):
    required_files_and_folders = [
        ('Historical_Data', 'Historical_Data'),
        ('Transform_Data_db/output', 'Transform_Data_db/output'),
        # ... add other folders if needed
    ]

    root_files = ['app_log.txt', 'settings.json', 'last_pull.json']

    # The directory where the bundled data is located, typically _MEIPASS when frozen
    bundled_data_dir = getattr(sys, '_MEIPASS', base_dir)

    # Use base_dir as the destination directory
    destination_directory = base_dir

    # Copy the root files (only when running from the compiled executable)
    if hasattr(sys, '_MEIPASS'):
        copy_root_files(bundled_data_dir, destination_directory, root_files)

    # Copy the folders and their contents (only when running from the compiled executable)
    if hasattr(sys, '_MEIPASS'):
        for src, dst in required_files_and_folders:
            src_path = os.path.join(bundled_data_dir, src)
            dst_path = os.path.join(destination_directory, dst)

            if os.path.exists(dst_path):
                if os.path.isdir(src_path) and os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)  # Remove the existing directory first
                else:
                    os.remove(dst_path)  # Remove the existing file first
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)
    if not hasattr(sys, '_MEIPASS'):
        # Define the directory path
        historical_data_dir = os.path.join(base_dir, 'Historical_Data')
        Transform_Data_db_dir = os.path.join(base_dir, 'Transform_Data_db')
        output_dir = os.path.join(base_dir, "Transform_Data_db/output")

        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(historical_data_dir):
            os.makedirs(historical_data_dir)

        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(Transform_Data_db_dir):
            os.makedirs(Transform_Data_db_dir)
        
        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

def copy_root_files(src_dir, dst_dir, file_list):
    for file_name in file_list:
        src_file_path = os.path.join(src_dir, file_name)
        dst_file_path = os.path.join(dst_dir, file_name)
        if os.path.exists(src_file_path):
            shutil.copy(src_file_path, dst_file_path)

def get_base_dir():
    # If the application is frozen using a bundler like PyInstaller, sys.executable
    # will be the path to the executable; otherwise, it's the path to the Python interpreter
    if getattr(sys, 'frozen', False):
        # The application is frozen (packaged into an executable)
        return os.path.dirname(sys.executable)
    else:
        # The application is not frozen (running as a script)
        return os.path.dirname(os.path.abspath(__file__))

# Other utility functions can be added here
 
