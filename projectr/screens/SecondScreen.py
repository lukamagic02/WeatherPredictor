from kivy.uix.screenmanager import Screen
import matplotlib.pyplot as plt
from projectr.data.GlobalData import GlobalData
from datetime import datetime
from meteostat import Point, Hourly, Daily, Monthly


def fetch_data(location, granularity, start, end):
    if granularity == "day":
        data = Hourly(location, start, end)
        data = data.fetch()
    elif granularity == "week":
        # dodati funkciju za obraditi tjedan
        data = Daily(location, start, end)
        data = data.fetch()
    elif granularity == "month":
        data = Monthly(location, start, end)
        data = data.fetch()
    else:
        # funkcija za obraditi cijelu godinu
        data = Monthly(location, start, end)
        data = data.fetch()

    return data


def plot_graphs(data, key, label):
    x_data = data.index.values  # vraća vrijeme
    y_data = data[key]

    fig, ax = plt.subplots()

    ax.plot(x_data, y_data, label=label)

    plt.xticks(x_data)  # da se ne prikazuje vrijeme, nego samo datum
    # bez ove linije pokazuje isti datum 2puta: u 12h i 00h

    ax.set_xlabel('Time')
    ax.set_ylabel(f'{label.split()[0]}')
    ax.set_title(f'NYC {label.capitalize()}')

    ax.legend()

    plt.savefig('plot.png')

    plt.close()

    return 'plot.png'


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):  # izvodi funkciju prije nego što odemo na secondScreen
        self.create_matplotlib_plot()

    # staviti nyc kao globalnu varijablu?
    def create_matplotlib_plot(self):

        self.ids.plot1.source = ''
        self.ids.plot1.nocache = True  # da ucita novu sliku

        nyc = Point(40.7789, -73.9692, 3)
        globalData = GlobalData()
        startDate = globalData.get_value("start_date")
        endDate = globalData.get_value("end_date")
        granularity = globalData.get_value("granularity")
        dataChoice = globalData.get_value("data_types")

        # pretvorili smo startDate - koji je objekt date u datetime kako bi mogli izvuci podatke s meteostata
        start = datetime.combine(startDate, datetime.min.time())
        end = datetime.combine(endDate, datetime.max.time())

        # dohvaćamo podatke s meteostata
        data = fetch_data(nyc, granularity, start, end)

        for choice in dataChoice:
            if choice == "temperature":
                key = "temp" if granularity == "day" else "tavg"
                label = "Temperature data"

            elif choice == "amount of precipitation":
                key = "prcp"
                label = "Precipitation data"

            else:
                key = "pres"
                label = "Pressure data"

            graph = plot_graphs(data, key, label)
            self.ids.plot1.source = graph
