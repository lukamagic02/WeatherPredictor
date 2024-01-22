import datetime
from statistics import mean
from meteostat import Hourly, Point


class DataAnalysis:
    @staticmethod
    def getFirstDayOfNextMonth(date, chooseMidnight):
        firstDayOfNextMonthMonth = (date.month % 12) + 1
        firstDayOfNextMonthYear = date.year if firstDayOfNextMonthMonth != 1 else date.year + 1
        firstDayOfNextMonth = datetime.date(firstDayOfNextMonthYear, firstDayOfNextMonthMonth, 1)

        if chooseMidnight is True:
            return datetime.datetime.combine(firstDayOfNextMonth, datetime.datetime.min.time())
        else:
            return datetime.datetime.combine(firstDayOfNextMonth, datetime.datetime.max.time())

    @staticmethod
    def isEndOfMonth(date):
        end = DataAnalysis.getFirstDayOfNextMonth(date, False) - datetime.timedelta(days=1)
        if end == date:
            return True
        return False

    @staticmethod
    def fetch_data(location: Point, granularity: str, start: datetime, end: datetime, key: str) -> (list, list):
        """
            Function for fetching and filtering data from Meteostat API based on given key and granularity.
        """
        if key == "":
            return [], []

        oldEnd = end
        if end > datetime.datetime.now():
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            end = datetime.datetime.combine(yesterday, datetime.datetime.max.time())

        """
            Preparing data to fetch based on granularity.
        """
        if granularity == "day" or granularity == "week":
            data_hourly = Hourly(location, start, end)
            data_toFetch = data_hourly.aggregate('D', 'mean')
        elif granularity == "month":
            if start.month == oldEnd.month and start.day != 1:
                start = DataAnalysis.getFirstDayOfNextMonth(start, True)

            if end.month == oldEnd.month and not DataAnalysis.isEndOfMonth(end):
                end = (datetime.datetime.combine(datetime.date(end.year, end.month, 1),
                                                 datetime.datetime.max.time()) - datetime.timedelta(days=1))

            if start > end:
                return [], []

            data_hourly = Hourly(location, start, end)
            data_toFetch = data_hourly.aggregate('M', 'mean')
        else:
            if start.month != 1 or start.day != 1:
                start = datetime.datetime(start.year + 1, 1, 1)

            if end.month != 12 or end.day != 31:
                end = datetime.datetime(end.year - 1, 12, 31, 23, 59, 59)

            if start > end:
                return [], []

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
        predictionDate=""

        """
            Filtering data based on granularity.    
        """
        if granularity == "day":
            for i in range(len(dates)):
                if oldEnd.day == 29 and oldEnd.month == 2:
                    if i > 0 and dates[i].year - dates[i-1].year > 4:
                        break
                else:
                    if i > 0 and dates[i].year - dates[i-1].year > 1:
                        break

                if oldEnd.day == dates[i].day and oldEnd.month == dates[i].month:
                    filtered_data.append(data[i])
                    filtered_dates.append(dates[i].year)
                    predictionDate=str(dates[i].day) + "." + str(dates[i].month)+"."
        elif granularity == "week":
            startOfWeek = oldEnd - datetime.timedelta(days=6)
            predictionDate=str(startOfWeek.day) +"."+str(startOfWeek.month) +".-"+str(oldEnd.day)+"."+str(oldEnd.month)+"."
            i = 0
            newWeek = []
            while i < len(dates):
                try:
                    date = datetime.datetime(startOfWeek.year, dates[i].month, dates[i].day)
                except ValueError:
                    i += 1
                    continue
                if startOfWeek <= date <= oldEnd:
                    newWeek.append((data[i], dates[i]))
                i += 1
            i = 0
            suma = []
            while i < len(newWeek):
                if i != 0 and newWeek[i][1] - newWeek[i-1][1] > datetime.timedelta(days=7):
                    filtered_data.append(mean(suma))
                    filtered_dates.append(newWeek[i-1][1].year)
                    suma = []
                suma.append(newWeek[i][0])
                i += 1
            if len(suma) > 0:
                filtered_data.append(mean(suma))
                filtered_dates.append(newWeek[len(newWeek)-1][1].year)

            startOfFirstWeek = datetime.date(dates[0].year, startOfWeek.month, startOfWeek.day)
            if startOfFirstWeek < dates[0]:
                filtered_data.pop(0)
                filtered_dates.pop(0)
        elif granularity == "month":
            for i in range(len(dates)):
                if i > 0 and dates[i].year - dates[i-1].year > 1:
                    break
                if oldEnd.month == dates[i].month:
                    filtered_data.append(data[i])
                    filtered_dates.append(dates[i].year)
                    predictionDate=str(dates[i].month) + ". month"
        else:
            for i in range(len(dates)):
                if i > 0 and dates[i].year - dates[i-1].year > 1:
                    break
                filtered_data.append(data[i])
                filtered_dates.append(dates[i].year)
                predictionDate=""

        return filtered_data, filtered_dates, predictionDate