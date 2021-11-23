import requests


def POST(data):
    URL = "http://130.240.200.37:1337/"

    req = requests.post(url = URL, data = data)
    responseText = req.text
    print("POST - " + responseText)