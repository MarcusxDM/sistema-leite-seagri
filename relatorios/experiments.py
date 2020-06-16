import calendar
from datetime import datetime, timedelta

def semestre_list(date_time):
    if date_time >= datetime(date_time.year, 1, 1).date() and date_time < datetime(date_time.year, 7, 1).date():
        first_day_semestre = datetime(date_time.year, 1, 1).date()
        last_day_semestre  = (first_day_semestre.replace(month=7) - timedelta(days=1))
    else:
        first_day_semestre = datetime(date_time.year, 7, 1).date()
        last_day_semestre  = (first_day_semestre.replace(month=1, year=date_time.year+1) - timedelta(days=1))
    return[first_day_semestre, last_day_semestre]

if __name__ == "__main__":

    date_time           = datetime.strptime("2020-12-30", '%Y-%m-%d').date()
    print(semestre_list(date_time))

