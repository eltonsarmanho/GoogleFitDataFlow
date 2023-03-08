from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from oauth2client.file import Storage
import os
import httplib2
import time
from datetime import datetime, timedelta
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage



OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.nutrition.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.heart_rate.read"
]
DATA_SOURCE = {
    #"steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
    #"estimated_steps":'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
    "bpm": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
    #"rhr": "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm",
    "sleep" :'derived:com.google.sleep.segment:com.google.android.gms:merged',
    #'cal':'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
    #'BMR':'raw:com.google.weight:com.xiaomi.hm.health:GoogleFitSyncHelper - weight',
    #'activities':'derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments'
}

def oauth2(credential_path: str):
    """Autenticacao
    Args:
        credential_path (str):
    """
    flow = flow_from_clientsecrets(
        #
        "./secret/client_secrets.json",
        #
        scope=OAUTH_SCOPE,
        #
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    authorize_url = flow.step1_get_authorize_url()
    print("Autorizado....")
    print(authorize_url)

    code = input("Code: ").strip()
    credentials = flow.step2_exchange(code)

    if not os.path.exists(credential_path):
        Storage(credential_path).put(credentials)

def oauth2(credential_path: str):
    """Autenticacao
    Args:
        credential_path (str):
    """
    flow = flow_from_clientsecrets(
        #
        "./secret/client_secrets.json",
        #
        scope=OAUTH_SCOPE,
        #
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    authorize_url = flow.step1_get_authorize_url()
    print("Autorizado....")
    print(authorize_url)

    code = input("Code: ").strip()
    credentials = flow.step2_exchange(code)

    if not os.path.exists(credential_path):
        Storage(credential_path).put(credentials)

def create_apiclient(credential_path: str) -> any:
    """token

    Args:
        credential_path (str): token

    Returns:
         googleapiclient.discovery.Resource: GoogleFitAPI
    """
    if os.path.exists(credential_path):
        credentials = Storage(credential_path).get()
    else:
        print("token not found!")

    http = httplib2.Http()
    http = credentials.authorize(http)
    credentials.refresh(http)  # Atualize um token de autenticação.
    apiclient = build("fitness", "v1", http=http)
    return apiclient

def main(credential_path: str,target_date_before: int = 1) -> None:
    """Receive data from GoogleFit and send data to Flow Server

        Args:
            target_date_before (int): _description_

        """
    if not os.path.exists(credential_path):  # Authenticate if no credentials exist
        print("OAuth2 authentication is performed because the credentials file does not exist.")
        oauth2(credential_path)
    apiclient = create_apiclient(credential_path=credential_path)


    data_sources = apiclient.users().dataSources().list(userId='me').execute()


    TODAY: datetime = datetime.today() - timedelta(days=target_date_before)
    STARTDAY: datetime = datetime(
            TODAY.year, TODAY.month, TODAY.day, 0, 0, 0
        )
    NEXTDAY: datetime = datetime(
            TODAY.year, TODAY.month, TODAY.day, 23, 59, 59
        )
    NOW = datetime.today()

    START = int(time.mktime(STARTDAY.timetuple()) * 1000000000)
    NEXT = int(time.mktime(NEXTDAY.timetuple()) * 1000000000)
    END = int(time.mktime(NOW.timetuple()) * 1000000000)

    while True:

                data_set = "%s-%s" % (START, NEXT)
                print(data_set)
                time_data_set = "%s-%s" % (datetime.fromtimestamp(START / 1000000000.0), datetime.fromtimestamp(NEXT / 1000000000.0))
                print(time_data_set)
                if END < NEXT:
                    break
                for key, value in DATA_SOURCE.items():
                    zepp_data = apiclient.users().dataSources(). \
                        datasets(). \
                        get(userId='me', dataSourceId=value,
                            datasetId=data_set). \
                        execute()
                    print(key)
                    if(key == 'bpm'):
                        for point in zepp_data["point"]:
                                if int(point["startTimeNanos"]) > START:
                                    print(f"Heart Rate:     {point['value'][0]['fpVal']} bpm")
                    if (key == 'sleep'):
                            for point in zepp_data["point"]:
                                if int(point["startTimeNanos"]) > START:
                                    print(f"Sleep Value:     {point['value'][0]['intVal']} value")

                    print("\n")

                STARTDAY = STARTDAY + timedelta(days=1)
                NEXTDAY = NEXTDAY + timedelta(days=1)
                START = int(time.mktime(STARTDAY.timetuple()) * 1000000000)
                NEXT = int(time.mktime(NEXTDAY.timetuple()) * 1000000000)


if __name__ == '__main__':
    CREDENTIALS_FILE = "./secret/credentials"
    credentials = ""
    main(credential_path=CREDENTIALS_FILE,target_date_before=25)
