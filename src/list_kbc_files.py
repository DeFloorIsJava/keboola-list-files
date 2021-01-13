"""
This Python app uses the Keboola Api to fetch a list of files in storage
The app first obtains the storage API token from the congig.json file.
It then uses a limit and offset to get paginated results from the API.
These results are concatenated and then saved to a resulting CSV file
Author: Adam Bako
"""

import json
import logging
import requests
import pandas as pd

# Pagination limit for the API
LIMIT = 10

# Url of the API
URL = 'https://connection.eu-central-1.keboola.com/v2/storage/files?'

CONFIG_FILE = "config.json"
OUTPUT_PATH = "keboola_file_list.csv"

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


def get_all_kbc_files(api_header):
    """Continuously calls API to receive all data available

            Parameters:
            api_header (dict): Holds the storage API token

            Returns:
            api_responses (list): Holds a list of json responses
    """

    offset = 0
    api_responses = []

    log.info('Retrieving data from Keboola...')

    # Keep making API calls until the response is
    # empty or lower than the limit
    while True:
        success, response = get_kbc_files(api_header, offset)

        if not success:
            return api_responses

        api_responses.append(response.json())

        if is_file_list_exhausted(response, LIMIT):
            api_responses = [item for sublist in api_responses
                             for item in sublist]
            log.info('Data retrieved, a total of %s files listed',
                     len(api_responses))
            return api_responses

        # Increase the offset by the limit for the next API call
        offset += LIMIT


def is_file_list_exhausted(response, expected):
    """Checks if API response is the final response

            Parameters:
            response (list): Holds a list of data from json response

            Returns:
            (Bool): True is final response
    """
    return len(response.json()) < expected


def get_kbc_files(api_header, offset):
    """Retrieves data from API using offset pagination

        Parameters:
        api_header (dict): Holds the storage API token
        offset (int): the offset of the API call

        Returns:
        (Bool): True if request was successful
        response (Response): Holds data of the response
       """

    params = {"limit": LIMIT,
              "offset": str(offset),
              "showExpired": "true"}

    response = requests.get(URL, headers=api_header, params=params)

    if response.status_code != 200:
        log.warning(response.text)
        return False, response

    return True, response


def save_kbc_files_as_csv(res_df, output_path):
    """Saves list of dictionaries to csv

            Parameters:
            res_df (list): Holds a list of data in dicts
            output_path (str): the path to save the file to
           """

    log.info('Saving list of files to %s', output_path)
    res_df.to_csv(output_path, index=False)


def postprocess_responses(api_responses):
    """Post-processes the final dataframe to desired output

        Parameters:
        api_responses (list): Holds a list of data in dicts

        Returns:
        res_df (Dataframe):
       """

    # Make a dataframe from the list of dictionaries
    res_df = pd.DataFrame(api_responses)

    if 'creatorToken' in res_df.columns:
        # Flatten the creator_tokens dict within the dataframe and add prefix
        creator_tokens = pd.DataFrame(res_df['creatorToken'].values.tolist(),
                                      index=res_df.index)
        creator_tokens = creator_tokens.add_prefix('creatorToken_')
        res_df = pd.concat([res_df, creator_tokens], axis=1)
        res_df = res_df.drop('creatorToken', axis=1)
    return res_df


if __name__ == '__main__':
    with open(CONFIG_FILE) as f:
        headers = json.load(f)

    responses = get_all_kbc_files(headers)

    if responses:
        responses_df = postprocess_responses(responses)
        save_kbc_files_as_csv(responses_df, OUTPUT_PATH)
        log.info('File saved correctly')
