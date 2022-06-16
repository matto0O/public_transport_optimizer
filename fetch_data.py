import time

import pandas as pd
from zipfile import ZipFile
import os
import shutil
from xml.etree.ElementTree import parse
from dataclasses import dataclass
import datetime
import sqlite3

lines = list()
db = sqlite3.connect("pto.db")
db.execute("PRAGMA foreign_keys = ON")
cursor = db.cursor()
start = datetime.datetime.now()


@dataclass(frozen=True)
class Line:
    signature: str
    variants: list

    def __repr__(self):
        return "Linia {}\n{}".format(self.signature, self.variants[0])

    def __str__(self):
        return f"Linia {self.signature}"


def find_line_by_signature(signature):
    for line in lines:
        if line.signature == signature:
            return line
    return None


def download_timetables():
    import requests as rq
    txt_files_url = \
        'https://www.wroclaw.pl/open-data/87b09b32-f076-4475-8ec9-6020ed1f9ac0/OtwartyWroclaw_rozklad_jazdy_GTFS.zip'
    xml_files_url = 'https://www.wroclaw.pl/open-data/6db186a9-9b94-4ed4-8d63-f3fa6d38dc5f/XML-rozkladyjazdy.zip'
    xml_filename = xml_files_url.split('/')[-1]
    txt_filename = txt_files_url.split('/')[-1]
    with open(xml_filename, 'wb') as xml_files:
        xml_files.write(rq.get(xml_files_url).content)
    with open(txt_filename, 'wb') as txt_files:
        txt_files.write(rq.get(txt_files_url).content)
    try:
        shutil.rmtree(xml_filename[:-4])
        os.remove("stops.txt")
    except FileNotFoundError:
            pass
    unpack_timetable(xml_filename)
    unpack_other(txt_filename)


def unpack_other(target):
    handle = ZipFile(target)
    handle.extract("stops.txt")
    handle.close()
    os.remove(target)


def unpack_timetable(target):
    handle = ZipFile(target)
    newname = target[:-4]
    handle.extractall(newname)
    handle.close()
    os.remove(target)

    lines_list = os.listdir(newname)
    for folder in lines_list:
        for file in os.listdir("{}/{}".format(newname, folder)):
            shutil.move(os.path.join("{}/{}".format(newname, folder), file), newname)
        os.rmdir("{}/{}".format(newname, folder))


def fetch_stops():
    file = pd.read_csv("stops.txt", dtype=str)
    for elem in file.iterrows():
        cursor.execute("INSERT INTO stops (code, stop_name, latitude, longitude) VALUES (?,?,?,?)",
                       (elem[1][1], elem[1][2], float(elem[1][3]), float(elem[1][4])))


def fetch_lines():
    for file in os.listdir("XML-rozkladyjazdy"):
        tree = parse(f"XML-rozkladyjazdy\{file}")
        root = tree.getroot()
        variants = list()
        for child in root[0]:
            intervals = dict()
            for times in child[0][0]:
                intervals[times.attrib['id']] = int(times.attrib['czas'])
            variants.append(intervals)
        lines.append(Line(root[0].attrib['nazwa'], variants))


def fetch_departures():
    for file in os.listdir("XML-rozkladyjazdy"):
        tree = parse(f"XML-rozkladyjazdy\{file}")
        root = tree.getroot()
        signature = root[0].attrib['nazwa']
        course_id = 0
        for variant in root[0]:
            variant_id = int(variant.attrib['id'])
            stop = variant[0]
            try:
                for day in stop[1]:
                    match day.attrib['nazwa']:
                        case 'w dni robocze':
                            timetable = 0
                        case 'Sobota':
                            timetable = 1
                        case 'niedz./ pon. – czw./ pt.':
                            timetable = 3
                        case 'pt./ sob.':
                            timetable = 4
                        case 'sob./ niedz.':
                            timetable = 5
                        case _:
                            timetable = 2
                    for hour in day:
                        h = int(hour.attrib['h'])
                        for minute in hour:
                            m = int(minute.attrib['m'])
                            low = signature in ('A', 'C', 'D', 'K', 'N')
                            try:
                                if int(signature) >= 100:
                                    low = True
                            except ValueError:
                                pass
                            if len(minute.attrib) > 1:
                                low = minute.attrib['ozn'] == 'N'
                            course_id += 1
                            for e, departure in enumerate(find_line_by_signature(signature).
                                                                  variants[variant_id].items()):
                                new_m = departure[1] + m
                                new_h = 24 if ((h + (new_m > 59)) % 24) == 0 else ((h + (new_m > 59)) % 24)
                                current_stop = variant[e].attrib['id']
                                cursor.execute(
                                    "INSERT INTO departures "
                                    "(time_h, time_m, timetable, line, variant, course_id, stop, low)"
                                    " VALUES (?,?,?,?,?,?,?,?)",
                                    (new_h, new_m % 60, timetable,
                                     signature, variant_id, course_id, current_stop, int(low)))

            except IndexError:
                pass


def db_setup():
    cursor.execute("DROP TABLE IF EXISTS departures")
    cursor.execute("DROP TABLE IF EXISTS stops")
    db.commit()
    cursor.execute("CREATE TABLE stops"
                   "(code integer primary key, stop_name string, latitude real, longitude real)")
    cursor.execute("CREATE TABLE departures(time_h smallint, time_m smallint, timetable smallint,"
                   " line string, variant smallint, course_id integer, stop integer, low smallint,"
                   " foreign key(stop) references stops(code))")
    db.commit()


def fetch_all():
    download_timetables()
    db_setup()
    fetch_stops()
    fetch_lines()
    fetch_departures()
    db.commit()
    db.close()
