# keboola-list-files
This Python app uses the Keboola Api to fetch a list of files in storage

The app first obtains the storage API token from the config.json file. It then uses a limit and offset to get paginated results from the API. These results are concatenated and then saved to a resulting CSV file : keboola_file_list.csv .

## Functionality 
- Performs a series of GET requests to https://connection.eu-central-1.keboola.com/v2/storage/files 
- Parses the JSON responses and stores the result as a CSV file.


## Use

Add the necessary X-StorageApi-Token to the config.json file<br/><br/>
`
{
  "X-StorageApi-Token" : "your_storage_token_here"
}
`<br/><br/>
Build the docker image : <br/>

`
docker build -t keboola-list-files .
`<br/>

Run the docker image : <br/>

`
docker run keboola-list-files 
`<br/><br/>

To view the csv file I used :<br/>

`
docker run --rm -it --entrypoint=/bin/bash keboola-list-files
`<br/>`
python list_kbc_files.py
`<br/>`
cat keboola_file_list.csv
`
<br/>
