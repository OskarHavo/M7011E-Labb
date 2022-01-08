from windmill import *
from simulator import *
import datetime

class Windmillhistory():
    def __init__(self, simulator):
        self.sim = simulator
        return

    def run(self):
        timestamp = datetime.datetime.now() - datetime.timedelta(seconds=10)
        for username, windmillNode in self.sim.productionNodes:
            data = windmillNode.client.getNext(timestamp)


        return

    def start(self, timeInterval):
        return