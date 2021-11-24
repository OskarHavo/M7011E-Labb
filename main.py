import datetime
import time
import model

def main():
    startDate = "2021-01-01"
    formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()
    model.initializeModel(10, formattedStartDate)
    while True:
        time.sleep(5)
        print("alive")
    return

main()
