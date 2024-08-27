import csv
import os
import random
import pandas as pd
import folium
from datetime import datetime, timedelta

sensor_coordinates = {}


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

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["SensorID", "Timestamp", "CO (ppm)", "O3 (ppm)", "Latitude", "Longitude"])

        for i in range(num_records):
            # Assuming that sensors sends data every 8 hours
            time_interval = timedelta(hours=interval)
            timestamp = (last_data - i * time_interval)
            # ISO format is a date format that JSON supports (this format might make easier future implementations)
            timestamp_iso = timestamp.isoformat()
            sensor_id = int(gen_random_value(0, 10, 0))

            # Assuming that coordinates don't change
            # There's a necessity to store values in a global variable
            global sensor_coordinates
            if sensor_id not in sensor_coordinates:
                lat = gen_random_value(-9, -10, 6)
                lon = gen_random_value(-75, -77, 6)
                sensor_coordinates[sensor_id] = (lat, lon)
            else:
                lat, lon = sensor_coordinates[sensor_id]

            co = gen_random_value(0, 50.5, 3)
            o3 = gen_random_value(0.000, 0.400, 3)
            writer.writerow([f'Sensor{sensor_id}', timestamp_iso, co, o3, lat, lon])


def classify_air_quality(co_value: float, o3_value: float):
    quality_levels = {"level1": ("green", "Buena"),
                      "level2": ("beige", "Moderada"),
                      "level3": ("orange", "Dañina a la salud para grupos sensibles"),
                      "level4": ("red", "Dañina a la salud"),
                      "level5": ("purple", "Muy dañina a la salud"),
                      "level6": ("darkred", "Peligrosa")
                      }
    co_level, color = (
        quality_levels["level1"] if co_value <= 4.4 else
        quality_levels["level2"] if co_value <= 9.4 else
        quality_levels["level3"] if co_value <= 12.4 else
        quality_levels["level4"] if co_value <= 15.4 else
        quality_levels["level5"] if co_value <= 30.4 else
        quality_levels["level6"]
    )

    o3_level, color = (
        quality_levels["level1"] if o3_value <= 0.059 else
        quality_levels["level2"] if o3_value <= 0.075 else
        quality_levels["level3"] if o3_value <= 0.095 else
        quality_levels["level4"] if o3_value <= 0.115 else
        quality_levels["level5"] if o3_value <= 0.374 else
        quality_levels["level6"]
    )

    general_level, color = (
        quality_levels["level1"] if 'Buena' in (co_level, o3_level) else
        quality_levels["level2"] if 'Moderada' in (co_level, o3_level) else
        quality_levels["level3"] if 'Dañina a la salud para grupos sensibles' in (co_level, o3_level) else
        quality_levels["level4"] if 'Dañina a la salud' in (co_level, o3_level) else
        quality_levels["level5"] if o3_value <= 0.374 else
        quality_levels["level6"]
    )

    return general_level, color


if __name__ == '__main__':
    file = "./sensor_data.csv"
    last_data_timestamp = datetime.now()
    interval = 8
    records = 100
    if not os.path.exists(file):
        gen_sensor_data(records, last_data_timestamp, interval, file)
        print(f"Archivo {file} generado con éxito.")

    else:
        os.remove(file)
        gen_sensor_data(records, datetime.now(), interval, file)
        print(f"Archivo {file} generado con éxito.")

    # Sorting dataframe from the most recent sensor data to the oldest
    df = (pd.read_csv(file)
          # .drop_duplicates(subset="SensorID")
          .sort_values(by="Timestamp", ascending=False)
          )
    sensor_positions = df.groupby("SensorID")[["Latitude", "Longitude"]].first()
    processed_values = df.groupby("SensorID")[["CO (ppm)", "O3 (ppm)"]].median()
    data = processed_values.join(sensor_positions).reset_index()

    print(data)

    # Generate a new map
    m = folium.Map(location=[-12.046374, -77.042793], zoom_start=6)

    # Creating a marker for each sensorID
    # When clicking to the marker it shows a popup with last information
    for i, row in data.iterrows():
        info_tuple = classify_air_quality(row["CO (ppm)"], row["O3 (ppm)"])
        row_df = pd.DataFrame(data=[row], columns=["SensorID", "CO (ppm)", "O3 (ppm)", "Latitude", "Longitude"])
        html = row_df.to_html(classes="table table-striped table-hover table-condensed table-responsive", index=False)
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"{html}",
            icon=folium.Icon(color=info_tuple[0], icon="info-sign")
        ).add_to(m)

    # Save map as HTML
    m.save("sensor_map.html")
