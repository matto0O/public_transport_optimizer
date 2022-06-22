import model.mainmodel as md


def save_settings(layout, instance):
    with open("model/settings.txt", 'w') as settings:
        settings.write(f"buses={layout.avoid_buses_btn.state}\n")
        settings.write(f"trams={layout.avoid_trams_btn.state}\n")
        settings.write(f"low={layout.low_floor_vehicles.state}\n")
        try:
            settings.write(f"mr={int(layout.max_radius_txt.text)}\n")
        except ValueError:
            settings.write(f"mr={700}")


def load_settings(layout):
    try:
        with open("model/settings.txt", 'r') as settings:
            layout.avoid_buses_btn.state = settings.readline().split('=')[1].strip('\n')
            layout.avoid_trams_btn.state = settings.readline().split('=')[1].strip('\n')
            layout.low_floor_vehicles.state = settings.readline().split('=')[1].strip('\n')
            layout.max_radius_txt.text = settings.readline().split('=')[1].strip('\n')
            md.avoid_trams(layout.avoid_trams_btn)
            md.avoid_buses(layout.avoid_buses_btn)
            md.low_floor(layout.low_floor_vehicles)
    except FileNotFoundError:
        pass


def get_results(layout, origin, destination, h, m, timetable):
    from model.mainmodel import process_results
    process_results(layout, origin, destination, h, m, timetable)


def on_search_click(layout, instance):
    match layout.timetable_spinner.text:
        case 'workdays':
            timetable = 0
        case 'saturdays':
            timetable = 1
        case 'nights sun/mon - thu/fri':
            timetable = 3
        case 'nights fri/sat':
            timetable = 4
        case 'nights sat/sun':
            timetable = 5
        case _:
            timetable = 2
    md.show_results_popup(layout.origin_txt.text, layout.destination_txt.text,
                          layout.hour_text.text, layout.minute_text.text, timetable)


def init_controller():
    md.init_settings()


def download_popup(instance):
    md.show_download_popup(instance)


def show_settings_popup(instance):
    md.show_settings_popup(instance)


def check_low(instance):
    md.low_floor(instance)


def check_at(instance):
    md.avoid_trams(instance)


def check_ab(instance):
    md.avoid_trams(instance)


def update(layout):
    from threading import Thread
    md.set_starting_view_on_download(layout)
    t = Thread(target=md.get_new_data)
    t.start()
    while layout.status.text != "Successfully gathered all the data!":
        print(layout.status.text)
        md.update_download_view(layout)
    layout.remove_widget(layout.btn)
    layout.status.size_hint = (1, 1)
