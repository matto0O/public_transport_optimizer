import math
import sqlite3
import gmaps
from datetime import time

db = sqlite3.connect("pto.db")
cursor = db.cursor()


class Trip:
    def __init__(self, start_point, end_point, departure, arrival, time):
        self.start_point = start_point
        self.end_point = end_point
        self.departure = departure
        self.start_stop_name = cursor.execute("SELECT stop_name FROM stops WHERE code=?",
                                              (departure[-2],)).fetchall()[0][0]
        self.arrival = arrival
        self.end_stop_name = cursor.execute("SELECT stop_name FROM stops WHERE code=?", (arrival[-2],)).fetchall()[0][0]
        self.total_time = time
        self.time_intervals = self.time_segments()

    def time_segments(self):
        a = gmaps.get_time_to_location(self.start_point, get_location_by_stop_code(self.departure[-2]))
        b = (self.arrival[0] - self.departure[0]) * 60 + self.arrival[1] - self.departure[1]
        c = gmaps.get_time_to_location(get_location_by_stop_code(self.arrival[-2]), self.end_point)
        return a, b, c

    def __repr__(self):
        h = int((self.departure[0] * 60 + self.departure[1] - self.time_segments()[0]) / 60)
        m = (self.departure[0] * 60 + self.departure[1] - self.time_segments()[0]) % 60
        h_end = int((self.arrival[0] * 60 + self.arrival[1] + self.time_segments()[2]) / 60)
        m_end = (self.arrival[0] * 60 + self.arrival[1] + self.time_segments()[2]) % 60
        return f"Leave at {time(h, m).strftime('%H:%M')}\nTake {self.departure[3]} from {self.start_stop_name}" \
               f" at {time(self.departure[0], self.departure[1]).strftime('%H:%M')} to {self.end_stop_name}.\n" \
               f"After {self.time_segments()[1]} minute ride and {self.time_segments()[2]} minute walk" \
               f", you're expected to reach your destination at {time(h_end, m_end).strftime('%H:%M')}\n" \
               f"Total time: {self.total_time}\n"


def sort_by_distance(location):
    cursor.execute("SELECT code, stop_name,"
                   " (([latitude]-?)*([latitude]-?)+([longitude]-?)*([longitude]-?)) AS dist FROM stops"
                   " ORDER BY ([latitude]-?)*([latitude]-?)+([longitude]-?)*([longitude]-?)",
                   (location[0], location[0], location[1], location[1],
                    location[0], location[0], location[1], location[1]))
    return cursor.fetchall()


def departures_from_stop(code, h, m, timetable):
    cursor.execute("SELECT * FROM "
                   "(SELECT * FROM departures WHERE (stop=? AND timetable=? AND (time_h>? OR (time_h=? AND time_m>=?)))"
                   " ORDER BY time_h, time_m)"
                   " GROUP BY stop, line HAVING COUNT(*)>=1 ", (code, timetable, h, h, m))
    return cursor.fetchall()


def arrivals_at_stop(code, h, m, timetable):
    cursor.execute("SELECT * FROM departures WHERE (stop=? AND timetable=? AND (time_h>? OR (time_h=? AND time_m>=?)))"
                   " ORDER BY time_h, time_m", (code, timetable, h, h, m))
    return cursor.fetchall()


def lines_at_stop(code):
    return tuple(cursor.execute("SELECT DISTINCT line, variant FROM departures WHERE stop=?", (code,)).fetchall())


def stops_by_course(line: int, course: int):
    return cursor.execute("SELECT * FROM departures WHERE (course_id=? AND line=?)", (course, line)).fetchall()


def get_location_by_stop_code(code):
    return cursor.execute("SELECT latitude, longitude FROM stops WHERE code=?", (code,)).fetchall()[0]


def get_direct(list_from, list_to):
    result = set()
    for dep in list_from:
        for arr in list_to:
            if dep[3] == arr[3] and dep[5] == arr[5] and (dep[0] * 60 + dep[1] < arr[0] * 60 + arr[1]):
                result.add((dep, arr))
    return tuple(result)


def remove_redundant_departures(dep_list, place):
    result = list()
    unique_deps = set(map(lambda x: (x[3], x[4]), dep_list))
    for unique in unique_deps:
        same_line = filter(lambda x: (x[3], x[4]) == unique, dep_list)
        stops_in_order = sorted(map(lambda x: (x, x[0] * 60 + x[1]), same_line), key=(lambda x: x[1]))
        last_time = stops_in_order[-1][1]
        try:
            result.append(sorted(stops_in_order, key=(lambda x: last_time - x[1] +
                                                                gmaps.get_time_to_location(
                                                                    get_location_by_stop_code(x[0][-2]), place)))[0][0])
        except IndexError:
            pass
    return result


def trip_time(tup, origin, destination):
    return (tup[1][0] - tup[0][0]) * 60 + tup[1][1] - tup[0][1] + \
           gmaps.get_time_to_location(origin, get_location_by_stop_code(tup[0][-2])) + \
           gmaps.get_time_to_location(get_location_by_stop_code(tup[1][-2]), destination)


def find_connections(h, m, timetable, origin, destination, max_radius=2000):
    dep_from = list()
    dep_to = list()
    origin_loc = gmaps.get_location(origin)
    dest_loc = gmaps.get_location(destination)
    for stop in filter(lambda x: math.sqrt(x[2]) * 111320 <= max_radius, sort_by_distance(origin_loc)):
        for vehicle in departures_from_stop(stop[0], h, m, timetable):
            dep_from.append(vehicle)
    end_stops = tuple(map(lambda x: x[0],
                          filter(lambda x: math.sqrt(x[2]) * 111320 <= max_radius, sort_by_distance(dest_loc))))
    possible_lines = set()
    for es in end_stops:
        for line in lines_at_stop(es):
            possible_lines.add(line)
    dep_from = remove_redundant_departures(dep_from, origin_loc)
    dep_from = list(filter(lambda x: (x[3], x[4]) in possible_lines, dep_from))
    for dep in dep_from:
        dep_to.extend(filter(lambda x: x[-2] in end_stops, stops_by_course(dep[3], dep[5])))
    dep_to = remove_redundant_departures(dep_to, dest_loc)

    holder = filter(lambda x: x[1] > 0,
                    map(lambda elem: (elem, trip_time(elem, origin_loc, dest_loc)), (get_direct(dep_from, dep_to))))
    return tuple(map(lambda x: Trip(origin_loc, dest_loc, x[0][0], x[0][1], x[1]),
                     sorted(holder, key=(lambda x: x[1]))))
