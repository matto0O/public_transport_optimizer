# from data_processing import find_connections
import fetch_data
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup


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

        anchor_settings = AnchorLayout(anchor_x='center', anchor_y='bottom')
        save_settings_btn = Button(text='Save', size_hint=(0.5, 0.15))
        anchor_settings.add_widget(save_settings_btn)
        self.add_widget(anchor_settings)

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


def show_popup(instance):
    panel = Settings()
    popup = Popup(title="Settings", content=panel, size_hint=(0.5, 0.5))
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

        anchor_search = AnchorLayout(anchor_x='center', anchor_y='bottom')
        search_btn = Button(text='Search', size_hint=(0.4, 0.2), on_press=self.search)
        anchor_search.add_widget(search_btn)

        anchor_redownload = AnchorLayout(anchor_x='right', anchor_y='top')
        redownload_btn = Button(size_hint=(0.13, 0.13), background_normal='gui_files/redownload.png',
                                background_down='gui_files/redownload_pressed.png')
        anchor_redownload.add_widget(redownload_btn)

        anchor_settings = AnchorLayout(anchor_x='left', anchor_y='top')
        settings_btn = Button(size_hint=(0.13, 0.13), background_normal='gui_files/settings.png',
                              background_down='gui_files/settings_pressed.png', on_press=show_popup)
        anchor_settings.add_widget(settings_btn)

        self.add_widget(anchor_label)
        self.add_widget(anchor_origin)
        self.add_widget(anchor_dst)
        self.add_widget(anchor_search)
        self.add_widget(anchor_settings)
        self.add_widget(anchor_redownload)

    def search(self, instance):
        if self.origin_txt.text != "" and self.destination_txt.text != "":
            print(self.origin_txt.text, self.destination_txt.text)


class PublicTransportOptimizer(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    # fetch_data.fetch_all()
    # for ride in find_connections(7, 0, 0, "Kamienna 145, Wrocław", "D-4 PWr", 700):
    #     print(ride)
    PublicTransportOptimizer().run()
