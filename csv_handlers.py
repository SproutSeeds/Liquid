import pandas as pd
import numpy as np
import json
import os
import datetime
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.adfvalues import mackinnonp, mackinnoncrit
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import utilities

def serialize_series(obj):
    """ Helper function to serialize pandas Series into lists """
    if isinstance(obj, pd.Series):
        return obj.to_list()
    raise TypeError("Type not serializable")

def load_dataset(file_path):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    return data

def combine_economic_data_to_csv(base_dir):
    # Paths to the CSV files
    file_paths = {
        'Federal Funds Rate': utilities.resource_path('Historical_Data/Federal Funds Interest Rate_history.csv', base_dir),
        'GDP': utilities.resource_path('Historical_Data/GDP Reports_history.csv', base_dir),
        'CPI': utilities.resource_path('Historical_Data/Inflation Data (CPI)_history.csv', base_dir),
        'Non-Farm Employment': utilities.resource_path('Historical_Data/Non-Farm Employees_history.csv', base_dir),
        'Unemployment Rate': utilities.resource_path('Historical_Data/Unemployment Rate_history.csv', base_dir)
    }

    # Read the first file to start the merge process
    key = next(iter(file_paths))
    combined_df = pd.read_csv(file_paths[key], usecols=['date', 'value'])
    combined_df.rename(columns={'value': key}, inplace=True)

    # Iterate and merge the rest of the files
    for key, path in file_paths.items():
        if key != next(iter(file_paths)):  # Skip the first file already read
            df = pd.read_csv(path, usecols=['date', 'value'])
            df.rename(columns={'value': key}, inplace=True)
            combined_df = pd.merge(combined_df, df, on='date', how='outer')

    # Cleaning and sorting
    combined_df.dropna(subset=file_paths.keys(), how='all', inplace=True)  # Drop rows where all values are NaN
    combined_df.sort_values('date', inplace=True)
    
    # Convert the 'date' column to datetime format
    combined_df['date'] = pd.to_datetime(combined_df['date'])

    # Display the DataFrame
    print("Successfully combined csv files into a singular dataframe.")
    
    absolute_file_path = utilities.resource_path('Transform_Data_db/output/1_combined_data.csv', base_dir)
    combined_df.to_csv(absolute_file_path, index=False)
    
    
    return combined_df

def linear_interpolation(combined_data, base_dir):
    # Drop the 'date' column temporarily
    combined_data_without_date = combined_data.drop(columns=['date'])

    # Replace any non-numeric placeholders with NaN
    combined_data_without_date.replace('.', pd.NA, inplace=True)

    # Convert all columns to numeric type as they might be read as strings due to non-numeric placeholders
    combined_converted_data = combined_data_without_date.apply(pd.to_numeric)

    # Use linear interpolation to fill missing values
    combined_converted_interpolated_data = combined_converted_data.interpolate(method='linear', limit_direction='forward', axis=0)

    # use back fill to fill in the gaps backward
    combined_converted_interpolated_bfilled_data = combined_converted_interpolated_data.bfill()

    # Add the 'date' column back to the interpolated data
    combined_converted_interpolated_bfilled_data['date'] = combined_data['date']

    # Save the interpolated data to a new CSV file
    interpolated_bfilled_csv_path = 'Transform_Data_db/output/2_combined_LI_BF_data.csv'

    absolute_file_path = utilities.resource_path(interpolated_bfilled_csv_path, base_dir)

    combined_converted_interpolated_bfilled_data.to_csv(absolute_file_path, index=False)

    print("Successfully filled in missing values with linear interpolation in conjunction with backfilling.")

    return combined_converted_interpolated_bfilled_data

def test_for_stationary_data(data, is_normalized, is_standardized, base_dir, window=12):
    adf_results = pd.DataFrame(columns=['Variable', 'Test Statistic', 'p-value', '#Lags Used', 
                                        'Number of Observations Used', 'Critical Value (1%)', 
                                        'Critical Value (5%)', 'Critical Value (10%)', 'Stationary'])
    adf_results_list = []
    stationary_data_dict = {} 
    for column in data.columns:
        if column == 'date':
            continue  # Skip the 'date' column
        
        result_before = adfuller(data[column])  # Perform ADF test before transformations
        stationary_before = result_before[1] < 0.05  # Assuming 5% significance level
        
        if not stationary_before:  # if not stationary_before or column == 'Unemployment Rate':
            # print(f"{column} is not stationary before transformations.")
            # Make the data stationary and update the DataFrame
            data, order_of_integration = make_data_stationary(data, column, window)
            
            # print(f"Column Name: {column}")

            stationary_before = True  # Assuming that the transformation makes it stationary
            
            # Store the stationary data and order of integration as a tuple in the dictionary 
            stationary_data_dict[column] = {'data': data[column], 'order_of_integration': order_of_integration}
        else:
            stationary_data_dict[column] = {'data': data[column], 'order_of_integration': 0}



        # Create a DataFrame to hold the result for this variable
        result_df = pd.DataFrame([{
            'Variable': column,
            'Test Statistic': result_before[0],
            'p-value': result_before[1],
            '#Lags Used': result_before[2],
            'Number of Observations Used': result_before[3],
            'Critical Value (1%)': result_before[4]['1%'],
            'Critical Value (5%)': result_before[4]['5%'],
            'Critical Value (10%)': result_before[4]['10%'],
            'Stationary': stationary_before
        }])
        adf_results_list.append(result_df)

    # This will create a DF to CSV file from our original test data
    adf_results = pd.concat(adf_results_list, ignore_index=True, join='outer', sort=False)

    absolute_file_path = utilities.resource_path('Transform_Data_db/output/3_adf_test_results.csv', base_dir)

    adf_results.to_csv(absolute_file_path, index=False)  # Save ADF test results
   
    # Create a DataFrame with just the 'date' column
    date_column_df = data[['date']]

    # Convert the values of the stationary_data_dict into a list of DataFrames
    dataframes_list = [date_column_df] + [value['data'] for value in stationary_data_dict.values()]

    # Create a single DataFrame by concatenating the list of DataFrames along the columns
    stationary_data_df = pd.concat(dataframes_list, axis=1)

    # Removing the rows with 0 and NaN values in the front and back of dataframe
    stationary_data_df = stationary_data_df[(stationary_data_df != 0).all(axis=1) & (~stationary_data_df.isna()).all(axis=1)]

    # Select only numeric columns for scaling
    numeric_columns = stationary_data_df.select_dtypes(include=['float64', 'int64'])


    # Apply normalization or standardization
    if is_normalized:
        normalized_df = normalize_data(numeric_columns)
        stationary_data_df.update(normalized_df)  # Update the numeric columns with normalized data
    elif is_standardized:
        standardized_df = standardize_data(numeric_columns)
        stationary_data_df.update(standardized_df)  # Update the numeric columns with standardized data

    absolute_file_path = utilities.resource_path('Transform_Data_db/output/4_processed_stationary_data.csv', base_dir)

    standardized_df.set_index('date', inplace=True)
    # Save the stationary data dictionary to a CSV file
    stationary_data_df.to_csv(absolute_file_path, index=True)

    # Update the dictionary with the final, cleaned data
    for column in stationary_data_dict:
        stationary_data_dict[column]['data'] = stationary_data_df[column]

    print("Successfully created a dict with our stationary data, detailing the order of integration associated with each column of our data.")



    return stationary_data_dict, stationary_data_df 

def make_data_stationary(data, column, period=12, max_differencing=5):
    series = data[column].replace(0, np.nan)  # Replace 0 with NaN to avoid issues with log transformation
    series.dropna(inplace=True)  # Drop NaN values

    p_value = 1.0  # Initialize p-value
    num_differences = 0

    # Apply differencing up to the maximum allowed
    for i in range(max_differencing + 1):
        # Log transform
        transformed = np.log(series)

        # Differencing
        differenced = transformed.diff().dropna()

        # Perform ADF test on differenced series
        result = adfuller(differenced)
        p_value = result[1]

        # print(f"p_value is equal to {p_value}")

        num_differences += 1

        # If the series is now stationary or we've reached the maximum allowed differencing, stop
        if p_value < 0.05 or i == max_differencing:
            break

        # Update the series for the next differencing iteration
        series = differenced
        


    # Decomposition
    decomposition = seasonal_decompose(differenced, model='additive', period=period)
    deseasonalized = differenced - decomposition.seasonal
    detrended = deseasonalized - decomposition.trend

    # Handle NaN and infinite values by replacing them with zeros
    detrended = detrended.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Drop NaN values after transformations
    stationary = detrended.dropna()

    # Update the original DataFrame with the stationary series
    data[column] = stationary

    return data, num_differences

def is_data_up_to_date(directory_path):
    """
    Checks if the data in the specified directory exists and is up to date.
    Returns True if data is up to date, False otherwise.
    """
    # List of files you expect to find
    expected_files = ['Federal Funds Interest Rate_history.csv', 'GDP Reports_history.csv', 'Inflation Data (CPI)_history.csv', 'Non-Farm Employees_history.csv', 'Unemployment Rate_history.csv']

    # Check if all expected files exist and are up to date
    for file in expected_files:
        file_path = os.path.join(directory_path, file)

        if not os.path.exists(file_path):
            return False

        # Check if the file is up to date (e.g., modified today)
        last_modified = datetime.date.fromtimestamp(os.path.getmtime(file_path))
        if last_modified < datetime.date.today():
            return False

    return True

def standardize_data(df):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
    return scaled_df

def normalize_data(df):
    min_max_scaler = MinMaxScaler()
    normalized_data = min_max_scaler.fit_transform(df)
    normalized_df = pd.DataFrame(normalized_data, columns=df.columns, index=df.index)
    return normalized_df

def combine_economic_data_make_stationary_clean(is_normalized, is_standardized, base_dir):

    ############## MAIN #####################

    # 1. Combine all of our downloaded economic data to a singular csv.
    #    this happens within the combine_economic_data_to_csv()
    combined_data = combine_economic_data_to_csv(base_dir)

    # 2. Handle missing values, we chose to use linear interpolation first,
    #    and then we back filled the rest of the data points.
    combined_linearInterpolated_backFilled = linear_interpolation(combined_data, base_dir)

    # 3. We then perform the ADF (Augmented Dickey-Fuller) test to determine stationarity.
    #    Saving csv files of the raw results from our ADF test as well as the now transformed 
    #    and statitoned data in this directory. Returns a dictionary that you can find all data in. 
    combined_LI_BF_stationary_data_dictionary, stationary_data_df = test_for_stationary_data(combined_linearInterpolated_backFilled,is_normalized, is_standardized, base_dir)



    # saving a copy of data into a JSON file for visualizing the data we have.
    json_formatted_str = json.dumps(combined_LI_BF_stationary_data_dictionary, indent=4, default=serialize_series)

    # Specify the file name (you can change this to your preferred file path)
    filename = 'Transform_Data_db/output/Dict_json_visual_stationary_data.json'

    absolute_file_path = utilities.resource_path(filename, base_dir)

    # Writing to a file
    with open(absolute_file_path, 'w') as file:
        file.write(json_formatted_str)

    print(f"JSON file saved as {absolute_file_path}, for visualization of the dictionary after the data is combined, linearly interpolated, back filled, made stationary, and removal of non vital rows with zeros and Nans, specifically, the first and last 7 rows of this dataset.")


    #4 return  
    return combined_LI_BF_stationary_data_dictionary

def train_model(app_state, base_dir):
    start_date, end_date = app_state.get_training_dates()
    processed_dataframe = app_state.get_processed_dataframe()

    # Convert the date column to datetime type if it's not already
    processed_dataframe['date'] = pd.to_datetime(processed_dataframe['date'])

    # isolate the processed data based on the user specified start and end date
    training_dataframe = processed_dataframe[(processed_dataframe['date'] >= start_date) & (processed_dataframe['date'] <= end_date)]

    absolute_file_path = utilities.resource_path('Training_Data/1_training_data.csv', base_dir)
   
    training_dataframe.set_index('date', inplace=True)
    training_dataframe.to_csv(absolute_file_path, index=True)

    # Set the training dataframe to state
    app_state.set_training_dataframe(training_dataframe)

    # gets the dataframe reference from state
    training_dataframe = app_state.get_training_dataframe()

    # explicitly stating the Month Start as the index frequency of the data
    training_dataframe.index.freq = 'MS'


    # declaring the model, pulling in VAR from statsmodels
    model = VAR(training_dataframe)

    # Select the optimal lag order
    maxlags = min(10, len(training_dataframe) // len(training_dataframe.columns) - 1)
    results = model.select_order(maxlags=maxlags)

    # print(results.summary())

    # Fit the VAR model using the optimal lag order
    optimal_lag = results.aic
    fitted_model = model.fit(optimal_lag)



    # Display model summary
    print(fitted_model.summary())



    # print(app_state.get_training_dataframe())


    # print(f"The start date: {start_date} The end date: {end_date}")
    # print(app_state.get_processed_dataframe())


"""
POTENTIAL CODE


# List of file names for the currency pair data
currency_files = ['AUDUSD_historical_data.csv', 'EURUSD_historical_data.csv', ...]  # continue for all files

# Initialize an empty DataFrame to hold all the combined data
combined_data = pd.DataFrame()

# Loop through each file and merge it into the combined DataFrame
for file in currency_files:
    # Read the currency data file
    currency_data = pd.read_csv(file)

    # Convert the 'Date' column to datetime
    currency_data['Date'] = pd.to_datetime(currency_data['Date'])

    # Set the 'Date' column as the index
    currency_data.set_index('Date', inplace=True)

    # Extract the currency pair code from the file name, assuming the format is 'CURRENCYCODE_historical_data.csv'
    currency_code = file.split('_')[0]

    # Rename the relevant column (e.g., 'Close') to the currency code for clarity
    # Assuming you want to use the closing price for resampling; adjust if using a different column
    currency_data.rename(columns={'Close': currency_code}, inplace=True)

    # Select only the column with the renamed currency data (if there are multiple columns)
    currency_data = currency_data[[currency_code]]

    # If this is the first file, assign it to combined_data; otherwise, join it with the existing combined_data
    if combined_data.empty:
        combined_data = currency_data
    else:
        # Use an outer join to ensure all dates are included, even if some data is missing for some dates
        combined_data = combined_data.join(currency_data, how='outer')

# Now, combined_data contains all currency data with each currency as a column

# Resample to get the first entry of each month (assumes the 'Open' price is the one you want)
monthly_data = combined_data.resample('MS').first()

# Save the resampled monthly data to a new CSV file
monthly_data.to_csv('monthly_currency_data.csv', index=True)
"""
