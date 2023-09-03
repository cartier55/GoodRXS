import logging
import shutil
import os
import uuid
import json
import pandas as pd


class Logger:

    def __init__(self, scraper_phase):
        """
        Initializes the logger.

        Parameters:
        scraper_phase (str): The phase of the scraping process.
        """
        self.phase = scraper_phase
        self.log_file = f'logs/{scraper_phase}_log.log'
        self.prev_log_file = f'logs/{scraper_phase}_log_prev.log'
        self._cleanup_log_file()

        self.logger = logging.getLogger(f'{__name__}_{str(uuid.uuid4())}')
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _cleanup_log_file(self):
        """
        Deletes the log file if it exists.
        """
        # If a _prev log exists from an even earlier session, remove it
        if os.path.exists(f'{self.prev_log_file}'):
            os.remove(f'{self.prev_log_file}')

        # If a log exists from the last session, rename it to _prev
        if os.path.exists(f'{self.log_file}'):
            shutil.move(f'{self.log_file}', f'{self.prev_log_file}')

    def log_message(self, level, message):
        """
        Logs the given message at the specified level.

        Parameters:
        level (str): The level of the log ('info', 'error', etc.).
        message (str): The log message.
        """
        if level.lower() == 'info':
            self.logger.info(message)
        elif level.lower() == 'error':
            self.logger.error(message)
        # You can add more elif statements here for other log levels like warning, debug, etc.

    def log(self, drug_name, drug_id):
        """
        Logs the given drug name and drug ID.

        Parameters:
        drug_name (str): The name of the drug.
        drug_id (int): The ID of the drug.
        """
        self.log_message(
            'info', f'Processing drug: {drug_name} with ID: {drug_id}')

    def log_failed_request(self, failed_request_info, error):
        """
        Logs the details of a failed request.

        Parameters:
        failed_request_info (dict): Dictionary containing details about the failed request.
            It should include 'last_success_row', 'drug_name', 'drug_id', 'qty', and 'error'. 
            It can optionally include 'pharmacy_id' and 'data_type'.
        """
        last_success_row = failed_request_info.get('last_success_row')
        drug_name = failed_request_info.get('drug_name')
        drug_id = failed_request_info.get('drug_id')
        qty = failed_request_info.get('qty')
        pharmacy_id = failed_request_info.get('pharmacy_id')
        
        if self.phase == 'info':
            self.log_message(
                'error', f'Request failed at row {last_success_row} for Drug: {drug_name}. Error: {error}')
            ...
        elif self.phase == 'combos':
            self.log_message(
                'error', f'Request failed at row {last_success_row} for Drug: {drug_name} with ID: {drug_id}. Error: {error}')
            ...
        elif self.phase == 'prices':
            self.log_message(
                'error', f'Request failed at row {last_success_row} for Drug: {drug_name} with ID: {drug_id}, Qty: {qty}, and Pharmacy ID: {pharmacy_id}. Error: {error}')
            ...
        elif self.phase == 'adj':
            self.log_message(
                'error', f'Request failed at row {last_success_row} for Drug: {drug_name} with ID: {drug_id}, Qty: {qty}, and Pharmacy ID: {pharmacy_id}. Error: {error}')
            ...

    def log_request_params(self, params):
        """
        Logs the request parameters.

        Parameters:
        params (dict): The request parameters.
        """
        # Convert NAType values to None
        params = {k: (v if pd.notna(v) else None) for k, v in params.items()}

        params_str = json.dumps(params)
        self.logger.info('Request parameters: %s', params_str)

    def get_last_request_params(self):
        """
        Returns the most recent request parameters logged in the previous log file.

        Returns:
        dict: The most recent request parameters, or None if no parameters were found.
        """
        prev_log_file = f'logs/{self.logger.handlers[0].baseFilename.rpartition("_log.log")[0]}_log_prev.log'

        # file_path = os.path.join(self.prev_log_file)

        if os.path.exists(self.prev_log_file):
            if self.check_scraping_complete(file_override=self.prev_log_file):
                return False
            with open(self.prev_log_file, 'r') as log_file:
                for line in reversed(list(log_file)):
                    if 'Request parameters:' in line:
                        params_str = line.partition('Request parameters: ')[2]
                        return json.loads(params_str)
        return None

    def check_scraping_complete(self, file_override=None):
        """
        Checks if the last log message indicates that the scraping process is complete.

        Returns:
        bool: True if the last log message indicates that the scraping process is complete, False otherwise.
        """
        with open(self.log_file if file_override == None else file_override, 'r') as log_file:
            # check if file is empty
            if os.stat(self.log_file if file_override == None else file_override).st_size == 0:
                return False
            last_line = list(log_file)[-1]
            return 'Scraping process completed.' in last_line

    def log_scraping_complete(self):
        """
        Logs a message indicating that the scraping process is complete.
        """
        self.log_message('info', 'Scraping process completed.')


# def get_latest_drug_info():
#     with open('log/app.log', 'r') as f:  # Change this line to include the "log" directory
#         logs = f.readlines()

#     if logs:
#         latest_log = logs[-1]
#         log_parts = latest_log.split("-")
#         message = log_parts[-1].strip()

#         if "Processing drug" in message:
#             drug_parts = message.split(":")
#             drug_name = drug_parts[1].split("with ID")[0].strip()
#             drug_id = drug_parts[2].strip()

#             return drug_name, drug_id

#     else:
#         return None, None

# latest_drug_name, latest_drug_id = get_latest_drug_info()
# print(f"Latest Drug Name: {latest_drug_name}")
# print(f"Latest Drug ID: {latest_drug_id}")
