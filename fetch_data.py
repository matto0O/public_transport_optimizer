import pandas as pd
from zipfile import ZipFile
import os
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass

stops = list()
lines = list()


@dataclass(frozen=True)
class Stop:
    code: str
    name: str
    latitude: str
    longitude: str

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


@dataclass(frozen=True)
class Line:
    signature: str
    variants: list

    def __repr__(self):
        return "Linia {}\n{}".format(self.signature, self.variants[0])


def find_stop_by_id(code):
    for stop in stops:
        if stop.code == code:
            return stop
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


def fetch_all():
    # unpack_timetable()
    fetch_stops()
    fetch_lines()
