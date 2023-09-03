import re
import pandas as pd
from os import system, name
import os
import glob
from functools import wraps
from time import sleep

from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError, RequestException, ConnectTimeout, ReadTimeout

def get_case_insensitive(dictionary, key):
    lower_case_dict = {k.lower(): v for k, v in dictionary.items()}
    return lower_case_dict.get(key.lower())

def clean_string(s):
    # Remove leading and trailing spaces
    s = s.strip()

    # Replace spaces and '/' with '-'
    s = s.replace(' ', '-').replace('/', '-')

    # Remove parentheses
    s = s.replace('(', '').replace(')', '')

    # Remove multiple hyphens and ensure no hyphen at the end
    s = re.sub('-+', '-', s)  # replace multiple '-' with single '-'
    s = re.sub('-+$', '', s)  # remove '-' at the end

    return s

def join_info_files(directory):
    # Get a list of all CSV files in the specified directory
    csv_files = glob.glob(os.path.join(directory, '*.csv'))

    # Create a list to hold DataFrame objects
    df_list = []

    # Loop through the list of CSV files and read each one into a DataFrame
    for file in csv_files:
        df = pd.read_csv(file)
        df_list.append(df)

    # Concatenate all DataFrame objects in the list
    all_data = pd.concat(df_list, ignore_index=True)
    all_data.to_csv('all_drug_infos.csv', index=False)
    return all_data

def clear(remote):
    if remote:
        return
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def retry_on_exception(num_retries=3, delay=5, backoff=2, exceptions=(RequestException,)):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                mdelay = delay
                for _ in range(num_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        print(f"{str(e)} - Retrying in {mdelay} seconds...")
                        sleep(mdelay)
                        mdelay *= backoff
                return func(*args, **kwargs)
            return wrapper
        return decorator
        ...
...

# Use the decorator on a function that always raises an exception
@retry_on_exception(num_retries=3, delay=1, backoff=2, exceptions=(ZeroDivisionError,))
def always_fails():
    return 1 / 0  # This will raise a ZeroDivisionError


def try_convert_to_numeric(value):
    try:
        return pd.to_numeric(value)
    except ValueError:
        return value

# always_fails()
# print(clean_string('Aspirin / Citric Acid / Sodium Bicarbonate'))
# print(clean_string('Aurovela 24 FE'))
# print(clean_string('Bupropion (Zyban)'))
# print(clean_string('Blisovi FE 1.5 / 30'))
# print(clean_string('B & O Supprettes'))
# print(clean_string('Dextromethorphan / Guaifenesin / Phenylephrine'))
