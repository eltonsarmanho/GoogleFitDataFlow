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
#print(data_sources)
#DATA_SOURCE = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

DATA_SOURCE = {
    "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
    "estimated_steps":'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
    "bpm": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
    "rhr": "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm",
    "sleep" :'derived:com.google.sleep.segment:com.google.android.gms:merged',
    'cal':'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
    'oxygen_saturation':'derived:com.google.oxygen_saturation.summary:com.google.android.gms:merged'
}
for key, value in DATA_SOURCE.items():
    zepp_data = fitness_service.users().dataSources(). \
        datasets(). \
        get(userId='me', dataSourceId=value,
            datasetId='1676170800000000000-1676257199000000000'). \
        execute()
    print(zepp_data)
