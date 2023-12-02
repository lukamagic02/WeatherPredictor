from kivy.uix.screenmanager import Screen
import matplotlib.pyplot as plt
from projectr.data.GlobalData import GlobalData


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)
        self.create_matplotlib_plot()

    def create_matplotlib_plot(self):  #Primjer kako napraviti graf na drugom ekranu
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 12, 8, 15, 20]

        #Podaci s prvog skringa se dohvacaju preko GlobalData
        #svi vracaju string osim data_types koji je string[]
        globalData = GlobalData()
        globalData.get_value("start_date")
        globalData.get_value("end_date")
        globalData.get_value("granularity")
        globalData.get_value("granularity")
        globalData.get_value("data_types")

        fig, ax = plt.subplots()
        ax.plot(x_data, y_data, label='Example Data')

        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title('Matplotlib Plot')

        ax.legend()

        plt.savefig('projectr/temp_plot.png')

        plt.close()
