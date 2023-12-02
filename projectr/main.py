from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.HomeScreen import HomeScreen
from screens.PredictionScreen import PredictionScreen
from screens.SecondScreen import SecondScreen

sm = ScreenManager()
sm.add_widget(HomeScreen(name="homeScreen"))
sm.add_widget(SecondScreen(name="secondScreen"))
sm.add_widget(PredictionScreen(name="predictionScreen"))


class WeatherApp(MDApp):
    def build(self):
        screen = Builder.load_file("main.kv")
        return screen


WeatherApp().run()
