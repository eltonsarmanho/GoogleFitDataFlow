import json
import requests

api_url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

access_token = "ya29.a0AeTM1id_VvDL6TP8upEkXaf_aMNzRRrTmI3dXSXKJIcWyRIPvcY9GGHMjhaJVIbxR1GleAiIsPFanbqK2gMFp2OjNXu7gCN_NcfAFMNEkDoggnu7DCaPO_ssqAgvT-00me7ZVYN68GqQCuZlvTsr4PW_8c9ZaCgYKARISARISFQHWtWOmmPmjwuqVnQjtjwIFyBWYpw0163"
headers = {
  "Authorization": "Bearer {}".format(access_token),
  "Content-Type": "application/json;encoding=utf-8"
  }

body = {
  "aggregateBy": [{
    "dataTypeName": "com.google.heart_rate.bpm",
  },{
    "dataTypeName": "com.google.sleep.segment",
  }],
  "bucketByTime": { "durationMillis": 86400000 },
  "startTimeMillis": 1669345200000,
  "endTimeMillis": 1669690800000
}


response = requests.post(api_url, data=json.dumps(body), headers=headers)

print(response.text)