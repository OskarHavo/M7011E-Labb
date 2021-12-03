class EnergyCentral:
    def __init__(self, maxCapacity):
        self.capacity = maxCapacity
        self.nClients = 0
        self.running = True
    def getAvailableEnergy(self):
        if not self.running:
            return 0
        if self.nClients == 0:
            return self.capacity
        return self.capacity/float(self.nClients)

    def nUsers(self):
        return self.nClients
    def attach(self):
        self.nClients = self.nClients +1
    def detach(self):
        self.nClients = self.nClients - 1