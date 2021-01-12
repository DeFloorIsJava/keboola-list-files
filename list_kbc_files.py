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

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


def get_kbc_files(api_header):
    """Retrieves data from API using offset pagination

        Parameters:
        api_header (dict): Holds the storage API token

        Returns:
        api_responses (list): Holds a list of json responses

       """
    offset = 0
    api_responses = []

    log.info('Retrieving data from Keboola...')

    while True:
        # Keep making API calls until the response is
        # empty or lower than the limit

        params = {"limit": "10",
                  "offset": str(offset),
                  "showExpired": "true"}

        response = requests.get(URL, headers=api_header, params=params)

        if response.status_code != 200:
            log.info(response.text)
            return False

        api_responses = api_responses + response.json()

        # increase the offset by the limit for the next API call
        offset += LIMIT

        if len(response.json()) < LIMIT:
            num_files = len(api_responses)
            log.info('Data retrieved, a total of %s files listed', num_files)
            return api_responses


def save_kbc_files(api_responses):
    """Saves list of dictionaries to csv

        Parameters:
        api_responses (list): Holds a list of json responses

       """
    # Make a dataframe from the list of dictionaries
    res_df = pd.DataFrame(api_responses)

    # Flatten the creator_tokens dict within the dataframe and add prefix
    creator_tokens = pd.DataFrame(res_df['creatorToken'].values.tolist(),
                                  index=res_df.index)
    creator_tokens = creator_tokens.add_prefix('creatorToken_')
    res_df = pd.concat([res_df, creator_tokens], axis=1)
    res_df = res_df.drop('creatorToken', axis=1)

    # Save dataframe to csv
    path = "keboola_file_list.csv"
    log.info('Saving list of files to %s', path)
    res_df.to_csv(path, index=False)


if __name__ == '__main__':
    with open('config.json') as f:
        headers = json.load(f)

    responses = get_kbc_files(headers)

    if responses:
        save_kbc_files(responses)
