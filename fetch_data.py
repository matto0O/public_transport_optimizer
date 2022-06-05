import pandas as pd
from zipfile import ZipFile
import os
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import datetime

stops = list()
lines = list()


@dataclass(frozen=True)
class Line:
    signature: str
    variants: list

    def __repr__(self):
        return "Linia {}\n{}".format(self.signature, self.variants[0])

    def __str__(self):
        return f"Linia {self.signature}"


@dataclass(frozen=True)
class Departure:
    line: Line
    time: datetime.time
    timetable: int
    low: bool = False

    def __repr__(self):
        match self.timetable:
            case 0:
                days = 'dni robocze'
            case 1:
                days = 'sobota'
            case _:
                days = 'święta'
        result = f"{self.line.__str__()}\n{self.time} - {days}"
        if self.low:
            result += ", niskopodłogowy"
        return result


class Stop:
    def __init__(self, code: str, name: str, latitude: str, longitude: str):
        self.__code = code
        self.__name = name
        self.__latitude = latitude
        self.__longitude = longitude
        self.departures = list()

    def append_departure(self, departure: Departure):
        self.departures.append(departure)

    @property
    def code(self):
        return self.__code

    @property
    def name(self):
        return self.__name

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.__code == other.__code
        else:
            return NotImplementedError

    def __hash__(self):
        return hash(self.__code)

    def __repr__(self):
        return "{} - {} - {}, {}".format(self.code, self.name, self.latitude, self.longitude)


@dataclass(frozen=True)
class Variant:
    start: Stop
    end: Stop
    intervals: dict

    def __repr__(self):
        result = "{} - {}\n".format(self.start.name, self.end.name)
        for stop in self.intervals.keys():
            result += stop.name + " - "
        return result[:-3]


def find_stop_by_id(code):
    for stop in stops:
        if stop.code == code:
            return stop
    return None


def find_line_by_signature(signature):
    for line in lines:
        if line.signature == signature:
            return line
    return None


def unpack_timetable():
    target = "XML-rozkladyjazdy.zip"
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
        stops.append(Stop(elem[1][1], elem[1][2], elem[1][3], elem[1][4]))


def fetch_lines():
    for file in os.listdir("XML-rozkladyjazdy"):
        tree = ET.parse(f"XML-rozkladyjazdy\{file}")
        root = tree.getroot()
        variants = list()
        for child in root[0]:
            intervals = dict()
            for times in child[0][0]:
                intervals[find_stop_by_id(times.attrib['id'])] = times.attrib['czas']
            stops_helper = list(intervals.keys())
            variants.append(Variant(stops_helper[0], stops_helper[-1], intervals))
        lines.append(Line(root[0].attrib['nazwa'], variants))


def fetch_departures():
    for file in os.listdir("XML-rozkladyjazdy"):
        tree = ET.parse(f"XML-rozkladyjazdy\{file}")
        line = tree.getroot()
        for variant in line[0]:
            for stop in variant:
                current_stop = find_stop_by_id(stop.attrib['id'])
                try:
                    for day in stop[1]:
                        match day.attrib['nazwa']:
                            case 'w dni robocze':
                                timetable = 0
                            case 'Sobota':
                                timetable = 1
                            case _:
                                timetable = 2
                        for hour in day:
                            h = hour.attrib['h']
                            for minute in hour:
                                m = minute.attrib['m']
                                low = False
                                if len(minute.attrib) > 1:
                                    low = minute.attrib['ozn'] == 'N'
                                d = Departure(find_line_by_signature(line[0].attrib['nazwa']),
                                            datetime.time(int(h % 24), int(m % 60)), timetable, low)
                                # TODO consider departures post-midnight
                                current_stop.append_departure(d)
                except IndexError:
                    pass


def fetch_all():
    # unpack_timetable()
    fetch_stops()
    fetch_lines()
    fetch_departures()
