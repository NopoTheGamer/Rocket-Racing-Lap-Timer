import requests
import json

webhook_url = "http://localhost:6942/webhook"


def send_webhook(data_to_send):
    headers = {'Content-Type': 'application/json'}

    response = requests.post(webhook_url, data=json.dumps(data_to_send), headers=headers)

    print("Response:", response.text)


send_webhook({
    "total": "value1",
    "key2": "value2"
})
