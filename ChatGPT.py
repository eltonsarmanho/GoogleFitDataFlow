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
DATA_SOURCE = 'raw:com.google.sleep.segment:com.xiaomi.hm.health:GoogleFitSyncHelper- sleep segments'
zepp_data = fitness_service.users().dataSources(). \
    datasets(). \
    get(userId='me', dataSourceId=DATA_SOURCE,
        datasetId='1675393200000-1677639599000'). \
    execute()

print(zepp_data)