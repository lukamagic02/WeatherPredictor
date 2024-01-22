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
from meteostat import Point

from projectr.dataAnalysis.dataAnalysis import DataAnalysis
from projectr.linreg.linreg import LinReg


def plot_graphs(data, dates, label):
    x_data = dates
    y_data = data

    values = np.array(data)
    values = values[~np.isnan(values)]

    # Ako nema valjanih podataka
    if len(data) == 0:
        return

    mean = np.mean(values)
    stand_dev = np.std(values)

    fig, ax = plt.subplots()

    ax.plot(x_data, y_data, label=label)

    if len(data) == 1:
        ax.scatter(x_data[0], y_data[0], color=None, s=50)
    else:
        for x in range(len(x_data)):
            if np.abs(y_data[x] - mean) > 2 * stand_dev:
                ax.scatter(x_data[x], y_data[x], color='magenta', s=100)

    ax.scatter([], [], color='magenta', s=50, label='Mean ± 2*SD')
    #if len(data) > 1:
    ax.fill_between(x_data[-2:], np.min(y_data), np.max(y_data), color='purple', alpha=0.2, label='Prediction Interval')

    #ax.fill_between(x_data, mean + 2 * stand_dev, y_data, where=np.abs(y_data - mean) > 2 * stand_dev, color='red', alpha=0.7, linewidth=2)

    plt.xticks(rotation=35, fontsize=8)

    plt.xticks(x_data)  # da se ne prikazuje vrijeme, nego samo datum
    # bez ove linije pokazuje isti datum 2puta, ali u razlicitim satima: u 12h i 00h

    ax.set_xlabel('Time')
    ax.set_ylabel(f'{label.split()[0]}')
    ax.set_title(f'NYC {label.capitalize()}')

    ax.legend()
    plt.subplots_adjust(bottom=0.2, left=0.2, right=0.9, top=0.9) #prilagođavamo veličinu grafa kako bi nazivi x i y osi stali u sliku

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


def add_graph(main_layout, graph_source, values, key, newDate):
    # Izračunaj statističke vrednosti
    values = np.array(values)

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

    if newDate != "":
        text_box_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, None),
                                    height=70)
        text_label = Label(text=f"Data is displayed for interval: {newDate}", color=(0, 0, 0, 1))
        text_box_layout.add_widget(text_label)

    labels = [
        Label(text=f"New Stand. Dev. = {stand_dev:.2f}", color=(0, 0, 0, 1)),
        Label(text=f"New Mean = {mean:.2f}", color=(0, 0, 0, 1)),
        Label(text=f"New Median = {median:.2f}", color=(0, 0, 0, 1))
    ]

    for label in labels:
        box_layout.add_widget(label)

    main_layout.add_widget(new_image)
    if newDate != "":
        main_layout.add_widget(text_box_layout)
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

        key = ""
        label = ""
        for choice in dataChoice:
            values = 0
            if choice == "temperature":
                key = "temp"
                label = "Temperature data"

            elif choice == "amount of precipitation":
                key = "prcp"
                label = "Precipitation data"

            elif choice == "pressure":
                key = "pres"
                label = "Pressure data"

            # dohvaćamo podatke s meteostata
            data, dates, newDate = DataAnalysis.fetch_data(nyc, granularity, start, end, key)
            if len(data) >= 2:
                nextData, nextDate = LinReg.predict_value(dates, data)
                data = np.append(data, nextData)
                dates = np.append(dates, nextDate)

            graph = plot_graphs(data, dates, label)
            add_graph(self.ids.main_box, graph, data, key, newDate)  # dodajemo graf dinamički na secondScreen

    def download_data_summary(self):
        def save_callback(selected_path):
            try:
                filename = "data_summary.txt"
                with open("data_summary.txt", "r") as source_file, open(
                        os.path.join(selected_path, filename), "w") as dest_file:
                    dest_file.write(source_file.read())
                popup.dismiss()
            except Exception as e:
                print(f"Error: {e}")

        file_chooser = FileChooserListView()
        file_chooser.path = os.path.sep  # Initial directory

        save_button = Button(text="Spremi", size_hint_y=None, height=40)
        save_button.bind(on_release=lambda x: save_callback(file_chooser.path))

        box_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box_layout.add_widget(file_chooser)
        box_layout.add_widget(save_button)

        popup = Popup(
            title="Odaberite mjesto za spremanje datoteke",
            content=box_layout,
            size_hint=(0.8, 0.8),
        )

        popup.open()

