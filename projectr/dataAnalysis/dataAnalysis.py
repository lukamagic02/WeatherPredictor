import datetime
from statistics import mean
from meteostat import Hourly, Point


def fetch_data(location: Point, granularity: str, start: datetime, end: datetime, key: str) -> (list, list):
    """
        Function for fetching and filtering data from Meteostat API based on given key and granularity.
    """
    if key == "":
        return [], []

    oldEnd = end
    if end > datetime.datetime.now():
        now = datetime.datetime.now()
        end = datetime.datetime(now.year, now.month, now.day)

    """
        Preparing data to fetch based on granularity.
    """
    if granularity == "day" or granularity == "week":
        data_hourly = Hourly(location, start, end)
        data_toFetch = data_hourly.aggregate('D', 'mean')
    elif granularity == "month":
        end = datetime.datetime(end.year, end.month, 1) - datetime.timedelta(days=1)
        data_hourly = Hourly(location, start, end)
        data_toFetch = data_hourly.aggregate('M', 'mean')
    else:
        end = datetime.datetime(end.year, 1, 1) - datetime.timedelta(days=1)
        data_hourly = Hourly(location, start, end)
        data_toFetch = data_hourly.aggregate('Y', 'mean')

    """
        Fetching data from Meteostat API.
    """
    dataFetched = data_toFetch.fetch()
    dates = dataFetched.index.date
    data = dataFetched[key].values

    filtered_data = []
    filtered_dates = []

    """
        Filtering data based on granularity.    
    """
    if granularity == "day":
        for i in range(len(dates)):
            if i > 0 and dates[i].year - dates[i-1].year > 1:
                break
            if oldEnd.day == dates[i].day and oldEnd.month == dates[i].month:
                filtered_data.append(data[i])
                filtered_dates.append(dates[i])
    elif granularity == "week":
        startOfWeek = oldEnd - datetime.timedelta(days=6)
        i = 0
        newWeek = []
        while i < len(dates):
            date = datetime.datetime(startOfWeek.year, dates[i].month, dates[i].day)
            if startOfWeek <= date <= oldEnd:
                newWeek.append((data[i], dates[i]))
            i += 1
        i = 0
        suma = []
        while i < len(newWeek):
            if i != 0 and newWeek[i][1] - newWeek[i-1][1] > datetime.timedelta(days=7):
                filtered_data.append(mean(suma))
                filtered_dates.append(newWeek[i-1][1])
                suma = []
            suma.append(newWeek[i][0])
            i += 1
    elif granularity == "month":
        for i in range(len(dates)):
            if i > 0 and dates[i].year - dates[i-1].year > 1:
                break
            if i == 0 and dates[i].day != 1:
                continue
            if oldEnd.month == dates[i].month:
                filtered_data.append(data[i])
                filtered_dates.append(dates[i])
    else:
        for i in range(len(dates)):
            if i > 0 and dates[i].year - dates[i-1].year > 1:
                break
            if i == 0 and dates[i].month != 1 and dates[i].day != 1:
                continue
            filtered_data.append(data[i])
            filtered_dates.append(dates[i])

    return filtered_data, filtered_dates
