import calendar
from datetime import datetime, timedelta

if __name__ == "__main__":
    calendar.setfirstweekday(6)
    cal = calendar.monthcalendar(datetime.strptime("2020-05-31", '%Y-%m-%d').date().year, datetime.strptime("2020-05-31", '%Y-%m-%d').date().month)
    cal2 = calendar.Calendar(6).monthdatescalendar(datetime.strptime("2020-05-31", '%Y-%m-%d').date().year, datetime.strptime("2020-05-31", '%Y-%m-%d').date().month)
    week_list = (cal)

    date_time           = datetime.strptime("2020-05-31", '%Y-%m-%d').date()
    first_day_month     = date_time.replace(day=1)
    last_day_month      = first_day_month.replace(month=first_day_month.month+1) - timedelta(days=1)
    half_day_month      = first_day_month + timedelta(days=14)
    afterhalf_day_month = half_day_month + timedelta(days=1)
    # print(first_day_month, half_day_month, afterhalf_day_month, last_day_month)
    
    if (date_time >= first_day_month and date_time <= half_day_month):
        print([first_day_month, half_day_month])
    else:
        print([afterhalf_day_month, last_day_month])

    # if datetime.strptime("2020-05-31", '%Y-%m-%d').date() in week_list[-1]:
    #     print("caralho")