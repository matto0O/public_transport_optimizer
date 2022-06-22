from kivy.uix.popup import Popup

from view.gui import DownloadProgress, Settings, Results


def avoid_buses(instance):
    if instance.state == 'normal':
        instance.text = "Buses will be avoided"
    else:
        instance.text = "Buses will be considered"


def avoid_trams(instance):
    if instance.state == 'normal':
        instance.text = "Trams will be avoided"
    else:
        instance.text = "Trams will be considered"


def low_floor(instance):
    if instance.state == 'normal':
        instance.text = "Every vehicle will be browsed"
    else:
        instance.text = "Only low floor vehicles will be browsed"


def fetch_results(layout, origin, destination, h, m, timetable):
    from model.data_processing import find_connections
    try:
        with open("model/settings.txt", 'r') as settings:
            layout.avoid_buses = settings.readline().split('=')[1].strip('\n') == 'normal'
            layout.avoid_trams = settings.readline().split('=')[1].strip('\n') == 'normal'
            layout.low_floor_vehicles = settings.readline().split('=')[1].strip('\n') == 'down'
            layout.max_radius_txt = settings.readline().split('=')[1].strip('\n')
    except FileNotFoundError:
        pass
    return find_connections(h, m, timetable, origin, destination, int(layout.max_radius_txt),
                            layout.low_floor_vehicles, layout.avoid_buses, layout.avoid_trams)


def process_results(layout, origin, destination, h, m, timetable):
    results = fetch_results(layout, origin, destination, h, m, timetable)
    amount_of_labels = len(results)
    from kivy.uix.label import Label
    if amount_of_labels == 0:
        layout.add_widget(Label(text="No connections to show", size_hint=(1, 1)))
    else:
        field_height = 0.3 if amount_of_labels >= 3 else 1.0 / amount_of_labels
        for i in range(amount_of_labels):
            label = Label(text=str(results[i]), size_hint=(1, field_height))
            layout.add_widget(label)


def show_download_popup(instance):
    panel = DownloadProgress()
    popup = Popup(title="Fetching status", content=panel, size_hint=(0.7, 0.3))
    popup.open()


def show_settings_popup(instance):
    panel = Settings()
    popup = Popup(title="Settings", content=panel, size_hint=(0.5, 0.5))
    popup.open()


def show_results_popup(origin, destination, h, m, timetable):
    try:
        if origin == "" or destination == "" or timetable == 20:
            raise ValueError
        panel = Results(origin, destination, int(h), int(m), timetable)
        popup = Popup(title="Connections", content=panel, size_hint=(0.8, 0.8))
        popup.open()
    except ValueError:
        pass


def get_new_data():
    from model.fetch_data import fetch_all
    fetch_all()


def set_starting_view_on_download(layout):
    entry_text = "Fetching the newest data..."
    layout.status.text = entry_text
    with open("model/status.txt", 'w') as status_file:
        status_file.write(entry_text)


def update_download_view(layout):
    try:
        with open("model/status.txt", 'r') as status_file:
            layout.status.text = status_file.readline()
    except FileNotFoundError:
        pass


def init_settings():
    try:
        with open("model/settings.txt", 'r'):
            pass
    except FileNotFoundError:
        with open("model/settings.txt", 'w') as settings:
            settings.write(f"buses={'down'}\n")
            settings.write(f"trams={'down'}\n")
            settings.write(f"low={'normal'}\n")
            settings.write(f"mr={'700'}\n")
