# from event_handlers import on_data_type_selection, on_process_data_click, on_graph_click, update_checkboxes
import event_handlers
# from json_handler import check_all_economic_data_pulled_today
import json_handler
import graphing as graph
import tkinter as tk
from tkinter import messagebox
import gui_components as gui
import settings_management as settings
import event_handlers
# from utilities import log_message
import utilities
import sys
import os
import shutil
import app_state

# print(sys.path)


def main():

    base_dir = utilities.get_base_dir()

    # File path definition 
    Config_Settings_file_path = utilities.resource_path('settings.json', base_dir)

    # Setting the state for our app from our config file "settings.json"
    the_app_state = app_state.AppState(Config_Settings_file_path)

    global data_type_var, economic_data_var, currency_pair_var
    global fred_api_key_var, trader_made_api_key_var
    global economic_data_menu, currency_pair_menu
    global fetch_all_economic_button, fetch_all_currency_button

    # Create the folders/files
    utilities.create_missing_files_and_folders(base_dir)

    global_currency_list = [
        "AUDCAD",
        "AUDCHF",
        "AUDJPY",
        "AUDNZD",
        "AUDUSD",
        "CADCHF",
        "CADJPY",
        "CHFJPY",
        "EURAUD",
        "EURCAD",
        "EURCHF",
        "EURGBP",
        "EURJPY",
        "EURNZD",
        "EURUSD",
        "GBPCAD",
        "GBPCHF",
        "GBPJPY",
        "GBPNZD",
        "GBPUSD",
        "NZDCAD",
        "NZDCHF",
        "USDBRL",
        "USDCAD",
        "USDCHF",
        "USDCNH",
        "USDCZK",
        "USDDKK",
        "USDHKD",
        "USDHUF",
        "USDIDR",
        "USDINR",
        "USDJPY",
        "USDMXN",
        "USDNOK",
        "USDPLN",
        "USDRUB",
        "USDSEK",
        "USDSGD",
        "USDTHB",
        "USDTRY",
        "USDZAR",
    ]

    settings_json_file = utilities.resource_path('settings.json')

    app_settings = settings.load_settings(settings_json_file)
    utilities.log_message(app_settings, console_output=False)


    root = gui.create_root_window()

    data_type_var = tk.StringVar(value="Select Data Type")
    economic_data_var = tk.StringVar(value="Select Economic Data")
    currency_pair_var = tk.StringVar(value="Select Currency Pair")
    fred_api_key_var = tk.StringVar(value=app_settings.get("fred_api_key", ""))
    trader_made_api_key_var = tk.StringVar(
        value=app_settings.get("trader_made_api_key", "")
    )

    # Create API key input fields using the updated create_api_key_input function
    gui.create_api_key_input(root, "FRED API Key:", fred_api_key_var, 'fred', base_dir, row=0, column=0)
    gui.create_api_key_input(root, "Trader Made API Key:", trader_made_api_key_var, 'trader_made', base_dir, row=1, column=0)

    #  # Create input fields for API keys
    # fred_api_key_frame = gui.create_api_key_input(root, "FRED API Key:", fred_api_key_var, 'fred')
    # trader_made_api_key_frame = gui.create_api_key_input(root, "Trader Made API Key:", trader_made_api_key_var, 'trader_made')

    # Dropdown for selecting data type
    data_type_menu = gui.create_option_menu(
        root, data_type_var, ["Economic Data", "Currency Pair"], row=2, column=0
    )

    # Dropdowns for specific data choices
    economic_data_menu = gui.create_option_menu(
        root,
        economic_data_var,
        [
            "Federal Funds Interest Rate",
            "Non-Farm Employees",
            "Unemployment Rate",
            "GDP Reports",
            "Inflation Data (CPI)",
        ],
        row=2, column=1
    )
    currency_pair_menu = gui.create_option_menu(
        root, currency_pair_var, global_currency_list, row=2, column=1
    )

    # Initially hide the dropdowns for specific data choices
    economic_data_menu.grid_remove()
    currency_pair_menu.grid_remove()


    # Checkboxes for selecting data types to fetch
    fetch_economic_data_var = tk.BooleanVar(value=False)
    economic_data_checkbox = tk.Checkbutton(root, text="Fetch Economic Data", var=fetch_economic_data_var, 
                                        command=lambda: gui.update_fetch_all_button_text(fetch_economic_data_var, fetch_currency_data_var, fetch_all_button))
    economic_data_checkbox.grid(row=6, column=0, sticky='w')  

    fetch_currency_data_var = tk.BooleanVar(value=False)
    currency_data_checkbox = tk.Checkbutton(root, text="Fetch Currency Data", var=fetch_currency_data_var, 
                                        command=lambda: gui.update_fetch_all_button_text(fetch_economic_data_var, fetch_currency_data_var, fetch_all_button))
    currency_data_checkbox.grid(row=6, column=1, sticky='w')  

    # Fetch All Data button
    fetch_all_button = gui.create_button(
        root,
        "Fetch All Data",
        lambda: event_handlers.on_fetch_all_data(
            fetch_economic_data_var.get(), fetch_currency_data_var.get(), fred_api_key_var.get(), trader_made_api_key_var.get(), base_dir
        ),
        row=6, column=2  
    )


    # Trace the 'data_type_var' StringVar to call 'on_data_type_selection' whenever the option changes
    data_type_var.trace_add('write', lambda *args: event_handlers.on_data_type_selection(
        data_type_var,
        economic_data_menu,
        currency_pair_menu,
        fetch_all_button
    ))

    # BUTTON 1
    
    # Existing Fetch data button for specific requests
    fetch_button = gui.create_button(
        root,
        "Fetch Data",
        lambda: event_handlers.on_fetch_button_click(
            data_type_var,
            economic_data_var,
            currency_pair_var,
            fred_api_key_var,
            trader_made_api_key_var,
            base_dir
        ),
        row=2, column=3
    )
    # Path to your last_pull.json file
    last_pull_file = utilities.resource_path('last_pull.json')


    # Create Boolean variables for normalization and standardization
    normalization_var = tk.BooleanVar(value=False)
    standardization_var = tk.BooleanVar(value=False)

    # Add checkboxes for normalization and standardization
    normalization_checkbox = tk.Checkbutton(root, text="Normalization", var=normalization_var, command=event_handlers.update_checkboxes)
    standardization_checkbox = tk.Checkbutton(root, text="Standardization", var=standardization_var, command=event_handlers.update_checkboxes)

    normalization_checkbox = tk.Checkbutton(root, text="Normalization", var=normalization_var, 
                                            command=lambda: event_handlers.update_checkboxes(normalization_var, standardization_var, 'normalization'))
    standardization_checkbox = tk.Checkbutton(root, text="Standardization", var=standardization_var, 
                                            command=lambda: event_handlers.update_checkboxes(normalization_var, standardization_var, 'standardization'))


    # Place the checkboxes in the GUI
    normalization_checkbox.grid(row=10, column=0, sticky='w')  # Adjust row as needed
    standardization_checkbox.grid(row=10, column=1, sticky='w')  # Adjust row as needed

    # Create the "Processing" button
    processing_button = gui.create_button(
            root,
            "Process Data",
            lambda: event_handlers.on_process_data_click(normalization_var.get(), standardization_var.get(), base_dir),
            row=10, column=3  # Adjust row and column indices as needed
    )
    
    # Check if all economic data is up to date
    if json_handler.check_all_economic_data_pulled_today(last_pull_file, base_dir):
        processing_button.grid(row=10, column=3) 
        # print('the button should show.')
    else:
        messagebox.showinfo("Update Required", "Please update your economic data before processing.")

    # create date range button
    date_range_button = tk.Button(root, text="Select Date Range", command=lambda: graph.ask_date_range(root, base_dir, the_app_state))
    date_range_button.grid(row=18, column=0, columnspan=2) 
    
    # Create the "GRAPH" button and place it in row 8
    graph_button = tk.Button(root, text="GRAPH", command=lambda: event_handlers.on_graph_click(root, base_dir, the_app_state))
    graph_button.grid(row=20, column=2, columnspan=4)  # Place the button in row 8




    root.mainloop()


if __name__ == "__main__":
    main()
