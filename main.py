import datetime

import model

def main():
    startDate = "2021-01-01"
    formattedStartDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()
    model.initializeModel(10, 1, formattedStartDate)
    return

main()
