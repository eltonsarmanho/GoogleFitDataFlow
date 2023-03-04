from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from oauth2client.file import Storage
import os
import httplib2

CREDENTIALS_FILE = "./secret/credentials"
credentials = ""

if os.path.exists(CREDENTIALS_FILE):
    credentials = Storage(CREDENTIALS_FILE).get()

http = httplib2.Http()
http = credentials.authorize(http)

fitness_service = build('fitness', 'v1', http=http)

data_sources = fitness_service.users().dataSources().list(userId='me').execute()
print(data_sources)
DATA_SOURCE = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

DATA_SOURCE = 'derived:com.google.sleep.segment:com.google.android.gms:merged'
zepp_data = fitness_service.users().dataSources(). \
    datasets(). \
    get(userId='me', dataSourceId=DATA_SOURCE,
        datasetId='1676170800000000000-1676257199000000000'). \
    execute()

print(zepp_data)