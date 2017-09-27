from math import atan2, cos, radians, sin, sqrt


def closest_sensor(search_pos, sensors):
    # Get the sensor with the smallest distance to search_pos
    low_dist = float('inf')
    closest_sensor = None
    closest_sensor_pos = None
    for sensor in sensors:
        sensor_id = int(sensor["sensor"]["id"])
        sensor_pos = (float(sensor["location"]["latitude"]), float(sensor["location"]["longitude"]))

        # Calculate the distance between this sensor (i) and search_pos
        dist = sqrt(((search_pos[0] - sensor_pos[0]) ** 2) + ((search_pos[1] - sensor_pos[1]) ** 2))

        # If distance of this sensor (i) is smaller then the smallest, set new closest_sensor
        if dist < low_dist:
            low_dist = dist
            closest_sensor = sensor_id
            closest_sensor_pos = sensor_pos

    return closest_sensor, closest_sensor_pos


def distance(search_pos, closest_sensor_pos):
    # Calculate distance between sensor_pos and closest_sensor
    lat1, lon1 = search_pos
    lat2, lon2 = closest_sensor_pos
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = round(6371 * c)
    if distance < 1000:
        distance *= 1000
        distance = str(distance) + "m"
    elif distance >= 1000:
        distance = str(distance) + "km"

    return distance