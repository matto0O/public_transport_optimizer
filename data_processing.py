import math
import sqlite3
from gmaps import get_time_to_location

db = sqlite3.connect("pto.db")
cursor = db.cursor()


class Departure:
    def __init__(self, arg):
        self.h = arg[0]
        self.m = arg[1]
        self.timetable = arg[2]
        self.line = arg[3]
        self.course_id = arg[5]
        self.stop_code = arg[6]
        self.low = arg[7]

    def __eq__(self, other):
        return self.line == other.line and self.course_id == other.course_id

    def __repr__(self):
        return f"({self.line}, {self.h}, {self.m}, {self.stop_code}, {self.course_id})"


class Trip:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point
        self.departures = list()
        self.arrivals = list()

    def total_time(self):
        time = get_time_to_location(self.start_point, get_location_by_stop_code(self.departures[0].stop_code))
        for i in range(len(self.departures)):
            time += (self.arrivals[i].h - self.departures[i].h) * 60 + self.arrivals[i].m - self.departures[i].m
        time += get_time_to_location(get_location_by_stop_code(self.arrivals[-1].stop_code), self.end_point)
        return time

    def add_dep(self, departure):
        self.departures.append(departure)

    def add_arr(self, arrival):
        self.arrivals.append(arrival)


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


def stops_by_course(line: int, course: int):
    return cursor.execute("SELECT * FROM departures WHERE (course_id=? AND line=?)", (course, line)).fetchall()


def get_location_by_stop_code(code):
    return cursor.execute("SELECT latitude, longitude FROM stops WHERE code=?", (code,)).fetchall()[0]


def get_stops_in_range(location, max_radius):
    return tuple(filter(lambda x: math.sqrt(x[2]) * 111320 <= max_radius, sort_by_distance(location)))


def trip_time(tup, origin, destination):
    return (tup[1][0] - tup[0][0]) * 60 + tup[1][1] - tup[0][1] + \
           get_time_to_location(origin, get_location_by_stop_code(tup[0][-2])) + \
           get_time_to_location(get_location_by_stop_code(tup[1][-2]), destination)


def best_unique_courses(courses_list, place):
    if len(courses_list) == 0:
        return []
    result = list()
    courses = list(set(map(lambda x: (x[3], x[5]), courses_list)))
    for course in courses:
        same_lines = sorted(filter(lambda x: (x[3], x[5]) == course, courses_list),
                            key=(lambda x: 60 * x[0] + x[1]))
        last = (lambda x: 60 * x[0] + x[1])(same_lines[-1])
        same_lines = sorted(same_lines, key=(lambda x: 60 * x[0] + x[1] - last +
                                                       get_time_to_location(place, get_location_by_stop_code(x[-2]))))
        result.append(same_lines[0])
    return result


def find_connections(h, m, timetable, origin, destination, max_radius):
    possible_beginnings = list()
    connections = list()
    for stop in get_stops_in_range(origin, max_radius):
        possible_beginnings.extend(departures_from_stop(stop[0], h, m, timetable))
    possible_beginnings = best_unique_courses(possible_beginnings, origin)
    possible_end_points = get_stops_in_range(destination, max_radius)
    for course in possible_beginnings:
        helper_connections = list()
        for stop in stops_by_course(course[3], course[-3]):
            if stop[-2] in map(lambda x: x[0], possible_end_points):
                helper_connections.append(cursor.execute
                                          ("SELECT * FROM departures WHERE (stop=? AND line=? AND course_id=?)",
                                           (stop[-2], stop[3], stop[-3])).fetchall()[0])
        try:
            connection = (Departure(course), Departure(best_unique_courses(helper_connections, destination)[0]))
            if connection[0].h * 60 + connection[0].m < connection[1].h * 60 + connection[1].m:
                connections.append(connection)
        except IndexError:
            pass
    return connections
