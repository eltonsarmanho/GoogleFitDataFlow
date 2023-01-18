
import requests

def get_history():
    print(token)

    r = requests.get('https://api-mifit.huami.com/v1/sport/run/history.json', headers={
        'apptoken': token,
        "appPlatform": APP_PLATFORM,
        "appname": APP_NAME,
    },)
    r.raise_for_status()

    return r.json()

def get_detail(track_id, source):
    r = requests.get('https://api-mifit-de2.huami.com/v1/sport/run/detail.json', headers={
        'apptoken': token
    }, params={
        'trackid': track_id,
        'source': source,
    })
    r.raise_for_status()

    return r.json()
if __name__ == '__main__':
    APP_NAME = "com.xiaomi.hm.health"
    APP_PLATFORM = "web"
    token = "UQVBQEJyQktGXip6SltGImp2ej48BAAEAAAAAV5hrus-9WYRhpygu5CZ2EWLS10eLQa98pAH-wnzOlbHbgXq7btJSOjlzME23NIJelcoiV_8g43NcgdM8djb2vjxx1ggdpJ8hL4LUdkXIB-vqxbl-NBBhXkXuApMPijYK0lwNhWbKjgZyVLv6tluyVk4QJWqqeITuUTonsIL-axAbUAbDTrkmpLgHXRX6BrfV"
    print(get_history())