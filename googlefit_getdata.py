import argparse
import os
import time
from datetime import datetime, timedelta

import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.nutrition.read",
    "https://www.googleapis.com/auth/fitness.sleep.read"
]


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
    credentials.refresh(http)  # 認証トークンを更新する。
    apiclient = build("fitness", "v1", http=http)
    return apiclient


def get_google_fitness_info(
    apiclient: any, start_time: datetime, end_time: datetime
) -> dict:
    """Get daily data by requesting a query to GoogleFitAPI.

    Args:
        apiclient (any): Authenticated API client
        start_time (datetime): Data acquisition start date
        end_time (datetime): Data acquisition end date

    Returns:
        dict: get results
    """

    # Convert date to milliseconds。
    start_unix_time_millis: int = int(time.mktime(start_time.timetuple()) * 1000)
    end_unix_time_millis: int = int(time.mktime(end_time.timetuple()) * 1000)
    request_body = {
        "aggregateBy": [
            {
                "dataTypeName": "com.google.oxygen_saturation.summary",
            },
            {
                "dataTypeName": "com.google.activity.summary",
            },
            {
                "dataTypeName": "com.google.sleep.segment",  # Sleep
            },
            {
                "dataTypeName": "com.google.distance.delta",  # Moving distance
            },
            {
                "dataTypeName": "com.google.step_count.delta",  # number of steps
            },
            {
                "dataTypeName": "com.google.calories.expended",  # calories burned
            },
            {
                "dataTypeName": "com.google.heart_minutes",  # vigorous exercise
            },
        ],
        "bucketByTime": {  #A unit for aggregating data. 1 day for this example
            "durationMillis": end_unix_time_millis - start_unix_time_millis
        },
        "startTimeMillis": start_unix_time_millis,
        "endTimeMillis": end_unix_time_millis,
    }

    return (
        (
            apiclient.users()
            .dataset()
            .aggregate(userId="me", body=request_body)
            .execute()
        )
        .get("bucket")[0]
        .get("dataset")
    )


def main(credential_path: str, target_date_before: int = 1) -> None:
    """Receive data from GoogleFit and send data to GooglePubSub

    Args:
        credential_path (str): _description_
        publisher (_type_): _description_
    """

    if not os.path.exists(credential_path):  # Authenticate if no credentials exist
        print("OAuth2 authentication is performed because the credentials file does not exist.")
        oauth2(credential_path)
    apiclient = create_apiclient(credential_path=credential_path)

    # set date
    yesterday: datetime = datetime.today() - timedelta(days=target_date_before)
    start_time: datetime = datetime(
        yesterday.year, yesterday.month, yesterday.day, 0, 0, 0
    )
    end_time: datetime = datetime(
        yesterday.year, yesterday.month, yesterday.day, 23, 59, 59
    )

    dataset = get_google_fitness_info(apiclient, start_time, end_time)
    print(dataset)
    #print(f"Distance traveled today: {dataset[0].get('point')[0].get('value')[0].get('fpVal')} m")
    #print(f"today's steps: {dataset[1].get('point')[0].get('value')[0].get('intVal')} passos")
    #print(f"today's calorie consumption: {dataset[2].get('point')[0].get('value')[0].get('fpVal')} kcal")
    #print(f"vigorous exercise today: {dataset[3].get('point')[0].get('value')[0].get('fpVal')} point")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--credential_path",
        help="Google credential key path",
        default="./secret/credentials",
    )
    args = parser.parse_args()

    main(args.credential_path, target_date_before=5)
