import argparse
import os
import time
from datetime import datetime, timedelta

import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.nutrition.read",
]


def oauth2(credential_path: str):
    """Autenticacao
    Args:
        credential_path (str):
    """
    flow = flow_from_clientsecrets(
        #
        "./key/secret.json",
        #
        scope=OAUTH_SCOPE,
        #
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    authorize_url = flow.step1_get_authorize_url()
    print("Autorizado....")
    print(authorize_url)

    code = input("Codeを入力してください: ").strip()
    credentials = flow.step2_exchange(code)

    if not os.path.exists(credential_path):
        Storage(credential_path).put(credentials)


def create_apiclient(credential_path: str) -> any:
    """tokenファイルを読み込みapiclientを作成する。

    Args:
        credential_path (str): tokenファイルのパス。

    Returns:
         googleapiclient.discovery.Resource: GoogleFitAPIにリクエストするクライアント。
    """
    if os.path.exists(credential_path):
        credentials = Storage(credential_path).get()
    else:
        print("tokenが存在しません。")

    http = httplib2.Http()
    http = credentials.authorize(http)
    credentials.refresh(http)  # 認証トークンを更新する。
    apiclient = build("fitness", "v1", http=http)
    return apiclient


def get_google_fitness_info(
    apiclient: any, start_time: datetime, end_time: datetime
) -> dict:
    """クエリをGoogleFitAPIにリクエストして1日毎のデータを取得する。

    Args:
        apiclient (any): 認証済みのAPIクライアント
        start_time (datetime): データ取得の開始日
        end_time (datetime): データ取得の終了日

    Returns:
        dict: 取得結果。
    """

    # 日付をミリ秒に変換する。
    start_unix_time_millis: int = int(time.mktime(start_time.timetuple()) * 1000)
    end_unix_time_millis: int = int(time.mktime(end_time.timetuple()) * 1000)
    request_body = {
        "aggregateBy": [
            {
                "dataTypeName": "com.google.distance.delta",  # 移動距離
            },
            {
                "dataTypeName": "com.google.step_count.delta",  # 歩数
            },
            {
                "dataTypeName": "com.google.calories.expended",  # 消費カロリー
            },
            {
                "dataTypeName": "com.google.heart_minutes",  # 強めの運動
            },
        ],
        "bucketByTime": {  # データを集約する単位。この例の場合は1日
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
    """GoogleFitからデータを受信しGooglePubSubにデータを送信する

    Args:
        credential_path (str): _description_
        publisher (_type_): _description_
    """

    if not os.path.exists(credential_path):  # クレデンシャルが存在しない場合認証を行う。
        print("クレデンシャルファイルが存在しないので、OAuth2認証を行います。")
        oauth2(credential_path)
    apiclient = create_apiclient(credential_path=credential_path)

    # 日付を設定
    yesterday: datetime = datetime.today() - timedelta(days=target_date_before)
    start_time: datetime = datetime(
        yesterday.year, yesterday.month, yesterday.day, 0, 0, 0
    )
    end_time: datetime = datetime(
        yesterday.year, yesterday.month, yesterday.day, 23, 59, 59
    )

    dataset = get_google_fitness_info(apiclient, start_time, end_time)
    print(f"今日の移動距離: {dataset[0].get('point')[0].get('value')[0].get('fpVal')} m")
    print(f"今日の歩数: {dataset[1].get('point')[0].get('value')[0].get('intVal')} 歩")
    print(f"今日の消費カロリー: {dataset[2].get('point')[0].get('value')[0].get('fpVal')} kcal")
    print(f"今日の強めの運動: {dataset[3].get('point')[0].get('value')[0].get('fpVal')} point")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--credential_path",
        help="Googleのクレデンシャルキーのパス",
        default="./key/credentials",
    )
    args = parser.parse_args()

    main(args.credential_path, target_date_before=1)
