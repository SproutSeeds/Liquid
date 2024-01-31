import tkinter as tk
from tkinter import ttk
# from json_handler import save_api_keys
import json_handler

def create_root_window():
    root = tk.Tk()
    root.withdraw() 
    root.title("Data Fetching Application")
    root.geometry("1200x900")
    return root

def create_label(parent, text, row, column, sticky='w', padx=10, pady=5):
    label = ttk.Label(parent, text=text)
    label.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
    return label

def create_entry(parent, textvariable, row, column, padx=10, pady=5):
    entry = ttk.Entry(parent, textvariable=textvariable)
    entry.grid(row=row, column=column, padx=padx, pady=pady)
    return entry

def create_button(parent, text, command, row, column, padx=10, pady=5, sticky='w'):
    button = ttk.Button(parent, text=text, command=command)
    button.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return button

def create_option_menu(parent, textvariable, options, row, column, padx=10, pady=5, sticky='w'):
    menu = ttk.OptionMenu(parent, textvariable, options[0], *options)
    menu.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return menu

def create_api_key_input(root, label_text, api_key_text_var, api_key_type, base_dir, app_state, row, column):
    frame = ttk.Frame(root)
    
    # Create label and entry inside the frame
    label = create_label(frame, label_text, row=0, column=0)
    entry = create_entry(frame, api_key_text_var, row=0, column=1)
    
    # Function to be called when Enter is pressed
    def on_enter_press(event):
        if api_key_type == 'fred':
            app_state.set_fred_api_key(api_key_text_var.get())
        elif api_key_type == 'trader_made':
            app_state.set_trader_made_api_key(api_key_text_var.get())

        # json_handler.save_api_keys(api_key_text_var.get(), api_key_type, base_dir)
        frame.destroy()  # This will remove the frame and all widgets inside it

    entry.bind('<Return>', on_enter_press)
    
    # Place the frame using grid
    frame.grid(row=row, column=column, sticky='nw')
    return frame, entry

def update_fetch_all_button_text(economic_var, currency_var, fetch_all_button):
    economic_checked = economic_var.get()
    currency_checked = currency_var.get()

    if economic_checked and currency_checked:
        fetch_all_button.config(text="Fetch All Economic and Currency Data")
    elif economic_checked:
        fetch_all_button.config(text="Fetch All Economic Data")
    elif currency_checked:
        fetch_all_button.config(text="Fetch All Currency Data")
    else:
        fetch_all_button.config(text="Fetch All Data")

def update_date_range_label(app_state, label, type):

    if type == 'processed':
        start_date, end_date = app_state.get_graphing_dates()  # Adjust the method if needed
    elif type == 'training':
        start_date, end_date = app_state.get_training_dates()  # Adjust the method if needed

    label.config(text=f"{start_date} to {end_date}")