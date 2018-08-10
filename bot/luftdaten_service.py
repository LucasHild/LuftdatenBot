import requests


def get_value(sensor_id):
    """Get value from Luftdaten-API"""
    url = f"https://api.luftdaten.info/v1/sensor/{sensor_id}/"
    r = requests.get(url, headers={"Host": "api.luftdaten.info"})

    if not r.json():
        return None

    value = r.json()[-1]["sensordatavalues"][0]["value"]
    return float(value)


def get_all_sensors():
    r = requests.get("https://api.luftdaten.info/static/v2/data.dust.min.json")
    return r.json()
