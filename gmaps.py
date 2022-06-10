import googlemaps

with open("gmaps_key", 'r') as file:
    gmaps = googlemaps.Client(file.read())


def get_location(place):
    return tuple(gmaps.place(gmaps.find_place(place, 'textquery')['candidates'][0]['place_id'])['result']['geometry']['location'].values())


def get_time_to_location(origin, destination):
    helper = str(gmaps.directions(origin, destination, mode="walking")).\
        split("'duration': {'text': '")[1].split("', 'value'")[0].split(" ")
    if len(helper) > 4 or len(helper) < 2:
        raise ValueError("Argument not in valid range")
    elif len(helper) == 4:
        return int(helper[0]) * 60 + int(helper[2])
    else:
        return int(helper[0])

