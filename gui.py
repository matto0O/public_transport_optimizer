from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.clock import mainthread
from fetch_data import fetch_all
from multiprocessing import Process


class MyLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            Rectangle(pos=self.pos, size=self.size)


class Settings(AnchorLayout):
    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        def avoid_buses(instance):
            if self.avoid_buses_btn.state == 'normal':
                self.avoid_buses_btn.text = "Buses will be avoided"
            else:
                self.avoid_buses_btn.text = "Buses will be considered"

        def avoid_trams(instance):
            if self.avoid_trams_btn.state == 'normal':
                self.avoid_trams_btn.text = "Trams will be avoided"
            else:
                self.avoid_trams_btn.text = "Trams will be considered"

        def low_floor(instance):
            if self.low_floor_vehicles.state == 'normal':
                self.low_floor_vehicles.text = "Every vehicle will be browsed"
            else:
                self.low_floor_vehicles.text = "Only low floor vehicles will be browsed"

        def save_settings(instance):
            with open("settings.txt", 'w') as settings:
                settings.write(f"buses={self.avoid_buses_btn.state}\n")
                settings.write(f"trams={self.avoid_trams_btn.state}\n")
                settings.write(f"low={self.low_floor_vehicles.state}\n")
                try:
                    settings.write(f"mr={int(self.max_radius_txt.text)}\n")
                except ValueError:
                    settings.write(f"mr={700}")

        anchor_save = AnchorLayout(anchor_x='center', anchor_y='bottom')
        save_settings_btn = Button(text='Save', size_hint=(0.5, 0.15), on_press=save_settings)
        anchor_save.add_widget(save_settings_btn)
        self.add_widget(anchor_save)

        anchor_max_radius = AnchorLayout(anchor_x='right', anchor_y='top')
        self.max_radius_txt = TextInput(hint_text='Max radius', size_hint=(0.5, 0.3), font_size=25)
        anchor_max_radius.add_widget(self.max_radius_txt)
        self.add_widget(anchor_max_radius)

        anchor_low = AnchorLayout(anchor_x='left', anchor_y='top')
        self.low_floor_vehicles = ToggleButton(text='Every vehicle will be browsed', size_hint=(0.5, 0.3),
                                               on_press=low_floor)
        self.low_floor_vehicles.font_size = self.low_floor_vehicles.width * 0.1
        anchor_low.add_widget(self.low_floor_vehicles)
        self.add_widget(anchor_low)

        anchor_trams = AnchorLayout(anchor_x='left', anchor_y='center')
        self.avoid_trams_btn = ToggleButton(text='Trams will be considered', size_hint=(0.5, 0.3),
                                            on_press=avoid_trams, state='down')
        anchor_trams.add_widget(self.avoid_trams_btn)
        self.add_widget(anchor_trams)

        anchor_buses = AnchorLayout(anchor_x='right', anchor_y='center')
        self.avoid_buses_btn = ToggleButton(text='Buses will be considered', size_hint=(0.5, 0.3),
                                            on_press=avoid_buses, state='down')
        anchor_buses.add_widget(self.avoid_buses_btn)
        self.add_widget(anchor_buses)

        def load_settings():
            try:
                with open("settings.txt", 'r') as settings:
                    self.avoid_buses_btn.state = settings.readline().split('=')[1].strip('\n')
                    self.avoid_trams_btn.state = settings.readline().split('=')[1].strip('\n')
                    self.low_floor_vehicles.state = settings.readline().split('=')[1].strip('\n')
                    self.max_radius_txt.text = settings.readline().split('=')[1].strip('\n')
                    avoid_trams(None)
                    avoid_buses(None)
                    low_floor(None)
            except FileNotFoundError:
                pass

        load_settings()


class DownloadProgress(AnchorLayout):
    @mainthread
    def set_text(self):
        while self.status.text is not "Successfully gathered all the data!":
            try:
                with open("status.txt", 'r') as status_file:
                    new = status_file.readline()
                    if self.status.text != new:
                        print(f"update: {new}")
            except FileNotFoundError:
                pass

    def rearrange(self):
        entry_text = "Fetching the newest data..."
        self.status = Label(text=entry_text, size_hint=(0.8, 0.5))
        with open("status.txt", 'w') as status_file:
            status_file.write(entry_text)
        self.remove_widget(self.btn)
        self.add_widget(self.status)

    def on_click(self, instance):
        self.rearrange()
        process = Process(target=self.set_text)
        process.run()
        fetch_all()

    def __init__(self, **kwargs):
        super(DownloadProgress, self).__init__(**kwargs)
        self.status = None
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        self.btn = Button(text="Download data", size_hint=(0.8, 0.5), on_press=self.on_click)
        self.add_widget(self.btn)


class Results(StackLayout):
    def get_results(self, origin, destination):
        from data_processing import find_connections
        try:
            with open("settings.txt", 'r') as settings:
                self.avoid_buses = settings.readline().split('=')[1].strip('\n') == 'normal'
                self.avoid_trams = settings.readline().split('=')[1].strip('\n') == 'normal'
                self.low_floor_vehicles = settings.readline().split('=')[1].strip('\n') == 'down'
                self.max_radius_txt = settings.readline().split('=')[1].strip('\n')
        except FileNotFoundError:
            pass
        return find_connections(7, 0, 1, origin, destination, int(self.max_radius_txt),
                                self.low_floor_vehicles, self.avoid_buses, self.avoid_trams)

    def __init__(self, origin, destination, **kwargs):
        super(Results, self).__init__(**kwargs)
        self.max_radius_txt = 2000
        self.low_floor_vehicles = False
        self.avoid_buses = False
        self.avoid_trams = False
        self.orientation = 'tb-lr'
        results = self.get_results(origin, destination)
        amount_of_labels = len(results)
        if amount_of_labels == 0:
            self.add_widget(Label(text="No connections to show", size_hint=(1, 1)))
        else:
            self.labels = []
            field_height = 0.3 if amount_of_labels >= 3 else 1.0 / amount_of_labels
            for i in range(amount_of_labels):
                label = Label(text=str(results[i]), size_hint=(1, field_height))
                self.labels.append(label)
                self.add_widget(label)


def show_download_popup(instance):
    panel = DownloadProgress()
    popup = Popup(title="Fetching status", content=panel, size_hint=(0.7, 0.3))
    popup.open()


def show_settings_popup(instance):
    panel = Settings()
    popup = Popup(title="Settings", content=panel, size_hint=(0.5, 0.5))
    popup.open()


def show_results_popup(instance, origin, destination):
    panel = Results(origin, destination)
    popup = Popup(title="Connections", content=panel, size_hint=(0.8, 0.8))
    popup.open()


class Container(FloatLayout):
    def _update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)

        with self.canvas.before:
            self.background = Image(source='gui_files/background.jpg')

        self.bind(size=self._update_background, pos=self._update_background)

        anchor_label = AnchorLayout(anchor_x='center', anchor_y='top')
        label = MyLabel(text="Wrocław - public transport optimizer", size_hint=(0.6, 0.2))
        anchor_label.add_widget(label)

        anchor_origin = AnchorLayout(anchor_x='left', anchor_y='center')
        self.origin_txt = TextInput(hint_text='Origin', size_hint=(0.4, 0.2))
        anchor_origin.add_widget(self.origin_txt)

        anchor_dst = AnchorLayout(anchor_x='right', anchor_y='center')
        self.destination_txt = TextInput(hint_text='Destination', size_hint=(0.4, 0.2))
        anchor_dst.add_widget(self.destination_txt)

        def on_search_click(instance):
            show_results_popup(instance, self.origin_txt.text, self.destination_txt.text)

        anchor_search = AnchorLayout(anchor_x='center', anchor_y='bottom')
        search_btn = Button(text='Search', size_hint=(0.4, 0.2), on_press=on_search_click)
        anchor_search.add_widget(search_btn)

        anchor_redownload = AnchorLayout(anchor_x='right', anchor_y='top')
        redownload_btn = Button(size_hint=(0.13, 0.13), background_normal='gui_files/redownload.png',
                                background_down='gui_files/redownload_pressed.png', on_press=show_download_popup)
        anchor_redownload.add_widget(redownload_btn)

        anchor_settings = AnchorLayout(anchor_x='left', anchor_y='top')
        settings_btn = Button(size_hint=(0.13, 0.13), background_normal='gui_files/settings.png',
                              background_down='gui_files/settings_pressed.png', on_press=show_settings_popup)
        anchor_settings.add_widget(settings_btn)

        self.add_widget(anchor_label)
        self.add_widget(anchor_origin)
        self.add_widget(anchor_dst)
        self.add_widget(anchor_search)
        self.add_widget(anchor_settings)
        self.add_widget(anchor_redownload)


def init_settings():
    try:
        with open("settings.txt", 'r'):
            pass
    except FileNotFoundError:
        with open("settings.txt", 'w') as settings:
            settings.write(f"buses={'down'}\n")
            settings.write(f"trams={'down'}\n")
            settings.write(f"low={'normal'}\n")
            settings.write(f"mr={'700'}\n")


class PublicTransportOptimizer(App):
    def build(self):
        init_settings()
        return Container()
