from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarListItem
from kivymd.uix.pickers import MDDatePicker
from projectr.data.GlobalData import GlobalData


class ItemGranularity(OneLineAvatarListItem):

    def on_release(self):
        self.print_and_close_dialog()

    def print_and_close_dialog(self):
        global_data = GlobalData()
        app = MDApp.get_running_app()
        home_screen = app.root.get_screen("homeScreen")

        home_screen.ids.granularity_label.text = f"Granularity chosen: {self.text}"
        global_data.set_value("granularity", self.text)
        home_screen.dialogGranularity.dismiss()


class ItemDataType(OneLineAvatarListItem):
    selected = False

    def on_release(self):
        if not self.selected:
            self.selected = True
            self.bg_color = [0, 0, 1, 1]
        else:
            self.selected = False
            self.bg_color = [1, 1, 1, 1]
        self.print_and_save()

    def print_and_save(self):
        global_data = GlobalData()
        app = MDApp.get_running_app()
        home_screen = app.root.get_screen("homeScreen")
        selected_types = global_data.get_value("data_types")

        if self.selected:
            if selected_types == "":
                selected_types = []
                selected_types.append(self.text)
            else:
                selected_types.append(self.text)
        else:
            selected_types.remove(self.text)
        global_data.set_value("data_types", selected_types)

        label_text = ", ".join(selected_types)
        home_screen.ids.data_type_label.text = f"Data type chosen: {label_text}"


class HomeScreen(Screen):
    dialogData = None
    dialogGranularity = None
    dialogDate = None

    def on_save(self, instance, value, date_range):
        if len(date_range) == 0:
            error_popup = Popup(title='Invalid Date Range',
                                content=Label(text='Please enter a valid date range.'),
                                size_hint=(None, None), size=(400, 200))
            error_popup.open()
        else:
            global_data = GlobalData()
            self.ids.date_label.text = f"Date chosen: {date_range[0]} || {date_range[-1]}"
            global_data.set_value("start_date", date_range[0])
            global_data.set_value("end_date", date_range[-1])

    def on_cancel(self, instance, value):
        self.dialogDate.dismiss()

    def show_date_picker(self):
        if not self.dialogDate:
            self.dialogDate = MDDatePicker(mode="range")
            self.dialogDate.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        self.dialogDate.open()

    def show_granularity(self):
        if not self.dialogGranularity:
            self.dialogGranularity = MDDialog(
                title="Choose granularity",
                type="simple",
                items=[
                    ItemGranularity(text="day"),
                    ItemGranularity(text="week"),
                    ItemGranularity(text="month"),
                    ItemGranularity(text="year"),
                ],
            )
        self.dialogGranularity.open()

    def show_data_type(self):
        if not self.dialogData:
            self.dialogData = MDDialog(
                title="Choose data type",
                type="confirmation",
                items=[
                    ItemDataType(text="temperature"),
                    ItemDataType(text="amount of precipitation"),
                    ItemDataType(text="pressure"),
                ],
            )
        self.dialogData.open()

    def on_submit(self):
        if GlobalData().check_values():
            self.manager.current = "secondScreen"
            self.ids.alert.text = ""
        else:
            self.ids.alert.text = f"All values needed!"
