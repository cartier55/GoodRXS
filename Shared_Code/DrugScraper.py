import re
from turtle import st
from httpx import get
import pandas as pd
import os
import sys
from time import sleep
import time
from helpers import clean_string, clear, join_info_files, retry_on_exception, try_convert_to_numeric
from data_fetchers import coupon_query, get_drug_combinations, get_drug_info, get_prices
from pprint import pprint as pp
from logger import Logger
import ast
from tqdm import tqdm
import asyncio
import csv
from collections import defaultdict

from test_find import failed_req
from test_fix import fix

from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError, RequestException, ConnectTimeout, ReadTimeout

from async_data_fetchers import get_drug_combinations_httpx, get_drug_info_httpx, coupon_query_httpx, get_prices_httpx


class DrugScraper:

    def __init__(self):
        # self.drug = drug
        # self.logger = Logger()
        self.drug_names = []
        self.drug_ids = None
        self.cur_display_drug = None
        self.cur_drug = None
        self.letter = None
        self.drug_info = [{}]
        self.drug_combos = []
        self.drugs_len = 6513
        self.data_types = ['info', 'combos']

        # ! - Prod File Paths
        self.combos_file_path = 'results/drug_combos/all_drug_combos_test.csv'
        self.info_file_path = 'results/drug_info/all_drug_infos_complete_test.csv'
        self.drug_names_file_path = 'all_drugs/all_drug_names.csv'
        
        # self.combos_file_path = 'results/drug_combos/all_drug_combos_test_1.csv'
        # self.info_file_path = 'results/drug_info/all_drug_infos_test_1.csv'
        # self.drug_names_file_path = 'all_drugs/all_drug_names.csv'

        self.batch_size = 100
        # self.filename_override = {
        #     'info': 'all_drug_infos_test_1.csv',
        #     'combos': 'all_drug_combos_test_1.csv'
        # }
        ...

# * - Documented
    def _check_process(self, step):
        """
        This method checks the existence and validity of CSV files for drug info or drug combos
        based on the input step. If the checks pass, the method displays an appropriate message
        and returns True. Otherwise, it displays an error message and returns False.

        Parameters:
        step (str): The processing stage. Can be 'info' or 'combos'.

        Returns:
        bool: True if checks pass and processing can move to the next stage, False otherwise.
        """
       
        if self.data_type == 'info':
            ...

        if step == 'info':
            file_path = self.info_file_path
            success_message = '''
            [+] Drug Info ✅
                
            Continuing to Drug Combos...
            '''
            failure_message = '''
            [+] Drug Info ❌
                
            Continuing to Drug Info...
            '''
        elif step == 'combos':
            file_path = self.combos_file_path
            success_message = '''
            [+] Drug Info ✅
            [+] Drug Combos ✅
                
            Continuing to Drug Prices...
            '''
            failure_message = '''
            [+] Drug Info ✅
            [-] Drug Combos ❌
                
            Continuing to Drug Combos...
            '''

        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
            if not df.empty and self.logger.check_scraping_complete():
                print(success_message)
                sleep(3)
                clear(False)
                return True

        print(failure_message)
        sleep(3)
        clear(False)
        return False
        ...
    ...

# * - Documented
    def _construct_filename(self) -> str:
        """
        This method is used to construct a filename based on the data_type parameter. 
        It has an argument data_type which should be either 'info' or 'combos'.
        It returns a filename which is a string.

        Parameters:
        data_type (str): The type of data. It should be either 'info' or 'combos'.

        Returns:
        str: The constructed filename as a string.

        Raises:
        ValueError: If the data_type is not either 'info' or 'combos', it raises a ValueError.

        Example:
        _construct_filename('info') returns 'all_drug_infos.csv'
        _construct_filename('combos') returns 'all_drug_combos.csv'

        Note: 
        The filename is constructed by appending the data_type to 'all_drug_' and '.csv' 
        and for 'info' data_type 's' is also added to the end of the filename.
        """
        filename_override = getattr(self, "filename_override", None)

        if self.data_type in ['info', 'combos']:
            if filename_override:
                filename = filename_override[self.data_type]
            else:
                filename = f'all_drug_{self.data_type}s.csv' if self.data_type == 'info' else f'all_drug_{self.data_type}.csv'
            return filename
        else:
            raise ValueError("Data type must be either 'info' or 'combos'.")
        ...
    ...

    def _check_path(self, path):
        if not os.path.isfile(path):
            sys.exit(f"File {path} does not exist")
        ...
    ...

# * - Documented
    def _logged_restart(self, prev_params):
        """
        This method restarts the logging process from a specific index to avoid duplicate entries in the data source. 
        It determines the restarting index based on the type of data being processed ('info' or 'combos') and the name of the drug from the previous request parameters.

        Args:
            prev_params (dict): A dictionary of previous request parameters. It should include a key 'drug_name' with the name of the previously processed drug.

        Returns:
            restart_index (int): The index from which to restart the logging process to avoid duplicates.

        """
        if self.data_type == 'info':
            # Get the drug name from the previous request parameters
            drug_name = prev_params['drug_name']
            # Find the index of the drug in the dataframe 'drug_names' and increment it by 1 to get the restart index
            restart_index = self.drug_names.loc[self.drug_names['drug_name']
                                                == drug_name].index[0] + 1
            return restart_index
        elif self.data_type == 'combos':
            # Set 'drug_name' as the index of the dataframe 'drug_ids'
            self.drug_ids.set_index('drug_name', inplace=True)
            # Get the drug name from the previous request parameters
            drug_name = prev_params['drug_name']
            # Find the location of the drug in the dataframe 'drug_ids' and increment it by 1 to get the restart index
            restart_index = self.drug_ids.index.get_loc(drug_name) + 1
            # Calculate the index for the restart_list function
            index = restart_index - 1
            # Prime entry file (combos.csv) for restart by removing combos from the most recent processed drug
            self.restart_list(index)
            # Reset the index of the dataframe 'drug_ids'
            self.drug_ids.reset_index(inplace=True)
            return restart_index
        ...
    ...

# * - Documented
    def _manual_restart(self, df):
        """
        This method manually restarts the process from a specific index based on the last entry in the given DataFrame.
        It gets the 'drug_name' from the last row of the DataFrame and finds its index in either 'drug_names' DataFrame or 'drug_ids' DataFrame depending on the 'data_type'.
        The method terminates the program execution if it encounters duplicate drug names or if the 'drug_name' is not found in the corresponding DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame from which the last 'drug_name' will be extracted to determine the restart index.

        Returns:
            index (int): The index to restart from, which is the location of the last processed 'drug_name' incremented by one.

        Raises:
            SystemExit: If the 'drug_name' is a known duplicate or if the 'drug_name' cannot be found in the list of drug names.
        """
        # Extract the last row from the DataFrame
        last_row = df.iloc[-1]

        # Get the value from the 'drug_name' column in the last row
        drug_name = last_row['drug_name']

        # Temporary fix for known duplicate drug names
        # The program will exit if it encounters these specific drug names
        if drug_name == 'Bendamustine' or drug_name == 'Diltiazem ER (Cardizem LA)':
            return sys.exit("[-] Duplicate drug name")

        try:
            # Try to get the index of the drug_name in the list of drugs
            if self.data_type == 'info':
                # Current approach uses DataFrame for locating the drug name
                # Future changes could consider using a dict for better indexing
                index = self.drug_names.loc[self.drug_names['drug_name']
                                            == drug_name].index[0] + 1
            elif self.data_type == 'combos':
                # For 'combos' data type, set 'drug_name' as the index of 'drug_ids' DataFrame
                self.drug_ids.set_index('drug_name', inplace=True)
                index = self.drug_ids.index.get_loc(drug_name) + 1
                # Call the restart_list function with the calculated index
                self.restart_list(index)
                # Reset the index of the 'drug_ids' DataFrame
                self.drug_ids.reset_index(inplace=True)
        except ValueError:
            # Exit the program if the drug_name isn't found in the list
            sys.exit(f"[-] {drug_name} not found in drug_names list.")

        # If the drug name is found, return the next index as the restart point
        return index
        ...
    ...

# * - Documented
    def get_restart_index(self):
        """
        Method to get the restart index from a saved CSV file.

        This method constructs a file path using a helper function and a pre-defined attribute (`data_type`) of the object. 
        It then checks if a CSV file exists at that file path. If the file does exist, it reads the file into a pandas 
        DataFrame and checks if this DataFrame is not empty. If the DataFrame is not empty, it gets the last request parameters 
        from a logger object, if any, and then decides the restart point accordingly, either through the `_logged_restart()` 
        method or the `_manual_restart()` method. 

        If the DataFrame is empty or if the file does not exist, it returns 0. 

        Returns:
            int: The index of the next drug name to process. It could be obtained through `_logged_restart()` or `_manual_restart()`.
                Returns 0 if the DataFrame is empty or the file does not exist.

        Raises:
            SystemExit: If the `_logged_restart()` or `_manual_restart()` method can't find the last processed drug name 
            in the list of drug names. 
        """

        # Construct the filename using a helper function.
        filename = self._construct_filename()

        # Join the folder path and the filename to create a complete file path.
        file_path = os.path.join(f'results/drug_{self.data_type}', filename)

        # Check if the CSV file exists at the given file path.
        if os.path.isfile(file_path):
            # Read the file into a pandas DataFrame.
            df = pd.read_csv(file_path)

            # Check if the DataFrame is not empty.
            if not df.empty:
                # Get the last request parameters from the logger object, if any.
                prev_params = self.logger.get_last_request_params()
                if prev_params:
                    # Determine the restart point based on the last logged parameters.
                    pp(prev_params['drug_name'])
                    return self._logged_restart(prev_params)
                # Determine the restart point manually if there are no last logged parameters.
                else:
                    index = self._manual_restart(df)
                    pp(df.iloc[index - 1])
                return index

            else:
                # If the DataFrame is empty, print a message and return 0.
                print('df empty')
                return 0

        # If the file doesn't exist, print a message and return 0.
        print('no file')
        return 0

# * - Documented
# ! - May not be needed extra thought required
    def restart_list(self, index):
        """
        This function is used to reset a specific drug combination list based on an index. 

        Parameters:
        index (int): The index of the drug that is in the drug_ids DataFrame. 

        The function does the following:
        1. Fetches the drug name and id from the drug_ids DataFrame based on the provided index.
        2. Generates a list of drug combinations involving the identified drug using the get_drug_combinations function.
        3. Iterates over the list of drug combinations and removes any matching entries from the drug_combos DataFrame. 

        A matching entry in drug_combos DataFrame is identified by comparing each row of the DataFrame 
        with the combination series (pandas Series object derived from the combo dictionary) and checking 
        if all elements are equal (done using the 'eq' function and 'all' function).

        After this function is run, the drug_combos DataFrame will not contain any combinations involving 
        the drug corresponding to the provided index.
        """
        # Fetch the drug name and id from the drug_ids DataFrame
        drug_name = self.drug_ids.iloc[index]['drug_name']
        drug_id = self.drug_ids.iloc[index]['drug_id']

        # Generate the list of drug combinations involving the identified drug
        combos = get_drug_combinations(drug_id, drug_name)

        # Iterate over the list of drug combinations
        for combo in combos:
            # Convert the current combo dictionary into a pandas Series
            combo_as_series = pd.Series(combo)

            # Identify rows in the drug_combos DataFrame that match the current combo series
            # and exclude them from the DataFrame
            self.drug_combos = self.drug_combos[~self.drug_combos.eq(
                combo_as_series).all(axis=1)]
        ...
    ...

# * - Documented
    def _set_data_type(self, data_type):
        """
        This is a private method that sets the 'data_type' attribute of the object. 
        The 'data_type' attribute defines the type of data that is going to be scraped by the object.

        The function also calls the 'get_inital_data' method after setting the 'data_type' attribute.
        The 'get_inital_data' method probably uses the 'data_type' attribute in its operations.

        :param data_type: A string that should either be 'info' or 'combos'. It determines which data to scrape.

        :raises ValueError: If the provided data_type is not either 'info' or 'combos'.
        """
        if data_type not in self.data_types:
            raise ValueError("Data type must be either 'info' or 'combos'.")
        else:
            self.data_type = data_type
            self.get_inital_data()
        ...
    ...

# * - Documented
    def get_inital_data(self):
        """
        This method is used to get the initial data based on the data type needed for further scraping of drug info
        or combos data. It sets the data_type attribute of the object and calls the specific get_data method.
        """
        if self.data_type == 'info':
            self._get_drug_names()
        elif self.data_type == 'combos':
            self._get_drug_ids()
        ...
    ...

    # For getting drug combinations
# * - Documented
    def _get_drug_ids(self):
        """
        Reads the specified CSV file and returns a DataFrame.
        Keeps only the 'drug_name' and 'drug_id' columns.

        Parameters:
        None

        Returns:
        pd.DataFrame: A DataFrame containing the 'drug_name' and 'drug_id' columns from the specified CSV file.
        """

        # Specify the path to the CSV file
        # file_path = self.info_file_path

        # ! - Temp for testing
        data = f'drug_info'
        # filename = self.filename_override[self.data_type]
        filename = 'all_drug_infos_test_1.csv'
        file_path = os.path.join(f'results/{data}', filename)
        # ! - Temp for testing

        self._check_path(file_path)

        # Load the CSV file into a DataFrame, keeping only the 'drug_name' and 'drug_id' columns
        self.drug_ids = pd.read_csv(
            file_path, usecols=['drug_name', 'drug_id'])
        # self.drug_ids.set_index('drug_name', inplace=True)

        # Return the DataFrame
        return self.drug_ids
        ...
    ...
    # For getting drug info
# * - Documented

    def _get_drug_names(self):
        """
        This function reads a csv file of drug names based on a provided letter. It assumes the csv file is named in the 
        format 'drugs_{letter}.csv' and is located in the 'all_drugs' folder. The drug names should be in the first column 
        of the csv file.

        Parameters:
        letter (str): A string representing the letter that corresponds to the drug names file. For example, if the letter
                      'a' is passed, the function will try to read the file 'drugs_a.csv'.

        Returns:
        None: If the file does not exist. It also prints a message specifying the file which does not exist.
        If the file exists, it updates the instance variable 'drug_names' with a list of drug names from the csv file. 
        """

        file_path = self.drug_names_file_path
        # Check if the file exists
        self._check_path(file_path)

        # Use pandas to read the csv file
        self.drug_names = pd.read_csv(file_path)

        # Assuming the drug names are in the first column
        # Use .tolist() to convert the column into a list
        # self.drug_names = df.iloc[:, 0].tolist()
    ...


    def scrape(self, data_type='info'):
        self._set_data_type(data_type)
        self.logger = Logger(self.data_type)
        asyncio.run(self.get_data_async())

        # for type in self.data_types:
        #     if type == 'combos':
        #         self._set_data_type(type)
        #         self.logger = Logger(self.data_type)
                # self._check_process()
        #         asyncio.run(self.get_data_async())
        ...
    ...


    # * - Documented
    def _get_df_slices(self, df):
        """
        This method splits a DataFrame into smaller slices of a given batch size. The start index for splitting can be obtained 
        from a previous stopped position (restart_index), allowing for continuation of processing from a certain point.

        Parameters:
        df (pandas.DataFrame): The DataFrame to be split into slices.

        Returns:
        list: A list containing DataFrame slices.
        """
        # Get the index from where to restart processing
        restart_index = self.get_restart_index()
        # Split the DataFrame 'df' into smaller slices with the size of 'self.batch_size' from 'restart_index'
        return [df[i:i+self.batch_size] for i in range(restart_index, len(df), self.batch_size)]
        ...
    ...

    # * - Documented
    def process_failed_requests(self):
        """
        This function processes a list of failed requests and groups them by 'last_success_row'. If 'data_type' is 
        'combos', it also includes 'drug_id' along with 'drug_name'. 
        
        The function takes no parameters as inputs, instead, it works on the 'failed_requests' and 'data_type' 
        attributes of the instance of the class this method belongs to.

        The output of this function is a list of dictionaries, where each dictionary has 'last_success_row' as a key 
        and another dictionary containing 'drug_info' as the value.

        Returns:
        list: A list of dictionaries. Each dictionary has a key 'last_success_row' and a key 'requests' with value as
        a list of tuples. Each tuple contains 'drug_name' and, if 'data_type' is 'combos', 'drug_id'.
        """
        
        combined_requests = []
        for request in self.failed_requests:
            last_success_row = request['last_success_row']
            drug_name = request['drug_name']
            
            if self.data_type == 'combos':
                drug_id = request['drug_id']

            existing_dict = next((dict_ for dict_ in combined_requests if dict_['last_success_row'] == last_success_row), None)

            if existing_dict is not None:
                existing_dict['requests'].append({'drug_name':drug_name})
                if self.data_type == 'combos':
                    existing_dict['requests'].append({'drug_name':drug_name, 'drug_id':drug_id})
            else:
                combined_requests.append({
                    'last_success_row': last_success_row,
                    'requests': [{'drug_name':drug_name}] if self.data_type == 'info' else [{'drug_name':drug_name, 'drug_id':drug_id}]
                })
        self.failed_requests = []
        return combined_requests
        ...
    ...

    # * - Documented
    async def get_data_async(self):
        """
        Asynchronously fetch data in batches and process them.

        This function performs the following steps:
        - Map the data using the drug names or drug IDs based on the data type.
        - Slice the data into manageable chunks (batches).
        - Initialize a progress bar to track the completion of data processing.
        - Process the data slices. If there are any failed requests, it retries them.

        Raises:
        KeyError: If the data type is not 'info' or 'combos'.
        """
        # Mapping data based on data type.
        data_map = {
            'info': self.drug_names,
            'combos': self.drug_ids,
        }
        # Select the data based on the data type.
        df = data_map[self.data_type]

        # Slice the DataFrame into batches.
        df_slices = self._get_df_slices(df)
        # df_slices = [df[i:i+batch_size] for i in range(restart_index, len(df), batch_size)]
        # Calculate the total number of batches for the progress bar.
        total_batches = len(df_slices)
        # Initialize a progress bar.
        progress_bar = tqdm(total=total_batches,
                            desc="Batches completed", dynamic_ncols=True)
        # Create an empty list for failed requests.
        self.failed_requests = []
        # Initalize the last successful row to None.
        self.last_success_row = None
        # Process the data slices and update the progress bar.
        await self.process_df_slices(df_slices, progress_bar)
        # If there were any failed requests, retry them.
        if self.failed_requests:
            while self.failed_requests:
                print('[+] Retrying failed requests...')
                processed_failed_requests = self.process_failed_requests()
                await self.retry_failed_requests(processed_failed_requests)
        self.logger.log_scraping_complete()
        ...
    ...


    # * - Documented
    async def _process_data(self, row):
        """
        This method processes a row of data based on the data type. 

        If the data type is 'info', the method will clean the drug name from the row, print it, and update the drug info dictionary.

        If the data type is 'combos', it will retrieve the drug name and drug ID from the row, print them, and update the drug combinations.

        Parameters:
        row (pd.Series): A row of data from a DataFrame.

        Returns:
        None. This method performs actions based on the data type and does not return anything.
        """

        if self.data_type == 'info':
            drug_info = [{}]
            # Clean the drug name
            cur_drug = clean_string(row['drug_name'])
            cur_display_drug = row['drug_name']

            # print(cur_display_drug)

            # Get the drug info and update drug_obj dictionary
            drug_info[0]['drug_name'] = cur_display_drug
            drug_info[0].update(await get_drug_info_httpx(cur_drug))
            return drug_info

        elif self.data_type == 'combos':
            drug_name = row['drug_name']
            drug_id = row['drug_id']
            # print(drug_name, drug_id)

            # Get the drug combinations and update drug_combos
            combos = await get_drug_combinations_httpx(drug_id, drug_name)
            drug_combos = combos
            return drug_combos
        ...
    ...

    # * - Documented
    async def process_df_slices(self, df_slices, progress_bar):
        """
        This method processes DataFrame slices asynchronously, updates a progress bar and handles the exceptions.

        Parameters:
        df_slices (iterable): An iterable containing DataFrame slices to be processed.
        progress_bar (ProgressBar object): An instance of a ProgressBar class to visualize the progress.

        Returns:
        None. The method updates the progress bar and handles the results as side-effects.
        """

        # Iterate over each DataFrame slice from df_slices
        for df_slice in df_slices:
            # Create a list of tasks where each task is to process data for a given row in df_slice
            tasks = [self._process_data(row) for _, row in df_slice.iterrows()]
            # Use asyncio.gather to run all tasks concurrently, return_exceptions=True ensures that instead of raising exceptions, it will return them so the code won't stop unexpectedly
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Process the results obtained from the tasks
            self.process_results(results, df_slice)
            # Update the progress bar after each df_slice is processed
            progress_bar.update()
        # Close the progress bar after all df_slices have been processed
        progress_bar.close()
        ...
    ...

# * - Documented
    def process_results(self, results, df_slice):
        """
        This method processes the results obtained from asynchronous tasks. 
        It handles both successful results and exceptions. 

        Parameters:
        results (list): A list of results returned from the tasks, each result could be data or an Exception.
        df_slice (DataFrame): A slice of DataFrame where each row corresponds to the respective result.

        Returns:
        None. The method handles the results as a side-effect, it does not return anything.
        """
        # Iterate over each result and corresponding DataFrame row
        for result, (index, row) in zip(results, df_slice.iterrows()):
            # If the result is an instance of Exception, handle it with the handle_failed_result method
            if isinstance(result, Exception):
                self.handle_failed_result(row)
            # If the result is not an Exception, it's considered a successful result and handled with handle_success_result method
            else:
                self.handle_success_result(result, row)
        ...
    ...

# * - Documented
    def _generate_failed_request_info(self, row):
        """
        This method generates information about a failed request, given the input row.

        It constructs a dictionary with various attributes of the request, including drug information
        and the last successful row number. If the data type of the class is 'adj', additional info
        like pharmacy id and type are also included.

        Parameters:
        row (pd.Series): A single row from a DataFrame containing the relevant data for the request.

        Returns:
        dict: A dictionary containing information about the failed request.
        """

        # Creating the base information for failed request
        failed_request_info = {
            'last_success_row': self.last_success_row,
            'drug_name': row['drug_name'],
        }

        # If data type is 'adj', add pharmacy_id and type to the failed request information
        if self.data_type == 'combos':
            failed_request_info.update({
                'drug_id': row['drug_id'],
            })

        # Return the failed request information
        return failed_request_info
        ...
    ...

# * - Documented
    def handle_failed_result(self, row):
        """
        This method handles failed results by retrying the operation and logging any exceptions that may occur. 

        If a retry also fails, it generates the information about the failed request, logs the failure, stores the failed request information for further use, and prints an error message.

        Parameters:
        row (Pandas Series or similar): A row of data that is to be processed. 

        Returns:
        None. The method handles exceptions and logging as side-effects.
        """

        # Attempt to retry and write data
        try:
            self.retry_and_write_data(row)
        except Exception as e:
            # If an exception occurs, generate the information about the failed request
            print(row)
            failed_request_info = self._generate_failed_request_info(row)
            # Log the failed request along with the exception
            self.logger.log_failed_request(failed_request_info, e)
            # Store the failed request information in the failed_request list for further use
            self.failed_requests.append(failed_request_info)
            # Print an error message
            print(
                f"Retry failed for row with Drug Name:{self.last_success_row['drug_name']}, ID:{self.last_success_row['drug_id']},  error: {e}")
        ...
    ...

# * - Documented
    def handle_success_result(self, result, row):
        """
        This method logs the parameters of a successful request, stores the last row of the successful request,
        stores the result data, writes the data to a CSV file and then carries out additional processing steps.

        Parameters:
        result (iterable): The result data from a successful request.
        row (pandas.Series or similar): The row of data that was used in the successful request.

        Returns:
        None. This method handles the result and updates class attributes as side-effects.
        """
        # Use logger to log the parameters that were used in the request
        self.logger.log_request_params(row.to_dict())

        # No Coupon Info aka no combinations
        if result == None:
            return

        # No drug concept error is the error caught here
        # Result is an error, log the error message
        if result[0].get('error') == True:
            self.logger.log_message('error', result[0].get('err_msg'))
        
        # Store the last row of the successful request
        self.last_success_row = result[-1]
        # Store the result data
        self.data = result
        # Write the result data to a CSV file
        self.write_to_csv()
        ...
    ...

    def retry_request(self, row):
        """
        This method performs a retry request for a given drug based on its data type. 
        If the data type is 'adj', it performs a coupon query; otherwise, it gets the prices for the drug.

        Parameters:
        row (dict or pandas.Series): A dictionary or pandas.Series representing a drug with keys 'drug_id', 
        'qty', 'pharmacy_id', 'drug_name', and 'type' (only necessary for 'adj' data type). 

        Returns:
        dict: A dictionary with the result of the retry request. For 'adj' data type, an additional 'type' key 
        is added to the result.
        """

        # Check the data type of the current instance
        if self.data_type == 'info':
            retry_result = [{}]
            # If the data type is 'adj', perform a coupon query
            formated_drug_name = clean_string(row['drug_name'])
            retry_result[0]['drug_name'] = row['drug_name']
            retry_result[0].update(get_drug_info(formated_drug_name))
            return retry_result
        elif self.data_type == 'combos':
            # If the data type is not 'adj', get the prices for the drug
            return get_drug_combinations(row['drug_id'], row['drug_name'])
        ...
    ...

# * - Documented
    def retry_and_write_data(self, row):
        """
        This method performs a retry request for a given row, updates the data attribute with the retry result,
        writes the updated data to a CSV file, and prints a success message.

        Parameters:
        row (dict or similar): A dictionary-like object with keys: "drug_id", "drug_name", "qty". 
                               This represents a row of data that a retry request will be performed on.

        Returns:
        None. The method has side-effects: it updates the data attribute, writes to a CSV file, and prints a success message.
        """
        # Perform a retry request for the given row and store the result
        retry_result = self.retry_request(row)
        # Update the data attribute with the result from the retry request
        self.data = retry_result
        # Write the updated data to a CSV file
        self.write_to_csv()
        # Print a success message including the drug_id, drug_name, and quantity from the row
        if self.data_type == 'info':
            print(f'[+] {row["drug_name"]} retry succeeded')
        elif self.data_type == 'combos':
            print(f'[+] {row["drug_id"]}-{row["drug_name"]} retry succeeded')
        ...
    ...

    def _load_dataframe(self):
        """
        Load a dataframe from a csv file. 

        The type of dataframe loaded depends on the `data_type` attribute of the instance. If `data_type` is 'prices', 
        it loads prices data from the 'prices_file_path' attribute of the instance with 'pharmacy_id' as Int64 dtype. 
        If `data_type` is 'adj', it loads adjacency data from the 'adj_file_path' with 'pharmacy_id' as Int64 dtype and 'bin' as str dtype.

        Attributes
        ----------
        self : object
            An instance of the class.

        Returns
        -------
        DataFrame
            A Pandas DataFrame loaded from a csv file.
        """

        if self.data_type == 'info':
            print('loading info df')
            return pd.read_csv(self.info_file_path, dtype={'Drug_id': 'Int64', 'schedule': 'Int64'})
        elif self.data_type == 'combos':
            print('loading combos df')
            return pd.read_csv(self.combos_file_path, dtype={'drug_id': 'Int64', 'qty': 'int64'})
        ...
    ...

    def _prepare_tasks(self, failed_req_list):
        """
        Prepares a list of tasks (either price retrieval or coupon queries) based on failed requests.

        The type of tasks to be prepared is determined by the `data_type` instance variable.
        If `data_type` is 'prices', the method prepares tasks for price retrieval.
        If `data_type` is not 'prices', the method prepares tasks for coupon queries.

        Each task is a function call, either to `get_prices_httpx` or `coupon_query_httpx`,
        with parameters extracted from the `failed_req_list` dictionary.

        Parameters:
        failed_req_list : list of tuples
            Contains data for failed requests. Each tuple represents one failed request.

        Returns:
        list
            A list of function calls, either to `get_prices_httpx` or `coupon_query_httpx`.
        """
        if self.data_type == 'info':
            return [get_drug_info_httpx(item['drug_name'])
                    for item in failed_req_list]
        else:
            return [get_drug_combinations_httpx(item['drug_id'], item['drug_name'])
                    for item in failed_req_list]
        ...
    ...

    def _handle_results(self, last_succesfull_row, failed_req_dict, results):
        """
        Handles the results of a list of requests, storing successful results and reprocessing failed requests.

        :param last_succesfull_row: Last successful row processed
        :type last_succesfull_row: dict
        :param failed_req_dict: A dictionary of failed requests
        :type failed_req_dict: dict
        :param results: A list of lists with dicts, where each sublist represents the result of a request
        :type results: list

        :return: A dictionary with the last successful row and combined results from all successful requests
        :rtype: dict
        """

        # Create a list to hold all successful results
        successful_results = []

        # Iterate over each result to check for successful results or exceptions
        for request, result in zip(failed_req_dict, results):
            # If result is an Exception, handle the exception
            if isinstance(result, Exception):
                self.handle_exception(request, last_succesfull_row, result)
            # If the request has succeeded upon retry, print a success message and add the result to the successful results list
            else:
                print(f"Retry succeeded for LSR {last_succesfull_row}")
                successful_results.extend(result)  # Assuming result is a list

        # Combine results from all successful requests
        combined_results = {'row': last_succesfull_row, 'results': successful_results}

        return combined_results
        ...
    ...

    def _find_matching_row_index(self, data, match_dict):
        """
            Finds the index of the row in the provided DataFrame that matches the provided dictionary.

            This function fills any NaN values in the 'pharmacy_id' column with 0 and converts the column to integers. 
            If the data_type attribute of the class is 'prices', it also converts the 'coupon_price' column to numeric. 
            It then searches for a row that matches the provided dictionary, with different conditions depending on the 
            data_type. If a single matching row is found, the index of that row is returned. If no match or more than 
            one match is found, the function returns None and prints the number of matching rows found.

            Parameters:
            data (pd.DataFrame): DataFrame to search in.
            match_dict (dict): Dictionary with the values to match.

            Returns:
            Optional[int]: The index of the matching row, or None if no match or more than one match is found.
        """

        # print(match_dict)
        # Check if match_dict contains all necessary keys
        required_keys_info = ['drug_name', 'drug_id', 'drug_class', 'sub_name', 'schedule', 'description', 'image_url']
        required_keys_combos = ['drug_id', 'drug_name', 'generic_status', 'form', 'dosage', 'qtys']

        if self.data_type == 'info' and not all(key in match_dict for key in required_keys_info):
            raise ValueError(
                "match_dict is missing one or more required keys for 'info' data type")
        elif self.data_type == 'combos' and not all(key in match_dict for key in required_keys_combos):
            raise ValueError(
                "match_dict is missing one or more required keys for 'combos' data type")

        # Depending on the data type, run the corresponding function
        if self.data_type == 'info':            # if self.data_type == 'prices':
            # temp_pharmacy_id = data['pharmacy_id'].fillna(0).astype(int)
            # temp_coupon_price = pd.to_numeric(data['price'], errors='coerce')
            # Match rows where 'pharmacy_id' is not 0
            matching_rows = data[
                # pd.notna(temp_pharmacy_id) &  # Checks for non-missing values
                # (temp_pharmacy_id != 0) &  # Excludes rows where pharmacy_id is 0
                (data['drug_name'] == match_dict['drug_name']) &
                (data['drug_id'] == match_dict['drug_id']) &
                (data['drug_class'] == match_dict['drug_class']) &
                (data['sub_name'] == match_dict['sub_name']) &
                (data['schedule'] == match_dict['schedule']) &
                (data['description'] == match_dict['description']) &
                (data['image_url'] == match_dict['image_url']) 
                # (data['qty'] == match_dict['qty']) &
                # (temp_pharmacy_id == match_dict['pharmacy_id']) &
                # (data['pharmacy_name'] == match_dict['pharmacy_name']) &
                # (data['type'] == match_dict['type']) &
                # (temp_coupon_price == match_dict['price'])
            ]
        elif self.data_type == 'combos':
            # Match rows where 'pharmacy_id' is not 0
            matching_rows = data[
                # Excludes rows where pharmacy_id is 0
                # (data['pharmacy_id'] != 0) &
                (data['drug_id'] == match_dict['drug_id']) &
                (data['drug_name'] == match_dict['drug_name']) &
                (data['generic_status'] == match_dict['generic_status']) &
                (data['form'] == match_dict['form']) &
                (data['dosage'] == match_dict['dosage']) &
                (data['qtys'] == match_dict['qtys']) 
                # (data['pharmacy_id'] == match_dict['pharmacy_id']) &
                # (data['group_id'] == match_dict['group_id']) &
                # (data['bin'] == match_dict['bin']) &
                # (data['pcn'] == match_dict['pcn'])
            ]

        if len(matching_rows) == 1:
            # print("Found!")
            # sys.exit()
            return matching_rows.index[0]
        else:
            print(f"Found {len(matching_rows)} matching rows.")
            # sys.exit()
            return None
        ...
    ...


    def _insert_rows(self, df, row_and_results):
        """
        Insert rows to a dataframe at the position of a specific row.

        Parameters:
        df (pd.DataFrame): The original DataFrame to which new rows need to be added.
        row_and_results (dict): A dictionary with 'row' being the reference row, and 'results' being the new rows to add.

        Returns:
        df (pd.DataFrame): The modified DataFrame with the new rows inserted.
        """

        # Get the reference row and the new rows from the input dictionary
        last_successful_row = row_and_results['row']
        results = row_and_results['results']

        # Convert the results to a DataFrame
        new_rows = pd.DataFrame(results)

        # Find the index of the reference row
        index = self._find_matching_row_index(df, last_successful_row)

        # Split the original DataFrame into two parts, before and after the reference row
        df_first = df[df.index <= index]
        df_second = df[df.index > index]

        # Concatenate the first part, the new rows, and the second part to form the final DataFrame
        df = pd.concat([df_first, new_rows, df_second])

        # Reset index
        df = df.reset_index(drop=True)

        # Return the modified DataFrame
        return df
        ...
    ...

    async def retry_failed_requests(self, combined_failed_requests):
        """
        Retry failed requests and write results to a csv file.

        Parameters:
        combined_failed_requests: A list of dictionaries. Each dictionary contains a failed request.
            - Each dictionary has the following format:
                'last_success_row': last successful row number before a request failure,
                'requests': failed requests data.

        Returns:
        None. But it writes the request results to a csv file.

        Raises:
        Any exceptions that may occur in the function call asyncio.gather(*tasks, return_exceptions=True).
        """

        # Load initial dataframe
        df_all = self._load_dataframe()

        # Iterate over all failed requests
        for combined_request in combined_failed_requests:
            last_succesfull_row = combined_request['last_success_row']
            failed_req_list = combined_request['requests']

            # Prepare tasks from failed requests
            tasks = self._prepare_tasks(failed_req_list)

            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results and combine them
            combined_results = self._handle_results(
                last_succesfull_row, failed_req_list, results)

            # If there are any combined results, insert them into dataframe
            if combined_results:
                df_all = self._insert_rows(df_all, combined_results)

        # If data_type is 'prices' or 'adj', write the dataframe to csv
        # If data_type is not recognized, no action is performed
        if self.data_type == 'prices':
            df_all.to_csv(self.prices_file_path, index=False)
        elif self.data_type == 'adj':
            df_all.to_csv(self.adj_file_path, index=False)
        ...
    ...

    def handle_exception(self, request, last_succesfull_row, result):
        self.last_success_row = last_succesfull_row
        self._generate_failed_request_info(request)
        print(*request)
        print(f"Retry failed for LSR {last_succesfull_row}, error: {result}")

# * - Documented

    def write_to_csv(self):
        """
        Writes the contents of the Drug object to a CSV file.

        This method first converts the Drug data to a pandas DataFrame. Then, it checks if the 'results' directory 
        exists and creates it if necessary. After that, it creates the CSV filename for the specific data type
        "info" or "combos". Then checks its exsitence in the file system if it does, it appends the DataFrame to 
        the file, otherwise, it creates a new file.

        The CSV file name is derived from the data_type attribute and follows the format 'all_drugs{data_type}(s).csv'. 
        For example, if 'data_type' is 'info', the CSV file will be named 'all_drug_infos.csv'.

        Note:
        This method does not return anything as it writes directly to a CSV file.
        """
        data = f'drug_{self.data_type}'
        df = pd.DataFrame(self.data)

        os.makedirs(f'results/{data}', exist_ok=True)

        filename = self._construct_filename()
        file_path = os.path.join(f'results/{data}', filename)

        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            df.to_csv(file_path, mode='a', index=False)
        else:
            df.to_csv(file_path, mode='a', index=False, header=False)
        ...
    ...

    def remove_html_tags(self, df, column_name):
        # Regular expression pattern to match and remove HTML tags
        tag_re = re.compile(r'<[^>]+>')
        
        # Apply the regular expression to the specified column
        df[column_name] = df[column_name].apply(lambda x: tag_re.sub('', str(x)) if pd.notnull(x) else x)
        
        return df

# * - Documented
    def format(self):
        """
        This method reads a CSV file containing drug combinations, transforms the data format and then saves the transformed DataFrame back to a CSV file.

        Specifically, it performs the following operations:
        1. Reads a CSV file into a DataFrame.
        2. Converts a string representation of lists in the 'qtys' column to actual lists.
        3. 'Explodes' the 'qtys' column so that each element in the lists gets its own row.
        4. Renames the 'qtys' column to 'qty'.
        5. Writes the transformed DataFrame back to a new CSV file.

        Parameters: None

        Returns: None. The function performs its operations as side-effects.
        """
        # Read the CSV file into a DataFrame
        # df = pd.read_csv('results/drug_combos/all_drug_combos.csv')
        info_df = self.remove_html_tags(pd.read_csv(self.info_file_path), 'description')
        info_df.to_csv(self.info_file_path, index=False)
        combos_df = pd.read_csv(self.combos_file_path)
        # Convert the 'qty' column from a string representation of lists to actual lists
        combos_df['qtys'] = combos_df['qtys'].apply(ast.literal_eval)
        # "Explode" the 'qtys' column so that each element in the lists gets its own row
        combos_df = combos_df.explode('qtys')
        # Rename the 'qtys' column to 'qty'
        combos_df.rename(columns={'qtys': 'qty'}, inplace=True)
        # Write the transformed DataFrame back to a new CSV file
        # combos_df.to_csv('results/drug_combos/all_drug_combos_exploded.csv', index=False)
        combos_df.to_csv(
            'results/drug_combos/all_drug_combos_exploded.csv', index=False)
        ...
    ...


# drug_scraper = DrugScraper()

# a_drugs = scraper.get_drug_names('a')
# b_drugs = scraper.get_drug_names('b')

# print([clean_string(drug) for drug in a_drugs])
# print([clean_string(drug) for drug in b_drugs])

# scraper.get_combos()
# drug_scraper.scrape()
# drug_scraper.format()
