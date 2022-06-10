import fetch_data
from gmaps import get_location, get_time_to_location
from data_processing import find_connections

if __name__ == '__main__':
    # fetch_data.fetch_all()
    print(find_connections(get_location('Wieczysta 155, Wrocław'),
                           get_location('D-2, plac Grunwaldzki 9, 50-384 Wrocław'),
                           500, 7, 0, 0))
