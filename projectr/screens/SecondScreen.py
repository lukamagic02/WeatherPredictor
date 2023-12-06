from kivy.uix.screenmanager import Screen
import matplotlib.pyplot as plt
from projectr.data.GlobalData import GlobalData
from datetime import datetime
from meteostat import Point, Hourly, Daily, Monthly


def fetch_data(location, granularity, start, end):
    if granularity == "day":
        data = Hourly(location, start, end)
    elif granularity == "week":
        # dodati funkciju za obraditi tjedan
        data = Daily(location, start, end)
    elif granularity == "month":
        data = Monthly(location, start, end)
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
    # bez ove linije pokazuje isti datum 2puta, ali u razlicitim satima: u 12h i 00h

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

    def on_pre_enter(self, *args):  # izvodi funkciju neposredno prije što odemo na secondScreen
        self.create_matplotlib_plot()

    # staviti nyc kao globalnu varijablu?
    def create_matplotlib_plot(self):

        images = ['plot1', 'plot2', 'plot3']
        boxes = ['box1', 'box2', 'box3']

        for id_img in images:
            getattr(self.ids, id_img).source = ''
            getattr(self.ids, id_img).size_hint = (None, None)
            getattr(self.ids, id_img).height = 0
            getattr(self.ids, id_img).nocache = True  # da prilikom svakog submita ucita novu sliku

        for id_box in boxes:
            getattr(self.ids, id_box).size_hint = (None, None)
            getattr(self.ids, id_box).height = 0
            getattr(self.ids, id_box).opacity = 0


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
                id_img = 'plot1'
                id_box = 'box1'

            elif choice == "amount of precipitation":
                key = "prcp"
                label = "Precipitation data"
                id_img = 'plot2'
                id_box = 'box2'

            else:
                key = "pres"
                label = "Pressure data"
                id_img = 'plot3'
                id_box = 'box3'

            graph = plot_graphs(data, key, label)
            getattr(self.ids, id_img).source = graph

            # prikaz grafa u aplikaciji ako je kategorija odabrana
            getattr(self.ids, id_img).size_hint = (1, None)
            getattr(self.ids, id_img).height = 500

            # prikaz deskriptivne statistike ispod slike
            getattr(self.ids, id_box).size_hint = (1, None)
            getattr(self.ids, id_box).height = 70
            getattr(self.ids, id_box).opacity = 1
