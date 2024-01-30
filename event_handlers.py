import tkinter as tk
import api_interaction
# from utilities import log_message
import utilities
import graphing as graph
from tkinter import messagebox
import time
import csv_handlers


def on_data_type_selection(var, economic_data_menu, currency_pair_menu, fetch_all_button):
    selected_data_type = var.get()
    if selected_data_type == "Economic Data":
        economic_data_menu.grid()  # Show the economic data menu
        currency_pair_menu.grid_remove()  # Hide the currency pair menu
        fetch_all_button.grid()  # Show the fetch all button
    elif selected_data_type == "Currency Pair":
        currency_pair_menu.grid()  # Show the currency pair menu
        economic_data_menu.grid_remove()  # Hide the economic data menu
        fetch_all_button.grid()  # Show the fetch all button
    else:
        economic_data_menu.grid_remove()  # Hide the economic data menu
        currency_pair_menu.grid_remove()  # Hide the currency pair menu
        fetch_all_button.grid_remove()  # Hide the fetch all button

    

def on_fetch_button_click(data_type_var, economic_data_var, currency_pair_var, fred_api_key_var, trader_made_api_key_var, base_dir):
    selected_data_type = data_type_var.get()
    selected_economic_data = economic_data_var.get()
    selected_currency_pair = currency_pair_var.get()
    
    utilities.log_message(f"{selected_data_type}", console_output=True)
 
    if selected_data_type == "Economic Data":
        utilities.log_message(f"{selected_economic_data}", console_output=True)
        api_interaction.fetch_economic_data(fred_api_key_var.get(), selected_economic_data,base_dir)
    elif selected_data_type == "Currency Pair":
        utilities.log_message(f"{selected_currency_pair}", console_output=True)
        api_interaction.fetch_historical_currency_data(trader_made_api_key_var.get(), selected_currency_pair, base_dir)
        
def on_fetch_all_data(fetch_economic, fetch_currency, fred_api_key_var, trader_made_api_key_var,base_dir):
    # If both checkboxes are unchecked or both are checked, set both variables to True
    if (not fetch_economic and not fetch_currency) or (fetch_economic and fetch_currency):
        fetch_economic = True
        fetch_currency = True

    # Log that the process has started
    utilities.log_message("Fetching data...", console_output=True)

    # Confirm with the user that this might take a long time and make many API calls
    response = messagebox.askyesno("Fetch Data", "This process may take some time. Do you want to continue?")
    if not response:
        utilities.log_message("Fetching data canceled.", console_output=True)
        return

    # Fetch economic data if selected
    if fetch_economic:
        for economic_data in ["Federal Funds Interest Rate", "Non-Farm Employees", "Unemployment Rate", "GDP Reports", "Inflation Data (CPI)"]:
            utilities.log_message(f"Now fetching {economic_data} historical...", console_output=True)
            api_interaction.fetch_economic_data(fred_api_key_var, economic_data,base_dir)
            time.sleep(1)  # Implement a delay if necessary to avoid hitting API rate limits
    
    # Fetch currency data if selected
    if fetch_currency:
        for currency_pair in ["AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD", "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD", "NZDCAD", "NZDCHF", "USDBRL", "USDCAD", "USDCHF", "USDCNH", "USDCZK", "USDDKK", "USDHKD", "USDHUF", "USDIDR", "USDINR", "USDJPY", "USDMXN", "USDNOK", "USDPLN", "USDRUB", "USDSEK", "USDSGD", "USDTHB", "USDTRY", "USDZAR"]:
            utilities.log_message(f"Now fetching {currency_pair} historical data...", console_output=True)
            api_interaction.fetch_historical_currency_data(trader_made_api_key_var, currency_pair, base_dir)
            time.sleep(1)  # Implement a delay if necessary to avoid hitting API rate limits

    utilities.log_message("Data fetching complete.", console_output=True)


def on_process_data_click(is_normalized, is_standardized, base_dir):
    try:
        # Saves processed data
        processed_data = csv_handlers.combine_economic_data_make_stationary_clean(is_normalized, is_standardized, base_dir)  # Replace with your data loading function

        # Handle successful processing - show a message or update the UI
        messagebox.showinfo("Success", "Data has been successfully processed.")

    except Exception as e:
        # Handle errors - show an error message
        messagebox.showerror("Error", f"An error occurred: {e}")


def on_graph_click(root, base_dir, app_state):
        graph.generate_graph(root, base_dir, app_state)

def update_checkboxes(normalization_var, standardization_var, clicked):
    if clicked == 'normalization':
        if normalization_var.get():
            standardization_var.set(False)
        else:
            normalization_var.set(True)
    elif clicked == 'standardization':
        if standardization_var.get():
            normalization_var.set(False)
        else:
            standardization_var.set(True)







        # POTENTIAL CODE
