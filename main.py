import fetch_data
from gmaps import get_location, get_time_to_location
from data_processing import find_connections

if __name__ == '__main__':
    # fetch_data.fetch_all()
    for i in find_connections(7, 0, 0, "Wieczysta 155, Wrocław", "D-4 PWr", 700):
        print(i)
