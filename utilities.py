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
    required_directories = [
        'Historical_Data',
        'Transform_Data_db/output',
        'Training_Data'
        # ... add other folders if needed
    ]

    root_files = ['app_log.txt', 'settings.json', 'last_pull.json']

    # The directory where the bundled data is located, typically _MEIPASS when frozen
    bundled_data_dir = getattr(sys, '_MEIPASS', base_dir)

    # Check and create directories
    for directory in required_directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # Handle files and directories when running from the compiled executable
    if hasattr(sys, '_MEIPASS'):
        for file_name in root_files:
            src_file_path = os.path.join(bundled_data_dir, file_name)
            dst_file_path = os.path.join(base_dir, file_name)
            if not os.path.exists(dst_file_path) and os.path.exists(src_file_path):
                shutil.copy(src_file_path, dst_file_path)

        for directory in required_directories:
            src_path = os.path.join(bundled_data_dir, directory)
            dst_path = os.path.join(base_dir, directory)
            if not os.path.exists(dst_path) and os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)

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
 
def focus_window(root):
    root.deiconify()  # Unhide the window if it was previously hidden
    root.focus_force()  # Force the focus on the window