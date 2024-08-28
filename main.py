import csv
import os
import random
import threading
import time

import pandas as pd
import folium
from datetime import datetime, timedelta

sensor_coordinates = {}
legend_html = '''<div style=" position: fixed; bottom: 50px; left: 50px; width: 300px; height: 200px; border:2px 
    solid grey; z-index:9999; font-size:14px; "> &nbsp; <strong>Leyenda</strong> <br> &nbsp; <i class="fa 
    fa-map-marker fa-2x" style="color:green"></i>&nbsp; Buena <br> &nbsp; <i class="fa fa-map-marker fa-2x" 
    style="color:beige"></i>&nbsp; Moderada <br> &nbsp; <i class="fa fa-map-marker fa-2x" 
    style="color:orange"></i>&nbsp; Dañina a la salud para grupos sensibles <br> &nbsp; <i class="fa fa-map-marker 
    fa-2x" style="color:red"></i>&nbsp; Dañina a la salud <br> &nbsp; <i class="fa fa-map-marker fa-2x" 
    style="color:purple"></i>&nbsp; Muy dañina a la salud <br> &nbsp; <i class="fa fa-map-marker fa-2x" 
    style="color:darkred"></i>&nbsp; Peligrosa <br> </div>'''


def gen_random_value(min_val: float, max_val: float, digits: int):
    """
    Generate a random value between min_val and max_val
    :param min_val: minimum value
    :param max_val: maximum value
    :param digits: number of digits
    :return: random number between min_val and max_val
    """
    return round(random.uniform(min_val, max_val), digits)


def gen_sensor_data(num_records: int, last_data: datetime, interval: int, filename: str):
    """
    Generates a CSV file to simulate sensor's data
    :param num_records: number of records to generate
    :param last_data: last data timestamp
    :param interval: interval between records
    :param filename: name of the CSV file
    :return: file_path
    """

    while True:
        last_data_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data = []
        for _ in range(10):
            sensor_id = random.randint(0, 10)
            lat, lon = sensor_coordinates.get(sensor_id, (gen_random_value(-9, -10, 6), gen_random_value(-75, -77, 6)))
            sensor_coordinates[sensor_id] = (lat, lon)
            co = gen_random_value(0, 19, 3)
            o3 = gen_random_value(0.000, 0.200, 3)
            timestamp = last_data_timestamp
            new_data.append([f'Sensor{sensor_id}', timestamp, co, o3, lat, lon])

        with open(filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(new_data)
        print(f"New datapoint for Sensor{sensor_id}: CO = {co}, O3 = {o3}, Lat = {lat}, Lon = {lon}, "
              f"timestamp = {timestamp}")
        time.sleep(interval)


def classify_air_quality(co_value: float, o3_value: float):
    """
    Given a CO value and a O3 make a evaluation of the air quality
    :param co_value: float that indicates CO value
    :param o3_value: float that indicates O3 value
    :return: Tuple with a color and a status (Buena, Moderada, etc)
    """
    quality_levels = {"level1": ("green", "Buena"),
                      "level2": ("beige", "Moderada"),
                      "level3": ("orange", "Dañina a la salud para grupos sensibles"),
                      "level4": ("red", "Dañina a la salud"),
                      "level5": ("purple", "Muy dañina a la salud"),
                      "level6": ("darkred", "Peligrosa")
                      }
    color, co_level = (
        quality_levels["level1"] if co_value <= 4.4 else
        quality_levels["level2"] if co_value <= 9.4 else
        quality_levels["level3"] if co_value <= 12.4 else
        quality_levels["level4"] if co_value <= 15.4 else
        quality_levels["level5"] if co_value <= 30.4 else
        quality_levels["level6"]
    )

    color, o3_level = (
        quality_levels["level1"] if o3_value <= 0.059 else
        quality_levels["level2"] if o3_value <= 0.075 else
        quality_levels["level3"] if o3_value <= 0.095 else
        quality_levels["level4"] if o3_value <= 0.115 else
        quality_levels["level5"] if o3_value <= 0.374 else
        quality_levels["level6"]
    )

    color, general_level, = (
        quality_levels["level1"] if 'Buena' in (co_level, o3_level) else
        quality_levels["level2"] if 'Moderada' in (co_level, o3_level) else
        quality_levels["level3"] if 'Dañina a la salud para grupos sensibles' in (co_level, o3_level) else
        quality_levels["level4"] if 'Dañina a la salud' in (co_level, o3_level) else
        quality_levels["level5"] if o3_value <= 0.374 else
        quality_levels["level6"]
    )

    return color, general_level


def build_map(file: str):
    """
    Reads the CSV file and generates a map with markers for each sensor
    :param file: filename to read
    :return:
    """
    df = (pd.read_csv(file)
          .sort_values(by="Timestamp", ascending=False)
          )

    data = df.groupby("SensorID").first().reset_index()
    print(data)

    # Generate a new map
    m = folium.Map(location=[-9.56, -75.2], zoom_start=7)

    for i, row in data.iterrows():
        info_tuple = classify_air_quality(row["CO (ppm)"], row["O3 (ppm)"])
        row_df = pd.DataFrame({
            "SensorID": [row["SensorID"]],
            "CO (ppm)": [row["CO (ppm)"]],
            "O3 (ppm)": [row["O3 (ppm)"]],
            "Latitude": [row["Latitude"]],
            "Longitude": [row["Longitude"]],
            "Air quality": [info_tuple[1]],
            "Timestamp": [row["Timestamp"]]
        })
        html = row_df.to_html(classes="table table-striped table-hover table-condensed table-responsive", index=False)
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{html}",
            icon=folium.Icon(color=info_tuple[0], icon="info-sign")
        ).add_to(m)

    m.get_root().html.add_child(folium.Element(legend_html))
    m.save("./sensor_map.html")


if __name__ == '__main__':
    try:
        file = "./sensor_data.csv"
        interval = 8

        # Create just the header for the CSV file (emulating a database)
        if not os.path.exists(file):
            with open(file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["SensorID", "Timestamp", "CO (ppm)", "O3 (ppm)", "Latitude", "Longitude"])

        # Generating data as a background process
        data_thread = threading.Thread(target=gen_sensor_data, args=(0, datetime.now(), interval, file))
        data_thread.start()

        # Building the map every 60 sec
        while True:
            print("arme mapa")
            time.sleep(10)
            build_map(file)
            time.sleep(50)
    except KeyboardInterrupt:
        print("Program finished")
