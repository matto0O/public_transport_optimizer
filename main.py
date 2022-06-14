from data_processing import find_connections
from optimizer import ticket_price_to_ride_time_ratio

if __name__ == '__main__':
    for ride in find_connections(7, 0, 0, "Kamienna 145, Wrocław", "D-4 PWr", 700):
        print(ride)
    print(ticket_price_to_ride_time_ratio(max_trip_length=16))
