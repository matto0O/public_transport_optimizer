import googlemaps

api_key = 'AIzaSyD3flnJCqT7n5-NC1f_Qxyn8jdP0TNssc0'
gmaps = googlemaps.Client(api_key)


def get_location(place):
    return tuple(gmaps.place(gmaps.find_place(place, 'textquery')['candidates'][0]['place_id'])['result']['geometry']['location'].values())


def get_time_to_location(origin, destination):
    return str(gmaps.directions(origin, destination, mode="walking")).\
        split("'duration': {'text': '")[1].split("', 'value'")[0]
