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
import numpy as np


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
    "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
    #"estimated_steps":'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
    "bpm": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
    "rhr": "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm",
    "sleep" :'derived:com.google.sleep.segment:com.google.android.gms:merged',
    'cal':'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
    #'BMR':'raw:com.google.weight:com.xiaomi.hm.health:GoogleFitSyncHelper - weight',
    #'activities':'derived:com.google.activity.segment:com.google.android.gms:merge_activity_segments'
}

dict_sleep={
0 : "Unspecified",
1:  "Awake: usuário está acordado.",
2 : "Sleeping: Descrição do sono genérico.",
3 : "Out of bed: usuário sai da cama no meio de uma sessão de sono.",
4 : "Light sleep: Ciclo de sono Leve.",
5 : "Deep sleep: Ciclo de sono profundo.",
6 : "REM sleep: user is in a REM sleep cycle."
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
                #print(data_set)
                time_data_set = "%s-%s" % (datetime.fromtimestamp(START / 1000000000.0), datetime.fromtimestamp(NEXT / 1000000000.0))
                print("Relatório do dia %s" % datetime.fromtimestamp(START / 1000000000.0).strftime('%d-%m-%y'))
                if END < NEXT:
                    break
                for key, value in DATA_SOURCE.items():
                    zepp_data = apiclient.users().dataSources(). \
                        datasets(). \
                        get(userId='me', dataSourceId=value,
                            datasetId=data_set). \
                        execute()
                    if(key == 'bpm'):
                        lst_hrv = []
                        for point in zepp_data["point"]:
                                if int(point["startTimeNanos"]) > START:
                                    lst_hrv.append(point['value'][0]['fpVal'])
                        print(f"Heart Rate diário: {np.mean(lst_hrv).round(2)} bpm")

                    if (key == 'rhr'):
                        lst_hrv = []
                        for point in zepp_data["point"]:
                            if int(point["startTimeNanos"]) > START:
                                lst_hrv.append(point['value'][0]['fpVal'])
                        print(f"Heart Rate em repouso diário: {np.mean(lst_hrv).round(2)} bpm")

                    if (key == 'sleep'):
                            for point in zepp_data["point"]:
                                if int(point["startTimeNanos"]) > START:
                                    print(f"Ponto do Sono:   {dict_sleep.get(point['value'][0]['intVal'])} em  {datetime.fromtimestamp(int(point['startTimeNanos']) / 1000000000.0)}")

                    if(key=='cal'):
                        lst_cal = []
                        for point in zepp_data["point"]:
                            if int(point["startTimeNanos"]) > START:
                                lst_cal.append(point['value'][0]['fpVal'])
                        print(f"Gasto Calórico Médio Diário: {np.mean(lst_cal).round(2)} Kcal")
                        print(f"Gasto Calórico Total Diário: {np.sum(lst_cal).round(2)} Kcal")

                    if (key == 'steps'):
                        lst_steps = []
                        for point in zepp_data["point"]:
                            if int(point["startTimeNanos"]) > START:
                                #print(f"Sleep segment: {point['value'][0].get('intVal')} ")
                                lst_steps.append(point['value'][0]['intVal'])
                        print(f"Número de Passos Total Diário: {np.sum(lst_steps).round(2)} passos")
                        print(f"Número de Passos Médio Diário: {np.mean(lst_steps).round(2)} passos")

                print("\n")
                STARTDAY = STARTDAY + timedelta(days=1)
                NEXTDAY = NEXTDAY + timedelta(days=1)
                START = int(time.mktime(STARTDAY.timetuple()) * 1000000000)
                NEXT = int(time.mktime(NEXTDAY.timetuple()) * 1000000000)


if __name__ == '__main__':
    CREDENTIALS_FILE = "./secret/credentials"
    credentials = ""
    main(credential_path=CREDENTIALS_FILE,target_date_before=25)
