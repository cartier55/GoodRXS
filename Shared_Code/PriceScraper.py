import re
from httpx import get
import pandas as pd
import os
import io
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
from complete import complete_sound
from test_find import failed_req
from test_fix import fix

from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError, RequestException, ConnectTimeout, ReadTimeout

from async_data_fetchers import get_drug_combinations_httpx, get_drug_info_httpx, coupon_query_httpx, get_prices_httpx
import aiofiles


class PriceScraper:

    def __init__(self):
        # self.logger = Logger()
        self.batch_size = 100
        self.combos = None
        self.drug_prices = None
        self.drug_adj = [{}]
        self.data = [{}]
        self.data_types = ['prices', 'adj']

        # ! - Prod price file path
        self.prices_file_path = 'results/drug_prices/all_drug_prices.csv'
        # self.prices_file_path = 'results/drug_prices/all_drug_prices_test_1.csv'
        # ! - Prod combos file path
        self.combos_file_path = 'results/drug_combos/all_drug_combos_exploded.csv'
        # self.combos_file_path = 'results/drug_combos/all_drug_combos_exploded_test_1.csv'
        # ! - Prod adj file path
        self.adj_file_path = 'results/drug_adj/all_drug_adjs.csv'
        # self.adj_file_path = 'results/drug_adj/all_drug_adjs_test_1.csv'

        # self.filename_override = {
        #     'prices': 'all_drug_prices_test_1.csv',
        #     'adj': 'all_drug_adjs_test_1.csv'
        # }
        ...

    def _construct_filename(self):

        filename_override = getattr(self, "filename_override", None)

        if self.data_type in ['prices', 'adj']:
            if filename_override:
                return filename_override[self.data_type]
            else:
                return f'all_drug_{self.data_type}s.csv' if self.data_type == 'adj' else f'all_drug_{self.data_type}.csv'
        else:
            raise ValueError("Data type must be either 'prices' or 'adj'.")
        ...
    ...

    def _check_path(self, path):
        if not os.path.isfile(path):
            sys.exit(f"File {path} does not exist")
        ...
    ...

    def _check_process(self):
        if self.data_type == 'prices':
            if os.path.isfile(self.prices_file_path):
                prices_df = pd.read_csv(self.prices_file_path)
                combos_df = pd.read_csv(self.combos_file_path)
                print(len(prices_df), len(combos_df))
                sys.exit()
                if len(prices_df) == len(combos_df):
                    print('''
                    [+] Drug Prices ✅

                    Continuing to Drug Adjucations...
                          ''')
                    sleep(3)
                    clear(False)
                    # self.get_combos()
                    return True
                else:
                    print('''
                    [+] Drug Prices ❌

                    Continuing to Drug Prices...
                          ''')
                    sleep(3)
                    clear(False)
                    return False
            else:
                print('''
                    [+] Drug Prices ❌

                    Continuing to Drug Prices...
                          ''')
                sleep(3)
                clear(False)
                return False
        elif self.data_type == 'adj':
            if os.path.isfile(self.adj_file_path):
                adj_df = pd.read_csv(self.adj_file_path)
                prices_df = pd.read_csv(self.prices_file_path)
                if len(adj_df) == len(prices_df):
                    print('''
                    [+] Drug Prices ✅
                    [+] Drug Adjucations ✅
                          ''')
                    sleep(3)
                    clear(False)
                    return True
                else:
                    print('''
                    [+] Drug Prices ✅
                    [-] Drug Adjucations ❌

                    Continuing to Drug Adjucations...
                          ''')
                    sleep(3)
                    clear(False)
                    return False
            else:
                print('''
                    [+] Drug Prices ✅
                    [-] Drug Adjucations ❌

                    Continuing to Drug Adjucations...
                          ''')
                sleep(3)
                clear(False)
                return False
        ...
    ...

    def set_failed_requests(self, failed_requests):
        self.failed_requests = failed_requests
        ...

    # * - Documented
    def process_failed_requests(self):
        """
        Processes a list of failed requests and groups them by last_success_row.

        Parameters:
        failed_requests (list): List of dictionaries containing last_success_row, drug_name, drug_id, and qty.

        Returns:
        dict: Dictionary with last_success_row as keys and dictionaries of drug info as values.
        """
        # Initialize a list to store combined requests
        combined_requests = []

        # Iterate over all failed requests
        for request in self.failed_requests:
            # Extract relevant data from each request
            last_success_row = request['last_success_row']
            drug_name = request['drug_name']
            drug_id = request['drug_id']
            qty = request['qty']

            # If data type is 'adj', additional details are extracted
            if self.data_type == 'adj':
                price_type = request['type']
                pharmacy_id = request['pharmacy_id']

            # Look for an existing dictionary in combined_requests that matches 'last_success_row'
            existing_dict = next((dict_ for dict_ in combined_requests if dict_[
                                 'last_success_row'] == last_success_row), None)

            # If existing dictionary is found, append new data to its 'requests' list
            if existing_dict is not None:
                if self.data_type == 'prices':
                    existing_dict['requests'].append((drug_id, qty, drug_name))
                if self.data_type == 'adj':
                    existing_dict['requests'].append(
                        (drug_name, drug_id, qty, pharmacy_id, price_type))
            else:
                # If no existing dictionary is found, create a new one and append it to combined_requests
                combined_requests.append({
                    'last_success_row': last_success_row,
                    'requests': [(drug_id, qty, drug_name)] if self.data_type == 'prices' else [(drug_name, drug_id, qty, pharmacy_id, price_type)]
                })

        return combined_requests
        ...
    ...

    # * - Documented
    def _check_restart(self, last_row):
        """
        Method to check the existence of a given row's elements ('drug_id', 'qty', 'drug_name', 'pharmacy_id' if applicable) 
        in a given DataFrame (either 'combos' or 'drug_prices'). 

        Parameters:
        last_row : dict
            Contains the 'drug_id', 'qty', 'drug_name', and 'pharmacy_id' (if applicable) to be checked

        Raises:
        SystemExit
            If the given row's elements are not found in the DataFrame. 

        Returns:
        None
        """

        # Define last values from last_row
        last_drug_id = last_row['drug_id']
        last_qty = last_row['qty']
        last_drug_name = last_row['drug_name']

        if self.data_type == 'adj':
            last_pharmacy_id = last_row['pharmacy_id']

        # Construct a dictionary to use with pandas isin function
        row_dict = {'drug_id': last_drug_id,
                    'qty': last_qty, 'drug_name': last_drug_name}
        if self.data_type == 'adj':
            row_dict['pharmacy_id'] = last_pharmacy_id

        # Select the dataframe to check based on data_type
        df_to_check = self.combos if self.data_type == 'prices' else self.drug_prices

        # Check if the current row exists in the DataFrame
        if not df_to_check.isin(row_dict).all(1).any():
            sys.exit(
                f"Row with Drug ID {last_drug_id}, qty {last_qty}, {('pharmacy ID ' + str(last_pharmacy_id) + ',') if self.data_type == 'adj' else ''} and name {last_drug_name} not found in the DataFrame.")
        ...
    ...

    # * - Documented
    def _calc_restart_index(self, obj):
        """
        Calculate the next index for either prices or adjustment data depending on the data type.

        The function operates by locating the last index of a specific drug based on its id, quantity,
        and name from either the combos or drug_prices data. It then returns the next index.

        Parameters:
        obj (dict): Dictionary containing the details of the drug.

        Returns:
        int: Next index.
        """
        # Extract relevant details from the input dictionary object.
        # These details include the drug's name, its unique identifier, and its quantity.
        # drug_name = obj['drug_name']
        # drug_id = obj['drug_id']
        # qty = obj['qty']
        try:
            drug_id = obj['drug_id'].iloc[0]
            drug_name = obj['drug_name'].iloc[0]
            qty = obj['qty'].iloc[0]
        except AttributeError as e:
            drug_id = obj['drug_id']
            drug_name = obj['drug_name']
            qty = obj['qty']
        # Depending on the data type being handled, the function will look for the last index in different ways.
        if self.data_type == 'prices':
            # If the data type is 'prices', the function looks in the 'combos' DataFrame.
            # It locates the last index where the drug_id, quantity, and drug name match the provided values.
            current_index = self.combos[
                (self.combos['drug_id'].astype(int) == int(drug_id)) &
                (self.combos['qty'].astype(int) == int(qty)) &
                (self.combos['drug_name'].astype(str) == str(drug_name))
            ].index[-1]
        elif self.data_type == 'adj':
            # If the data type is 'adj', the function looks in the 'drug_prices' DataFrame instead.
            # It also takes into account additional attributes: pharmacy_id and type.
            try:
                pharmacy_id = obj['pharmacy_id'].iloc[0]
                price_type = obj['type'].iloc[0]
            except AttributeError as e:
                pharmacy_id = obj['pharmacy_id']
                price_type = obj['type']
            current_index = self.drug_prices[
                (self.drug_prices['drug_id'] == drug_id) &
                (self.drug_prices['qty'] == qty) &
                (self.drug_prices['drug_name'] == drug_name) &
                (self.drug_prices['pharmacy_id'] == pharmacy_id) &
                (self.drug_prices['type'] == price_type)
            ].index[-1]

            # Since the drug prices df is altered in the import to only include type coupon
            # we need to grab the positsion of the last index in the df
            pos = self.drug_prices.index.get_loc(current_index)

            # The add 1 to current posistion to get the next posistion then get the index for that positsion
            # Which is the next index
            next_index = self.drug_prices.index[pos + 1]
        # The next index is then returned as the result of the function.
        return next_index
        ...
    ...

    # * - Documented

    def _get_last_line(self, file_path):
        """
        Reads the headers and the last line of a file.

        Args:
            file_path (str): The path of the file to read.

        Returns:
            pd.DataFrame: A DataFrame containing the last line of the file with headers.
        """
        with open(file_path, 'rb') as f:
            # Get headers
            headers = f.readline().decode().strip().split(',')

            # Go to the end of file
            f.seek(-2, os.SEEK_END)

            # Go backwards until a newline character is found
            while f.read(1) != b'\n':
                f.seek(-2, io.SEEK_CUR)

            # Read and decode the last line
            last_line = f.readline().decode().strip().split(',')

        # Create a DataFrame
        df_last_line = pd.DataFrame([last_line], columns=headers)

        # Convert the data type of 'drug_id' and 'qty' to int
        df_last_line['drug_id'] = df_last_line['drug_id'].astype(int)
        df_last_line['qty'] = df_last_line['qty'].astype(int)
        if 'pharmacy_id' in df_last_line.columns:
            df_last_line['pharmacy_id'] = df_last_line['pharmacy_id'].astype(
                int)

        return df_last_line
        ...
    ...

    def get_restart_index(self):
        """
        Get the index from which to restart a process, based on the data stored in a specific file.

        The function first constructs the file path, then checks if the file exists and is not empty.
        If the file exists and is not empty, it retrieves the last request parameters logged.
        If these parameters are present, the restart index is calculated based on them.
        If the parameters are not present, the restart index is calculated based on the last row of the DataFrame.

        Returns:
            int: The index from which to restart the process. If the file doesn't exist or is empty, returns 0.
        """

        # Construct the file path
        file_name = self._construct_filename()
        file_path = os.path.join(f'results/drug_{self.data_type}', file_name)

        if os.path.isfile(file_path) and os.stat(file_path).st_size != 0:
            prev_params = self.logger.get_last_request_params()
            if prev_params:
                # Determine the restart point based on the last logged parameters
                return self._calc_restart_index(prev_params)
            else:
                # Get the last line in the file
                last_row = self._get_last_line(file_path)
                # Convert the last line to DataFrame
                # assuming the file is comma-separated
                # last_row = pd.DataFrame([last_line.split(',')])

                # Check if the last row in the DataFrame matches any of the rows in the initial data
                # print(last_row)
                # self._check_restart(last_row)

                # Determine the restart point manually if there are no last logged parameters
                # next_index = self._calc_restart_index(last_row)
                # current_index = next_index - 1
                # print('current_index', current_index)
                # print(f"Restarting from index {next_index}.")
                # print('current index')
                # print(self.drug_prices.iloc[current_index])
                # print('next index')
                # print(self.drug_prices.iloc[next_index])
                # print('last index')
                # print(self.drug_prices.iloc[-1])
                # sys.exit()

                return self._calc_restart_index(last_row)
        else:
            # The file is not found or is empty, return 0
            return 0
        ...
    ...

    def run(self):
        if self._check_process('prices'):
            self.get_drug_pharmacies()
            self.get_data('adj')
        else:
            self.get_combos()
            self.get_data('prices')
            self.get_drug_pharmacies()
            self.get_data('adj')

        print('[+] Done!')

        # self.get_combos()
        # self.get_data('prices')
        # self.get_drug_pharmacies()
        # self.get_data('adj')
        ...
    ...

    def run_timer(self):
        print("""
              [+]Starting Timer...
              """)
        start = time.time()
        self._check_process('prices')
        self.get_combos()
        # self.get_data('prices')
        asyncio.run(self.get_data_async('prices'))
        end = time.time()
        elapsed_time = end - start  # This is the elapsed time in seconds.
        minutes, seconds = divmod(elapsed_time, 60)
        print(f'Time taken: {int(minutes)} minutes and {seconds:.2f} seconds')
        ...
    ...

    def run_async(self):
        start = time.time()
        # # self.data_type = 'prices'
        # for type in self.data_types:
        #     self.data_type = type
        #     if self._check_process():
        #         continue
        #     else:
        #         self.get_inital_data()
        #         asyncio.run(self.get_data_async())
        self.data_type = 'adj'
        self.logger = Logger(self.data_type)
        # self._set_data_type(self.data_type)
        # self._check_process()
        self.get_initial_data()
        asyncio.run(self.get_data_async())

        end = time.time()
        elapsed_time = end - start  # This is the elapsed time in seconds.
        minutes, seconds = divmod(elapsed_time, 60)
        print(f'Time taken: {int(minutes)} minutes and {seconds:.2f} seconds')
        ...
    ...

    # * - Documented
    def _set_data_type(self, data_type):
        """
        Setter method to update the 'data_type' attribute of the class.

        This method checks if the given 'data_type' is included in the 'data_types' attribute of the class. If it's not, 
        it raises a ValueError, otherwise it sets the 'data_type' attribute to the given value.

        Parameters
        ----------
        data_type : str
            The new data type to be set. It should be either 'prices' or 'adj'.

        Raises
        -------
        ValueError
            If the 'data_type' provided is not in the 'data_types' list.
        """
        if data_type not in self.data_types:
            raise ValueError(
                f"Invalid data type. Expected either 'prices' or 'adj', got {data_type}.")
        else:
            self.data_type = data_type
        ...
    ...

    # * - Documented
    def _get_drug_pharmacies(self):
        """
        This method is responsible for reading the drug prices from a CSV file into a pandas DataFrame.

        The CSV file should contain the following columns: 'drug_id', 'drug_name', 'qty', 
        'pharmacy_id', 'type'. It also checks if the file path is valid before proceeding.

        Attributes
        ----------
        self.prices_file_path : str
            The path to the CSV file containing drug prices information.
        self.drug_prices : DataFrame
            The pandas DataFrame holding the drug prices information.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing the drug prices information.
        """
        # Check the path to CSV file
        # ! - Dont Change Here - !
        # ! - Change in __init__ - !
        self._check_path(self.prices_file_path)

        # Read the CSV file into a pandas DataFrame
        self.drug_prices = pd.read_csv(self.prices_file_path, usecols=[
            'drug_id', 'drug_name', 'qty', 'pharmacy_id', 'type'], dtype={'pharmacy_id': 'Int64'})

        # Only keep rows where data_type equals COUPON
        self.drug_prices = self.drug_prices.query('type == "COUPON"')
        # return self.drug_prices
        ...
    ...

    # * - Documented
    def _get_combos(self):
        """
        This method reads a CSV file specified by the self.combos_file_path attribute
        and loads it into a pandas DataFrame, selecting only the 'drug_id', 'drug_name', 
        and 'qty' columns. The DataFrame is then assigned to self.combos.

        :return: None
        """

        # check if the file path exists
        # ! - Dont Change Here - !
        # ! - Change in __init__ - !
        self._check_path(self.combos_file_path)

        # read the CSV file into a DataFrame and select only the required columns
        df = pd.read_csv(self.combos_file_path, usecols=[
                         'drug_id', 'drug_name', 'qty'])

        # assign the DataFrame to self.combos
        self.combos = df
        ...
    ...

    # * - Documented
    def get_initial_data(self):
        """
        Fetch initial data based on the data type.

        The data type can either be 'prices', in which case the method fetches combos, 
        or 'adj', in which case it fetches drug pharmacies. If the data type is neither, 
        the method does nothing.

        Raises:
            ValueError: If `self.data_type` is not 'prices' or 'adj'.
        """
        if self.data_type == 'prices':
            self._get_combos()
        elif self.data_type == 'adj':
            self._get_drug_pharmacies()
        else:
            raise ValueError(f"Invalid data type: {self.data_type}")

    # * - Documented
    def _get_df_slices(self, df, batch_size=50):
        """
        Splits a DataFrame into smaller slices of specified size.

        Args:
            df (pd.DataFrame): The DataFrame to be sliced.
            batch_size (int, optional): The size of each slice. Defaults to 50.

        Returns:
            list: A list containing slices of the original DataFrame.
        """
        restart_index = self.get_restart_index()
        # Get the position of the restart_index in the DataFrame
        restart_position = df.index.get_loc(restart_index)
        return [df.iloc[i:i+self.batch_size] for i in range(restart_position, len(df), self.batch_size)]
        ...
    ...

    # * - Documented
    async def get_data_async(self):
        """
        This method asynchronously processes data slices derived from a selected dataframe (df). If any requests fail, it attempts to retry those requests.

        :param self: represents the instance of the class. 
        :returns: No return value
        """
        # A dictionary mapping data types to their respective dataframes
        data_map = {
            'prices': self.combos,
            'adj': self.drug_prices,
        }

        # Selects the appropriate dataframe based on the data_type attribute
        df = data_map[self.data_type]

        # Get dataframe slices by calling a separate function
        df_slices = self._get_df_slices(df)

        # Initialize a progress bar using tqdm for tracking the completion of processing batches
        total_batches = len(df_slices)
        progress_bar = tqdm(total=total_batches,
                            desc="Batches completed", dynamic_ncols=True)

        # Initializations before starting processing
        self.failed_requests = []
        self.last_success_row = None

        # Process the dataframes slices asynchronously
        await self._process_df_slices(df_slices, progress_bar)

        # If any requests failed, retry those requests
        if self.failed_requests:
            print('[+] Retrying failed requests...')
            processed_failed_requests = self.process_failed_requests()
            await self.retry_failed_requests(processed_failed_requests)
        self.logger.log_scraping_complete()
        complete_sound()
        ...
    ...

    # * - Documented
    async def _get_data_for_row(self, row):
        """
        Asynchronously fetches and prepares data for a given row. 
        Based on the self.data_type, it can either prepare adjustment or price data.

        Args:
            row (dict): A dictionary representing a row of data with keys:
                'drug_name': str, 'drug_id': str, 'qty': int, 'type': str, 'pharmacy_id': str

        Returns:
            list: A list of dictionaries containing fetched and prepared data.
        """
        drug_name = row['drug_name']
        drug_id = row['drug_id']
        qty = row['qty']
        data = []

        if self.data_type == 'adj':
            price_type = row['type']
            pharmacy_id = row['pharmacy_id']
            if pd.isna(pharmacy_id):
                print(drug_name, drug_id, qty, 'no pharmacy id')
                data.append({
                    'drug_name': drug_name,
                    'drug_id': drug_id,
                    'qty': qty,
                    'pharmacy_id': '',
                    'group_id': '',
                    'bin': '',
                    'pcn': ''
                })
            else:
                res = await coupon_query_httpx(drug_id, qty, pharmacy_id, drug_name)
                res[0]['type'] = price_type
                data.extend(res)

        elif self.data_type == 'prices':
            res = await get_prices_httpx(drug_id, qty, drug_name)
            data.extend(res)

        return data
        ...
    ...

    # * - Documented
    async def _process_df_slices(self, df_slices, progress_bar):
        """
        Asynchronously processes slices of a DataFrame based on the 'data_type' attribute.
        For 'prices' type, all rows of each slice are processed. For 'adj' type, only rows with 'type' as 'COUPON' are processed.

        Args:
            df_slices: Iterable containing slices of a DataFrame to process.
            progress_bar: An instance of a progress bar object to update.

        Returns:
            This function doesn't return anything. It updates the instance with the results.
        """

        # Loop through each DataFrame slice
        for df_slice in df_slices:
            # Check the type of data to process
            if self.data_type == 'prices':
                # For 'prices', process all rows
                tasks = [self._get_data_for_row(row)
                         for _, row in df_slice.iterrows()]
            elif self.data_type == 'adj':
                # For 'adj', process only rows where 'type' is 'COUPON'
                tasks = [self._get_data_for_row(
                    row) for _, row in df_slice.iterrows() if row['type'] == 'COUPON']

            # Gather results of tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            self._process_results(results, df_slice)

            # Update progress bar
            progress_bar.update()

        # Close progress bar
        progress_bar.close()
        ...
    ...

    # * - Documented

    def _process_results(self, results, df_slice):
        """
        Process each result from `results` with the corresponding row in `df_slice`.

        For each result, if the result is an instance of Exception, it calls `handle_failed_result` 
        to handle the exception. Otherwise, it calls `handle_success_result` to handle the result.

        Parameters
        ----------
        results : list
            The list of results to process. This can contain either results or exceptions.

        df_slice : pd.DataFrame
            The slice of the DataFrame that corresponds to `results`. Each result is processed with 
            the corresponding row in this DataFrame.

        Returns
        -------
        None
        """
        for result, (index, row) in zip(results, df_slice.iterrows()):
            if isinstance(result, Exception):
                # If the result is an Exception, handle it as a failure
                self.handle_failed_result(result, row)
            else:
                # Otherwise, handle the result as a success
                self.handle_success_result(result, row)
        ...
    ...

    # * - Documented

    def _generate_failed_request_info(self, row: dict) -> dict:
        """
        Method to generate a dictionary containing failed request information.

        Parameters:
        row (dict): A dictionary that represents a row of data. It should at least contain the following keys: 'drug_name', 'drug_id', 'qty'. 
                    If self.data_type equals 'adj', it should also contain 'pharmacy_id' and 'type'.

        Returns:
        dict: A dictionary containing the failed request information.

        Raises:
        KeyError: If any of the required keys are missing in the row dictionary.
        """
        # Ensure all required keys are present in the row dictionary
        required_keys = ['drug_name', 'drug_id', 'qty']
        if self.data_type == 'adj':
            required_keys.extend(['pharmacy_id', 'type'])

        if not all(key in row for key in required_keys):
            raise KeyError(
                f'Missing one or more required keys: {required_keys}')

        failed_request_info = {
            'last_success_row': self.last_success_row,
            'drug_name': row['drug_name'],
            'drug_id': row['drug_id'],
            'qty': row['qty']
        }
        if self.data_type == 'adj':
            failed_request_info.update({
                'pharmacy_id': row['pharmacy_id'],
                'type': row['type']
            })
        return failed_request_info
        ...
    ...

    # * - Documented
    def handle_failed_result(self, result, row):
        """
        Handles failed results by attempting a retry and logging the error if the retry fails.

        Parameters:
        - result: The result that has failed.
        - row: The data row for which the result has failed.

        The method does the following:
        - Tries to retry and write the data for the given row
        - If an exception occurs, it does the following:
        - Generates failed request info
        - Logs the failed request
        - Appends the failed request info to the failed_request list
        - Prints an error message
        """
        try:
            self.retry_and_write_data(row)
        except Exception as e:
            failed_request_info = self._generate_failed_request_info(row)
            self.logger.log_failed_request(failed_request_info, e)
            self.failed_requests.append(failed_request_info)
            print(f"Retry failed for row {self.last_success_row}, error: {e}")
        ...
    ...

    # * - Documented

    def handle_success_result(self, result, row):
        """
        Handles successful result data.

        This function takes the result data as input, updates the last successful row,
        stores the result data in an instance variable, and writes it to a CSV file
        asynchronously.

        Parameters:
        result (list): The result data to be handled.

        Returns:
        None
        """
        # Use logger to log the parameters that were used in the request
        self.logger.log_request_params(row.to_dict())
        # The last row of result data is stored
        self.last_success_row = result[-1]

        # All of the result data is stored
        self.data = result

        # Calls method to write data to a CSV file asynchronously
        self.write_to_csv_async()
        ...
    ...

    # * - Documented

    def _retry_request(self, row):
        """
        Function to retry a request depending on the data type.

        Parameters:
        row (dict): A dictionary containing the drug details including 'drug_id', 'qty', 'pharmacy_id', 'drug_name' and 'type'.

        Returns:
        dict: The result of the retry, which could either be a coupon query or a price retrieval.
        """

        # Check if the data type is 'adj'
        if self.data_type == 'adj':
            # Perform the coupon query again
            retry_result = coupon_query(
                row['drug_id'], row['qty'], row['pharmacy_id'], row['drug_name'])
            # Assign the type from the row to the result
            retry_result[0]['type'] = row['type']
            return retry_result
        else:
            # If the data type is not 'adj', get the prices again
            return get_prices(row['drug_id'], row['qty'], row['drug_name'])
        ...
    ...

    # * - Documented
    def retry_and_write_data(self, row: dict) -> None:
        """
        Tries to get data using a retry request and then writes the data to a CSV file asynchronously. 

        Parameters:
        row (dict): A dictionary containing data about the drug with keys 'drug_id', 'drug_name' and 'qty'.

        Returns:
        None
        """
        retry_result = self._retry_request(row)
        self.data = retry_result
        self.write_to_csv_async()
        print(
            f'[+] {row["drug_id"]} {row["drug_name"]} {row["qty"]} retry succeeded')
        ...
    ...

    # * - Documented
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

        if self.data_type == 'prices':
            print('loading prices df')
            return pd.read_csv(self.prices_file_path, dtype={'pharmacy_id': 'Int64'})
        elif self.data_type == 'adj':
            print('loading adj df')
            return pd.read_csv(self.adj_file_path, dtype={'pharmacy_id': 'Int64', 'bin': str})
        ...
    ...

    #  * - Documented
    def _prepare_tasks(self, failed_req_dict):
        """
        Prepares a list of tasks (either price retrieval or coupon queries) based on failed requests.

        The type of tasks to be prepared is determined by the `data_type` instance variable.
        If `data_type` is 'prices', the method prepares tasks for price retrieval.
        If `data_type` is not 'prices', the method prepares tasks for coupon queries.

        Each task is a function call, either to `get_prices_httpx` or `coupon_query_httpx`,
        with parameters extracted from the `failed_req_dict` dictionary.

        Parameters:
        failed_req_dict : list of tuples
            Contains data for failed requests. Each tuple represents one failed request.

        Returns:
        list
            A list of function calls, either to `get_prices_httpx` or `coupon_query_httpx`.
        """
        if self.data_type == 'prices':
            return [get_prices_httpx(int(drug_id), int(qty), drug_name)
                    for drug_id, qty, drug_name in failed_req_dict]
        else:
            return [coupon_query_httpx(int(drug_id), int(qty), int(pharmacy_id), drug_name)
                    for drug_name, drug_id, qty, pharmacy_id, _ in failed_req_dict]
        ...
    ...

    # * - Documented
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

        # Combine results from all successful requests
        combined_results = {'row': last_succesfull_row, 'results': [
            item for sublist in results for item in sublist]}

        # Handle each failed request
        for request, result in zip(failed_req_dict, results):
            # If result is an Exception, handle the exception
            if isinstance(result, Exception):
                self.handle_exception(request, last_succesfull_row, result)
            # If the request has succeeded upon retry, print a success message
            else:
                print(f"Retry succeeded for LSR {last_succesfull_row}")
        return combined_results
        ...
    ...

    # * - Documented
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
        required_keys_prices = ['drug_id', 'drug_name', 'qty',
                                'pharmacy_id', 'pharmacy_name', 'type', 'price']
        required_keys_adj = ['drug_id', 'drug_name',
                             'qty', 'pharmacy_id', 'group_id', 'bin', 'pcn']

        if self.data_type == 'prices' and not all(key in match_dict for key in required_keys_prices):
            raise ValueError(
                "match_dict is missing one or more required keys for 'prices' data type")
        elif self.data_type == 'adj' and not all(key in match_dict for key in required_keys_adj):
            raise ValueError(
                "match_dict is missing one or more required keys for 'adj' data type")

        # Depending on the data type, run the corresponding function
        if self.data_type == 'prices':            # if self.data_type == 'prices':
            temp_pharmacy_id = data['pharmacy_id'].fillna(0).astype(int)
            temp_coupon_price = pd.to_numeric(data['price'], errors='coerce')
            # Match rows where 'pharmacy_id' is not 0
            matching_rows = data[
                pd.notna(temp_pharmacy_id) &  # Checks for non-missing values
                (temp_pharmacy_id != 0) &  # Excludes rows where pharmacy_id is 0
                (data['drug_id'] == match_dict['drug_id']) &
                (data['drug_name'] == match_dict['drug_name']) &
                (data['qty'] == match_dict['qty']) &
                (temp_pharmacy_id == match_dict['pharmacy_id']) &
                (data['pharmacy_name'] == match_dict['pharmacy_name']) &
                (data['type'] == match_dict['type']) &
                (temp_coupon_price == match_dict['price'])
            ]
        elif self.data_type == 'adj':
            # Match rows where 'pharmacy_id' is not 0
            matching_rows = data[
                # Excludes rows where pharmacy_id is 0
                (data['pharmacy_id'] != 0) &
                (data['drug_id'] == match_dict['drug_id']) &
                (data['drug_name'] == match_dict['drug_name']) &
                (data['qty'] == match_dict['qty']) &
                (data['pharmacy_id'] == match_dict['pharmacy_id']) &
                (data['group_id'] == match_dict['group_id']) &
                (data['bin'] == match_dict['bin']) &
                (data['pcn'] == match_dict['pcn'])
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

# * - Documented
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

# * - Documented
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
            failed_req_dict = combined_request['requests']

            # Prepare tasks from failed requests
            tasks = self._prepare_tasks(failed_req_dict)

            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results and combine them
            combined_results = self._handle_results(
                last_succesfull_row, failed_req_dict, results)

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
        print(*request)
        print(f"Retry failed for LSR {last_succesfull_row}, error: {result}")

    def _get_tasks_builder(self):
        if self.data_type == 'prices':
            return lambda failed_req_dict: [get_prices_httpx(int(drug_id), int(qty), drug_name) for drug_id, qty, drug_name in failed_req_dict]
        else:
            return lambda failed_req_dict: [coupon_query_httpx(int(drug_id), int(qty), int(pharmacy_id), drug_name) for drug_id, qty, pharmacy_id, drug_name in failed_req_dict]
        ...
    ...


# * - Documented


    def write_to_csv_async(self):
        """
        Writes the object's 'data' attribute to a CSV file.

        The file is stored in a 'results' directory, within a subdirectory named 'drug_{self.data_type}'. 
        The filename is generated using the '_construct_filename' method.
        If the file does not already exist or is empty, the DataFrame is written to the file along with the column headers.
        If the file does exist and is not empty, the DataFrame is appended to the file, but the column headers are not included.
        """
        folder = f'drug_{self.data_type}'
        df = pd.DataFrame(self.data)

        # Create a directory named 'results' if it does not already exist.
        os.makedirs(f'results/{folder}', exist_ok=True)

        filename = self._construct_filename()

        # Construct the full path to the file.
        file_path = os.path.join(f'results/{folder}', filename)

        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            df.to_csv(file_path, mode='a', index=False)
        else:
            df.to_csv(file_path, mode='a', index=False, header=False)
        ...
    ...

    def format(self):
        # fuction to format the prices csv file to change the type of pharmacy_id col to interger
        df = pd.read_csv(self.adj_file_path)
        # df = pd.read_csv('results/drug_prices/all_drug_prices.csv', dtype={'pharmacy_id': 'Int64'})

        #  Convert missing values in 'pharmacy_id' to NaN
        # df['pharmacy_id'] = df['pharmacy_id'].fillna(pd.NA)

        # Convert 'pharmacy_id' to integer type, while keeping NaN values as is
        # df['pharmacy_id'] = df['pharmacy_id'].astype('Int64')
        #
        # Convert non-numeric values in 'coupon_price' to NaN and convert the column to float
        # df['coupon_price'] = pd.to_numeric(df['coupon_price'], errors='coerce')

        # df.to_csv('results/drug_prices/all_drug_prices.csv', index=False)

        print(df.dtypes)
        print(df.head())
        # code to change the coupon price type to int
        # df.to_csv('results/drug_adjucations/all_drug_adjucations.csv', index=False)
        # df = pd.read_csv('results/drug_adjucations/all_drug_adjucations.csv')

        # # Code to replace all cells that are 0 in pharmacy_id with empty string
        # df = pd.read_csv('results/drug_adjucations/all_drug_adjucations.csv')
        # df.to_csv('results/drug_adjucations/all_drug_adjucations.csv', index=False)

        ...


failed_test = [
    {
        'last_success_row':
        {
            'drug_name': 'Acetaminophen PM',
            'drug_id': 37876,
            'qty': 40,
            'pharmacy_id': 1,
            'group_id': 'DR33',
            'bin': '015995',
            'pcn': 'GDC',
            # 'pharmacy_name': 'Walmart',
            'type': 'COUPON',
            # 'price': 9.21
        },
        'drug_name': 'Acetaminophen / Aspirin / Caffeine',
        'drug_id': 45021,
        'qty': 10,
        'pharmacy_id': 83286,
        'type': 'COUPON'

    },
    {
        'last_success_row':
        {
            'drug_name': 'Acetaminophen PM',
            'drug_id': 37876,
            'qty': 40,
            'pharmacy_id': 1,
            'group_id': 'DR33',
            'bin': '015995',
            'pcn': 'GDC',
            # 'pharmacy_name': 'Walmart',
            'type': 'COUPON',
            # 'price': 9.21
        },
        'drug_name': 'Acetaminophen / Aspirin / Caffeine',
        'drug_id': 45021,
        'qty': 24,
        'pharmacy_id': 85327,
        'type': 'COUPON'

    },
    {
        'last_success_row':
        {
            'drug_name': 'Acetaminophen PM',
            'drug_id': 37876,
            'qty': 40,
            'pharmacy_id': 1,
            'group_id': 'DR33',
            'bin': '015995',
            'pcn': 'GDC',
            # 'pharmacy_name': 'Walmart',
            'type': 'COUPON',
            # 'price': 9.21
        },
        'drug_name': 'Acetaminophen / Aspirin / Caffeine',
        'drug_id': 45021,
        'qty': 30,
        'pharmacy_id': 6,
        'type': 'COUPON'

    },
    {
        'last_success_row':
        {
            'drug_id': 45021,
            'drug_name': 'Acetaminophen / Aspirin / Caffeine',
            'qty': 40,
            'pharmacy_id': 31240,
            'group_id': 'DR33',
            'bin': '015995',
            'pcn': 'GDC',
            # 'pharmacy_name': 'Costco',
            'type': 'COUPON',
            # 'price': 16.99
        },
        'drug_name': 'Acetaminophen / Aspirin / Caffeine',
        'drug_id': 45021,
        'qty': 60,
        'pharmacy_id': 83286,
        'type': 'COUPON'
    }
]


price_scraper = PriceScraper()
# price_scraper.format()
# price_scraper.run_timer()
# price_scraper.get_drug_pharmacies()
price_scraper.run_async()
# asyncio.run(price_scraper.retry_failed_requests([33468, 33469, 33470, 33471, 33472, 33473, 33474, 33475, 33476, 33478, 33479, 33480, 33481, 33482, 33483, 33484, 33485, 33486, 33487, 33489]))
# price_scraper.run()
# price_scraper.get_restart_index('prices')
# price_scraper.get_data('adj')
# price_scraper.get_data('prices')
# asyncio.run(price_scraper.retry_failed_requests([({'drug_id': 41733, 'drug_name': 'Abbott Freestyle', 'qty': 30, 'pharmacy_id': 1, 'pharmacy_name': 'Walmart', 'coupon_price': 8.95}, 41733, 100, 'Abbott Freestyle')] , 'prices'))
# processed_failed_req = price_scraper.process_failed_requests([({'drug_id': 45359, 'drug_name': 'Etravirine', 'qty': 180, 'pharmacy_id': 31240, 'pharmacy_name': 'Costco', 'coupon_price': 3872.86}, 45358, 30, 'Etravirine')])

# i - Test for _find_matching_row_index for prices
# price_scraper._set_data_type('prices')
# df = price_scraper._load_dataframe()
# price_scraper._find_matching_row_index(df, {
#     'drug_id': 42521,
#     'drug_name': 'Abacavir / Lamivudine',
#     'qty': 30,
#     'pharmacy_id': 23357,
#     'pharmacy_name': 'Rite Aid',
#     'coupon_price': 69.6
# })


# price_scraper._set_data_type('adj')
# price_scraper.set_failed_requests(failed_test)
# processed_failed_req = price_scraper.process_failed_requests()
# pp(processed_failed_req)
# print(len(processed_failed_req))
# asyncio.run(price_scraper.retry_failed_requests(processed_failed_req))


def main():
    # drug_scraper = DrugScraper()
    # drug_scraper.run()

    print('[+] Drug Info ✅')
    print('[+] Drug Combos ✅')

    price_scraper = PriceScraper()
    price_scraper.run()

    print('[+] Drug Prices ✅')
    print('[+] Drug Adjudacations ✅')

# main()


# function to read all_drug_prices and return the len of the df
def get_len():
    df = pd.read_csv('results/drug_prices/all_drug_prices.csv')
    return len(df)
    ...


# print(get_len())
