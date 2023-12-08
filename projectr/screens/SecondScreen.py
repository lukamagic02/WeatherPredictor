from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
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


def add_graph(main_layout, graph_source):
    # dodavanje Image i BoxLayout

    new_image = Image(source=graph_source, allow_stretch=False, keep_ratio=True,
                      size_hint=(1, None), height=500, pos_hint={'center_x': 0.5, 'center_y': 0.5}, nocache=True)
    box_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint=(1, None),
                           height=70, pos_hint={'center_x': 0.5, 'center_y': 0.1})

    labels = [
        Label(text="New Stand. Dev. = ?", color=(0, 0, 0, 1)),
        Label(text="New Avg. = ?", color=(0, 0, 0, 1)),
        Label(text="New Median = ?", color=(0, 0, 0, 1))
    ]

    for label in labels:
        box_layout.add_widget(label)

    main_layout.add_widget(new_image)
    main_layout.add_widget(box_layout)

    return


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):  # izvodi funkciju neposredno prije što odemo na secondScreen
        self.create_matplotlib_plot()

    # staviti nyc kao globalnu varijablu?

    def create_matplotlib_plot(self):
        self.ids.main_box.clear_widgets() #prilikom svakog submita čisti prethodne grafove

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
            add_graph(self.ids.main_box, graph)  # dodajemo graf dinamički na secondScreen

