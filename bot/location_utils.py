from math import atan2, cos, radians, sin, sqrt

import bot.luftdaten_service as luftdaten_service


def get_closest_sensor(latitude, longitude):
    sensors = luftdaten_service.get_all_sensors()

    # Get the sensor with the smallest distance to search_pos
    lowest_distance = float('inf')
    closest_sensor_id = None
    closest_sensor_latitude = None
    closest_sensor_longitude = None

    for sensor in sensors:
        sensor_id = int(sensor["sensor"]["id"])
        sensor_latitude = float(sensor["location"]["latitude"])
        sensor_longitude = float(sensor["location"]["longitude"])

        # TODO: Use distance()
        dist = sqrt(((latitude - sensor_latitude) **
                     2) + ((longitude - sensor_longitude) ** 2))

        if dist < lowest_distance:
            lowest_distance = dist
            closest_sensor_id = sensor_id
            closest_sensor_latitude = sensor_latitude
            closest_sensor_longitude = sensor_longitude

    return {
        "sensor_id": closest_sensor_id,
        "latitude": closest_sensor_latitude,
        "longitude": closest_sensor_longitude
    }


def distance(search_pos, closest_sensor_pos):
    # Calculate distance between sensor_pos and closest_sensor
    lat1, lon1 = search_pos
    lat2, lon2 = closest_sensor_pos
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * \
        cos(radians(lat2)) * sin(dlon / 2) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = round(6371 * c)
    if distance < 1000:
        distance *= 1000
        distance = str(distance) + "m"
    elif distance >= 1000:
        distance = str(distance) + "km"

    return distance
