
import requests

def get_history():

    r = requests.get('https://api-mifit-de2.huami.com/v1/sport/run/history.json', headers={
        'apptoken': token,
        "appPlatform": APP_PLATFORM,
        "appname": APP_NAME,
    })
    r.raise_for_status()

    return r.json()

def get_detail(track_id, source):
    r = requests.get('https://api-mifit.huami.com/v1/sport/run/detail.json', headers={
        'apptoken': token,
        "appPlatform": APP_PLATFORM,
        "appname": APP_NAME,
    }, params={
        'trackid': track_id,
        'source': source,
    })
    r.raise_for_status()

    return r.json()
if __name__ == '__main__':
    APP_NAME = "com.xiaomi.hm.health"
    APP_PLATFORM = "web"
    token = "UQVBQEJyQktGXip6SltGImp2ej48BAAEAAAAAjgkSTzczBFJs2vysA_qqopPWVSyTCsdNCjfNQIAfgXiO6rgu-eEbkIVc66hRRTWdSh4pKe_7es3GxsT6OwGQ1LzjrJmeDKvrYhLZrt2yF9ojfXyKB6fzyUkVfuCfPUMT9HkSMK8IJqT7jgcmJP68zRa_ci-fF4avx1PzyRZZibQpCZV8-8cKeAKvwY7rtD4w"
    #print(get_history())
    print(get_detail('1673992911', 'run.263.huami.com'))