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
from functools import partial

from controller import controller
from model.fetch_data import fetch_all
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.spinner import Spinner


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

        anchor_save = AnchorLayout(anchor_x='center', anchor_y='bottom')
        save_settings_btn = Button(text='Save', size_hint=(0.5, 0.15), on_press=partial(controller.save_settings, self))
        anchor_save.add_widget(save_settings_btn)
        self.add_widget(anchor_save)

        anchor_max_radius = AnchorLayout(anchor_x='right', anchor_y='top')
        self.max_radius_txt = TextInput(hint_text='Max radius', size_hint=(0.5, 0.3), font_size=25)
        anchor_max_radius.add_widget(self.max_radius_txt)
        self.add_widget(anchor_max_radius)

        anchor_low = AnchorLayout(anchor_x='left', anchor_y='top')
        self.low_floor_vehicles = ToggleButton(text='Every vehicle will be browsed', size_hint=(0.5, 0.3),
                                               on_press=controller.check_low)
        self.low_floor_vehicles.font_size = self.low_floor_vehicles.width * 0.1
        anchor_low.add_widget(self.low_floor_vehicles)
        self.add_widget(anchor_low)

        anchor_trams = AnchorLayout(anchor_x='left', anchor_y='center')
        self.avoid_trams_btn = ToggleButton(text='Trams will be considered', size_hint=(0.5, 0.3),
                                            on_press=controller.check_at, state='down')
        anchor_trams.add_widget(self.avoid_trams_btn)
        self.add_widget(anchor_trams)

        anchor_buses = AnchorLayout(anchor_x='right', anchor_y='center')
        self.avoid_buses_btn = ToggleButton(text='Buses will be considered', size_hint=(0.5, 0.3),
                                            on_press=controller.check_ab, state='down')
        anchor_buses.add_widget(self.avoid_buses_btn)
        self.add_widget(anchor_buses)

        controller.load_settings(self)


class DownloadProgress(AnchorLayout):
    # @mainthread
    # def set_text(self):
    #     while self.status.text is not "Successfully gathered all the data!":
    #         try:
    #             with open("model/status.txt", 'r') as status_file:
    #                 new = status_file.readline()
    #                 if self.status.text != new:
    #                     print(f"update: {new}")
    #         except FileNotFoundError:
    #             pass

    def rearrange(self):
        entry_text = "Fetching the newest data..."
        self.status = Label(text=entry_text, size_hint=(0.8, 0.5))
        with open("model/status.txt", 'w') as status_file:
            status_file.write(entry_text)
        self.remove_widget(self.btn)
        self.add_widget(self.status)

    def on_click(self, instance):
        from threading import Thread
        self.rearrange()
        #Thread(target=self.set_text).start()
        fetch_all()

    def __init__(self, **kwargs):
        super(DownloadProgress, self).__init__(**kwargs)
        self.status = None
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        self.btn = Button(text="Download data", size_hint=(0.8, 0.5), on_press=self.on_click)
        self.add_widget(self.btn)


class Results(StackLayout):

    def __init__(self, origin, destination, h, m, timetable, **kwargs):
        super(Results, self).__init__(**kwargs)
        self.max_radius_txt = 2000
        self.low_floor_vehicles = False
        self.avoid_buses = False
        self.avoid_trams = False
        self.orientation = 'tb-lr'

        controller.get_results(self, origin, destination, h, m, timetable)


class Container(FloatLayout):
    def _update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)

        with self.canvas.before:
            self.background = Image(source='view/gui_files/background.jpg')

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

        anchor_params = AnchorLayout(anchor_x='center', anchor_y='center')
        layout_h = RelativeLayout()
        self.hour_text = TextInput(hint_text="hour", size_hint=(0.15, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        layout_h.add_widget(self.hour_text)
        layout_m = RelativeLayout()
        self.minute_text = TextInput(hint_text="minute", size_hint=(0.15, 0.1),
                                     pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout_m.add_widget(self.minute_text)
        layout_timetable = RelativeLayout()
        self.timetable_spinner = Spinner(text="Timetable", size_hint=(0.15, 0.1),
                                         pos_hint={'center_x': 0.5, 'center_y': 0.4},
                                         values=["workdays", "saturdays", "sundays and holidays",
                                                 "nights sun/mon - thu/fri", "nights fri/sat", "nights sat/sun"])
        layout_timetable.add_widget(self.timetable_spinner)
        anchor_params.add_widget(layout_m)
        anchor_params.add_widget(layout_h)
        anchor_params.add_widget(layout_timetable)

        anchor_search = AnchorLayout(anchor_x='center', anchor_y='bottom')
        search_btn = Button(text='Search', size_hint=(0.4, 0.2), on_release=partial(controller.on_search_click, self))
        anchor_search.add_widget(search_btn)

        anchor_redownload = AnchorLayout(anchor_x='right', anchor_y='top')
        redownload_btn = Button(size_hint=(0.13, 0.13), background_normal='view/gui_files/redownload.png',
                                background_down='view/gui_files/redownload_pressed.png',
                                on_release=controller.download_popup)
        anchor_redownload.add_widget(redownload_btn)

        anchor_settings = AnchorLayout(anchor_x='left', anchor_y='top')
        settings_btn = Button(size_hint=(0.13, 0.13), background_normal='view/gui_files/settings.png',
                              background_down='view/gui_files/settings_pressed.png',
                              on_release=controller.show_settings_popup)
        anchor_settings.add_widget(settings_btn)

        self.add_widget(anchor_label)
        self.add_widget(anchor_origin)
        self.add_widget(anchor_dst)
        self.add_widget(anchor_search)
        self.add_widget(anchor_settings)
        self.add_widget(anchor_redownload)
        self.add_widget(anchor_params)


class PublicTransportOptimizer(App):
    def build(self):
        controller.init_controller()
        return Container()


if __name__ == '__main__':
    PublicTransportOptimizer().run()
