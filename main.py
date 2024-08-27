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


def generate_sensor_data(num_records: int, last_data: datetime, interval: int, filename: str):
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


if __name__ == '__main__':
    file = "./sensor_data.csv"
    last_data_timestamp = datetime.now()
    interval = 8
    records = 100
    if not os.path.exists(file):
        generate_sensor_data(records, last_data_timestamp, interval, file)
    else:
        os.remove(file)
        generate_sensor_data(records, datetime.now(), interval, file)

    # Cleaning duplicates to get unique information
    df = pd.read_csv(file).drop_duplicates(subset='SensorID')

    # Obtaining coordinates for each sensor
    df = df[['SensorID', 'Latitude', 'Longitude']]

    # Generating a new map centered in Lima
    m = folium.Map(location=[-12.046374, -77.042793], zoom_start=6)
    for i, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['SensorID']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    m.save("sensor_map.html")
    print(df)
    print("Archivo 'sensor_data.csv' generado con éxito.")
