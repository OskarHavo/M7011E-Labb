import random
import threading
import dataGeneration
import datetime
import numpy as np

class EnergyCentral:
    """! Class for handling our power plant."""
    def __init__(self, maxCapacity, delta):
        """! Init
        @param maxCapacity The maximum production capacity
        @param delta Time delta between updates. Given in seconds.
        """
        self.capacityModifier = 1
        self.maxCapacity = maxCapacity
        self.currentCapacity = 0
        self.currentConsumption = 0
        self.clients = {}
        self.running = 0  # 0 = Stopped 1-9 = Starting 10 = Running
        self.sellRatio = 1
        self.buffer = 0
        self.marketDemand = 0
        self.modeledElectricityPrice = 0
        self.electricityPrice = 15.0
        self.blackoutRandState = dataGeneration.RandomState(random.random(), [0, 1])
        self.date = datetime.datetime.now()
        self.mutex = threading.Lock()
        self.delta = delta
        self.forceStop = False

    def getAvailableEnergy(self, user):
        """! Get the energy available to a singular user connected to the power plant
        The total energy is balanced over each of the users, providing equal power plant power to all.
        @param user A reference to a Windmill object
        @return The available energy for this user.
        """
        if user not in self.clients:
            # Unauthorized client
            return 0

        if self.clients[user]["powerOutage"]:
            return 0

        power = 0
        if self.running < 10:
            if len(self.clients) == 0:
                power = self.buffer
        else:
            power = self.currentCapacity

        nClients = 0
        for client in self.clients:
            if not self.clients[client]["powerOutage"]:
                nClients = nClients + 1
        if nClients == 0:
            return power
        return power / float(nClients)

    def nUsers(self):
        """! Get the number of users connected to the power plant.
        @param The total number of clients.
        """
        with self.mutex:
            return len(self.clients)

    def attach(self, client):
        """! Register a new client windmill to this energy central.
        @param client A reference to a windmill object
        """
        with self.mutex:
            self.clients[client.user] = {"windmill":client,"powerOutage": False}

    def detach(self, client):
        """! Unregister a client windmill from this energy central
        @param client A reference to a windmill client.
        """
        with self.mutex:
            if client.user in self.clients:
                del self.clients[client.user]

    def getEnergyPrice(self):
        """! Get energy price from the power plant.
        @return Energy price.
        """
        with self.mutex:
            return self.electricityPrice

    def setValue(self, valueName, value):
        """!Set energy central status variables.
        @param valueName 'SellRatio', 'stop', 'start', 'powerplantproduction', 'marketRatio', or 'currentelectricityprice'.
        @param value The requested value to set.
        """
        with self.mutex:
            if valueName == "sellRatio":
                self.sellRatio = value;
            elif valueName == "stop":
                self.running = 0
            elif valueName == "start":
                self.running = 1
            elif valueName == "powerplantproduction":
                self.capacityModifier = value;
                if self.capacityModifier == 0:
                    self.running = 0
                elif self.running == 0:
                    self.running = 1
            elif valueName == "marketRatio":
                self.sellRatio = value
            elif valueName == "currentelectricityprice":
                self.electricityPrice = value

    def updateTime(self):
        """! Update the timestamp."""
        date = datetime.datetime.now()
        formattedDate = date - datetime.timedelta(microseconds=date.microsecond)  # Ensures only 2 digits for seconds
        self.date = formattedDate

    def getCurrentData(self):
        """! Get the current data from the power plant.
        @return Dictionary with energy central state and output.
        """
        with self.mutex:
            return {
                "production": str(self.currentCapacity),
                "consumption": str(self.currentConsumption),
                "sellRatio": str(self.sellRatio),
                "running": str(self.running),
                "buffer": str(self.buffer),
                "modeledPrice": str(self.modeledElectricityPrice),
                "price": str(self.electricityPrice),
                "timestamp": str(self.date),
                "demand": str(self.marketDemand),
                "maxCapacityPercentage": str(self.capacityModifier),
                "maxCapacity": str(self.maxCapacity)}

    def updatePowerOutage(self):
        """! The implementation of our power outage function, where the users randomly can experience blackouts and thus
        only recieve power from its local windmill and not the central powerplant."""
        for client in self.clients:
            rn = self.blackoutRandState.tick()
            if self.clients[client]["powerOutage"]:
                # Turn back on with a 5% chance
                if rn < 0.05:
                    self.clients[client]["powerOutage"] = False
            else:
                # Turn off with a 1% chance
                if rn < 0.01:
                    self.clients[client]["powerOutage"] = True

    def halt(self):
        """! Halt the power plant update function."""
        with self.mutex:
            self.forceStop = True
    def tick(self):
        """! Calculate the current status of the energy central and produce a modelled electricity price, as well as
        store energy in the buffer or sell it to the market. If the run status is below 10, the energy central will only
        user power that is stored in the buffer and decrease the value until it reaches 0.
        """
        with self.mutex:
            self.updateTime()
            self.updatePowerOutage()
            self.currentConsumption = 0
            for client in self.clients:
                if not self.clients[client]["powerOutage"]:
                    self.currentConsumption = self.currentConsumption + self.clients[client]["windmill"].getPurchaseVolume()

            cap = self.capacityModifier * self.maxCapacity

            self.currentCapacity = np.clip(self.sellRatio * cap,0,self.maxCapacity)
            if self.running < 10:
                self.currentCapacity = self.buffer
                if self.running > 0:
                    self.running = self.running + 1
                self.buffer = self.buffer - self.currentConsumption
            else:
                self.buffer = self.buffer + cap - self.currentConsumption

            print(self.currentConsumption, "   ", self.marketDemand, "   ", self.currentCapacity, "   ", self.running)
            self.marketDemand = 0
            if self.currentCapacity > 0:
                self.marketDemand = (self.currentConsumption / self.currentCapacity) * 100.0

            self.modeledElectricityPrice = dataGeneration.calculateDailyEnergyPrice(self.currentCapacity,
                                                                                    self.currentConsumption)

    def stop(self):
        """! Stop the power plant. """
        with self.mutex:
            self.running = 0

    def run(self, socketio):
        """! Start the power plant. To stop it, call EnergyCentral.halt(self)
        @param socketio - Reference to a global socketIO object for handling multithreading/monkey threading. Yes, we need this.
        """
        with self.mutex:
            self.running = 1
        while True:
            with self.mutex:
                if self.forceStop:
                    return
            self.tick()
            socketio.sleep(self.delta)
