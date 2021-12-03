import json

from flask import Flask, redirect, url_for, request
import threading
from time import sleep
import requests
global app
app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.values.get("user")
      print(user)
      return {"data":user}
   else:
      #user = request.args.get('user')
      return {"data":"Nothing"}

def test():
    app.run(debug=True)

if __name__ == '__main__':
   thread = threading.Thread(target=app.run)
   thread.start()
   sleep(1)
   pload = {'user': 'Olivia', 'password': '123'}
   r = requests.post('http://127.0.0.1:5000/', data=pload)
   print(r.text)
