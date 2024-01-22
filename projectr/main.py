from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from screens.HomeScreen import HomeScreen
from screens.SecondScreen import SecondScreen

sm = ScreenManager()
sm.add_widget(HomeScreen(name="homeScreen"))
sm.add_widget(SecondScreen(name="secondScreen"))


class WeatherApp(MDApp):
    def build(self):
        screen = Builder.load_file("main.kv")
        return screen


WeatherApp().run()
