import math
import sqlite3

db = sqlite3.connect("pto.db")
cursor = db.cursor()


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


def stops_by_course(code, course):
    helper = cursor.execute("SELECT time_h, time_m FROM departures WHERE (course_id=? AND stop=?)", (course, code)) \
        .fetchall()
    cursor.execute("SELECT * FROM departures WHERE (course_id=? AND (time_h>? OR (time_h=? AND time_m>=?)))"
                   "ORDER BY time_h, time_h", (course, helper[0], helper[0], helper[1]))
    return cursor.fetchall()


def get_direct(list_from, list_to):
    result = set()
    for dep in list_from:
        for arr in list_to:
            if dep[3] == arr[3] and dep[5] == arr[5]:
                result.add((dep, arr))
    return tuple(result)


def find_connections(origin, destination, max_radius, h, m, timetable):
    dep_from = list()
    dep_to = list()
    for stop in filter(lambda x: math.sqrt(x[2]) * 111320 <= max_radius, sort_by_distance(origin)):
        for vehicle in departures_from_stop(stop[0], h, m, timetable):
            dep_from.append(vehicle)
    for stop in filter(lambda x: math.sqrt(x[2]) * 111320 <= max_radius, sort_by_distance(destination)):
        for vehicle in arrivals_at_stop(stop[0], h, m, timetable):
            dep_to.append(vehicle)
    print(get_direct(dep_from, dep_to))
