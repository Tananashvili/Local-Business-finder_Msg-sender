import requests
import json

def send_msg(receiver, text):
  url = "https://graph.facebook.com/v17.0/106231419099043/messages"

  payload = json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": f"{receiver}",
    "type": "text",
    "text": {
      "preview_url": False,
      "body": text
    }
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer EAAKmzOcRo6wBO0Dcv9aJ7qTwEABurJx8BQWUC5cDT9XZCHPFhD5u7ZC5hdyEJhu7YgToyO9hDxO1O9TNXeoPGFOyeb78eHvvgjOCuC3pQK5e8QXvyp0GUvAnPFp3osPR3vbUqImep6IKZA5pWXowRwlksKUZACNCkdbH9cERxu8BLXiWlwk7ZBH3umwMTJG8z'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)
