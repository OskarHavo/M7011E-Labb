import time

import databaseFunctions
from windmill import *
from simulator import *
from threading import  Lock
import threading
import datetime
import json

## How to round time: https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object/10854034#10854034
def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

class Windmillhistory():
    ## Create a new windmill history generator. Default delta time is 60 seconds
    def __init__(self, simulator, timeDelta = 60*60*12):
        self.sim = simulator
        self.running = False
        self.mtx=Lock()
        self.delta =timeDelta
        return

    def run(self):
        while True:
            with self.mtx:
                if not self.running:
                    return
                timestamp = datetime.datetime.now() - datetime.timedelta(seconds=10)
                print ("Iterating through", len(self.sim.productionNodes), "nodes")
                for username in self.sim.productionNodes:
                    data = self.sim.productionNodes[username].client.getNext(timestamp)[0][0]
                    oldData = databaseFunctions.getHistoricalData(username)

                    if not oldData[0]:
                        oldData = {'history': []}
                    else:
                        oldData = json.loads(oldData[0].decode("utf-8"))
                    #        print("old data", d[0], "   ", type(old_data))
                    oldData['history'].append(data)

                    if len(oldData) > 10:
                        oldData = oldData[len(oldData)-10:]

                    old_data_string = str(oldData)
                    old_data_string = str.replace(old_data_string,"'","\"")
                    print("Old data:", old_data_string)
                    databaseFunctions.setHistoricalData(username,old_data_string)


                now = datetime.datetime.now()
                rounded = roundTime(now,self.delta)
                nextTime = rounded+datetime.timedelta(seconds=self.delta)

                print("next update will be at", str(nextTime), "current time:", now)
                delta = (nextTime-now)
                print("Sleeping for ", delta.seconds)
            time.sleep(delta.seconds)

    def stop(self):
        with self.mtx:
            self.running = False

    def start(self):
        print("Starting windmill history")
        self.running = True
        thread = threading.Thread(target=Windmillhistory.run, args=(self,))
        thread.start()
        return