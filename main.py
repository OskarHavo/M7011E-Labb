import datetime

import model

def main():
    startDate = "2021-01-01"
    formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()
    households = model.initializeModel(10, formattedStartDate)
    return

main()
