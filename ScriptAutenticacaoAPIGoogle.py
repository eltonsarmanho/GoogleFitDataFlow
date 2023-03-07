
import os
import json
import httplib2
import numpy as np
import requests

import time
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.file import Storage

#OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.heart_rate.read'
OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.nutrition.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.heart_rate.read"
]
DATA_SOURCE = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CREDENTIALS_FILE = "./secret/credentials"

def auth_data():

    credentials = ""

    if os.path.exists(CREDENTIALS_FILE):
        credentials = Storage(CREDENTIALS_FILE).get()
    else:
        # flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
        flow = flow_from_clientsecrets(
            # Specify the JSON file for OAuth acquired when API is enabled
            './secret/client_secrets.json',
            # Specify the scope
            scope=OAUTH_SCOPE,
            # Specify the token receiving method after user authentication (described later)
            redirect_uri=REDIRECT_URI)

        authorize_url = flow.step1_get_authorize_url()
        print('Please start the following URL in your browser.')
        print(authorize_url)

        code = input('Please enter Code: ').strip()
        credentials = flow.step2_exchange(code)

        if not os.path.exists(CREDENTIALS_FILE):
            Storage(CREDENTIALS_FILE).put(credentials)

        # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service


def retrieve_data(fitness_service, dataset):

    return fitness_service.users().dataSources(). \
        datasets(). \
        get(userId='me', dataSourceId=DATA_SOURCE, datasetId=dataset,). \
        execute()


def nanoseconds(nanotime):
    """
Convert to nanoseconds
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def logwrite(date, step):
    with open('./data/step.log', 'a') as outfile:
        outfile.write(str(date) + "," + str(step) + "\n")


if __name__ == "__main__":

    authdata = auth_data()

    #Get the data for the previous day
    TODAY = datetime.today() - timedelta(days=30)
    STARTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 0, 0, 0)
    NEXTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)
    NOW = datetime.today()

    START = int(time.mktime(STARTDAY.timetuple())*1000000000)
    NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
    END = int(time.mktime(NOW.timetuple())*1000000000)

    data_set = "%s-%s" % (START, NEXT)

    while True:
        print(data_set)
        data_set_data = "%s-%s" % (datetime.fromtimestamp(START / 1000000000.0), datetime.fromtimestamp(NEXT / 1000000000.0))
        print(data_set_data)

        if END < NEXT:
            break

        dataset = retrieve_data(authdata, data_set)

        starts = []
        ends = []
        values = []
        #print(type(dataset))
        #print(dataset)

        for point in dataset["point"]:
              if int(point["startTimeNanos"]) > START:
                 starts.append(int(point["startTimeNanos"]))
                 ends.append(int(point["endTimeNanos"]))
                 values.append(point['value'][0]['fpVal'])
        #
        if(starts is not None):
            print("From: {}".format(nanoseconds(min(starts))))
            print("To: {}".format(nanoseconds(max(ends))))
            print("Mean HR:{}".format(np.mean(values)))
        #
        # step = np.mean(values)
        #
        # startdate = STARTDAY.date()
        # logwrite(startdate, step)

        STARTDAY = STARTDAY + timedelta(days=1)
        NEXTDAY = NEXTDAY + timedelta(days=1)
        START = int(time.mktime(STARTDAY.timetuple())*1000000000)
        NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
        data_set = "%s-%s" % (START, NEXT)

        time.sleep(2)