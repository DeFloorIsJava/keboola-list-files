# keboola-list-files
This Python app uses the Keboola Api to fetch a list of files in storage

The app first obtains the storage API token from the congig.json file. It then uses a limit and offset to get paginated results from the API. These results are concatenated and then saved to a resulting CSV file.

## Use

Add the necessary X-StorageApi-Token to the config.json file
`
{
  "X-StorageApi-Token" : "your_storage_token_here"
}
`
Run the code : 

`
python list_kbc_files.py
`
