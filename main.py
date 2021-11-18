import datetime

import model

def main():
    startDate = datetime.datetime(2023, 1, 1, 0)
    model.initializeModel(10, 1, startDate)
    return

main()
