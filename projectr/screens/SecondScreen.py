import numpy as np
import os
import matplotlib.pyplot as plt

from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from projectr.data.GlobalData import GlobalData
from datetime import datetime
from meteostat import Point, Hourly, Daily, Monthly


# Treba se ovo promijeniti
# Ako potrebno mijenjati 168. liniju: ako se negdje koristi f-ja Hourly, za nju je temp, za ostale tavg
def fetch_data(location, granularity, start, end):
    if granularity == "day":
        data = Daily(location, start, end)

    elif granularity == "week":
        daily_data = Hourly(location, start, end)
        data = daily_data.aggregate('W-Mon', 'mean')
        # W oznacava tjedno grupiranje,
        # a Mon da pocetak ciklusa
        # na kraju izracunamo srednju vrijednost uz pomoc mean

    elif granularity == "month":
        data = Monthly(location, start, end)

    else:
        # funkcija za obraditi cijelu godinu
        monthly_data = Monthly(location, start, end)
        data = monthly_data.aggregate('Y', 'mean')

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


def data_to_txt_file(file_path, data_summary):  # data_sum su razl vrste podataka(temp, tlak, padaline)
    with open(f"{file_path}.txt", 'a') as file:
        for data_type, data_info in data_summary.items():
            values = data_info['values']
            mean = data_info['mean']
            stand_dev = data_info['stand_dev']
            median = data_info['median']

            file.write(f"{data_type.capitalize()} Data:\n")
            file.write(f"Values: {values}\n")
            file.write(f"Standard Deviation: {stand_dev:.2f}\n")
            file.write(f"Mean: {mean:.2f}\n")
            file.write(f"Median: {median:.2f}\n\n")


def add_graph(main_layout, graph_source, values, key):
    # Izračunaj statističke vrednosti
    values = np.array(values)
    values = values[~np.isnan(values)]  # ako nemamo pod za neki mjesec/god/dan/tjedan jos, ignoriramo

    # Ako nema valjanih podataka
    if len(values) == 0:
        return

    mean = np.mean(values)
    stand_dev = np.std(values)
    median = np.median(values)

    # dodavanje Image i BoxLayout
    new_image = Image(source=graph_source, allow_stretch=False, keep_ratio=True,
                      size_hint=(1, None), height=500, pos_hint={'center_x': 0.5, 'center_y': 0.5}, nocache=True)
    box_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint=(1, None),
                           height=70, pos_hint={'center_x': 0.5, 'center_y': 0.1})

    labels = [
        Label(text=f"New Stand. Dev. = {stand_dev:.2f}", color=(0, 0, 0, 1)),
        Label(text=f"New Mean = {mean:.2f}", color=(0, 0, 0, 1)),
        Label(text=f"New Median = {median:.2f}", color=(0, 0, 0, 1))
    ]

    for label in labels:
        box_layout.add_widget(label)

    main_layout.add_widget(new_image)
    main_layout.add_widget(box_layout)
    data_summary = {key: {'values': values, 'mean': mean, 'stand_dev': stand_dev, 'median': median}}

    data_to_txt_file('data_summary', data_summary)

    return


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):  # izvodi funkciju neposredno prije što odemo na secondScreen
        self.create_matplotlib_plot()

    # staviti nyc kao globalnu varijablu?

    def create_matplotlib_plot(self):

        self.ids.main_box.clear_widgets()  # prilikom svakog submita čisti prethodne grafove

        file_name = 'data_summary.txt'
        # zelim da mi se izbrisu prijasni podatci u slucaju da postoje
        if os.path.exists(file_name):
            # otvaranje datoteke u "write" načinu brisanja postojećeg sadržaja
            with open(file_name, 'w') as file:
                # pisanje praznog niza u datoteku
                file.write('')

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
        print(data.head())

        for choice in dataChoice:
            values = 0
            if choice == "temperature":
                key = "temp" if granularity == "week" else "tavg"
                label = "Temperature data"

            elif choice == "amount of precipitation":
                key = "prcp"
                label = "Precipitation data"

            elif choice == "pressure":
                key = "pres"
                label = "Pressure data"

            # Izračunaj statističke vrijednosti
            values = data[key].tolist()

            graph = plot_graphs(data, key, label)
            add_graph(self.ids.main_box, graph, values, key)  # dodajemo graf dinamički na secondScreen

    def download_data_summary(self):
        # otvara prozor za odabir datoteke pomoću FileChooserListView
        content = FileChooserListView()
        popup = Popup(title="Odaberite mjesto za spremanje datoteke", content=content, size_hint=(0.8, 0.8))

        def save_callback(selected_path, selected_filename):
            # Kopiraj datoteku na tu lokaciju
            try:
                with open("data_summary.txt", "r") as source_file, open(
                        os.path.join(selected_path, selected_filename), "w") as dest_file:
                    dest_file.write(source_file.read())
                popup.dismiss()
            except Exception as e:
                print(f"Error: {e}")

        save_button = Button(text="Spremi", size_hint_y=None, height=40)

        # tu pozivamo save_callback i spremamo dat kad kliknemo spremi
        save_button.bind(on_release=lambda x: save_callback(content.path, "data_summary.txt"))
        content.add_widget(save_button)

        popup.open()
