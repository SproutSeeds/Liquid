import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkinter import simpledialog
from matplotlib.figure import Figure
import utilities

# Function to generate and display the graph in a separate window
def generate_graph(root, base_dir, app_state):

    start_date, end_date = app_state.get_graphing_dates()

    # Specify the path to your CSV file
    absolute_file_path = utilities.resource_path("Transform_Data_db/output/4_processed_stationary_data.csv", base_dir)

    # Read data from the CSV file into a DataFrame
    df = pd.read_csv(absolute_file_path)

    # Convert the 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'])

    # Filter the DataFrame based on the date range input
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df.loc[mask]

    # Create a Matplotlib figure (twice as big)
    fig = Figure(figsize=(16, 8))
    ax = fig.add_subplot(111)

    ax.plot(df_filtered['date'], df_filtered['Federal Funds Rate'], label='Federal Funds Rate')
    ax.plot(df_filtered['date'], df_filtered['GDP'], label='GDP')
    ax.plot(df_filtered['date'], df_filtered['CPI'], label='CPI')
    ax.plot(df_filtered['date'], df_filtered['Non-Farm Employment'], label='Non-Farm Employment')
    ax.plot(df_filtered['date'], df_filtered['Unemployment Rate'], label='Unemployment Rate')

    # Customize the plot
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.set_title('Economic Data Over Time')
    ax.legend()
    ax.grid(True)

    # Create a new Toplevel window for the graph
    graph_window = tk.Toplevel(root)
    graph_window.title("Graph Window")

    # Embed the Matplotlib figure in a Tkinter canvas within the graph window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()  # Place the graph in the new window
    canvas.draw()

# Function to ask for date range
def ask_date_range(root, base_dir, app_state):
    default_start, default_end = app_state.get_graphing_dates()
    start_date = simpledialog.askstring("Input", "Enter start date (YYYY-MM-DD):", initialvalue=default_start, parent=root)
    end_date = simpledialog.askstring("Input", "Enter end date (YYYY-MM-DD):", initialvalue=default_end, parent=root)
    
    app_state.set_graphing_dates(start_date, end_date)

    # if start_date and end_date:
    #     generate_graph(root, start_date, end_date, base_dir)