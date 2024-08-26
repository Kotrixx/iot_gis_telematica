import csv
import random
from datetime import datetime, timedelta


def gen_random_value(min_val: float, max_val: float, digits: int):
    """
    Generate a random value between min_val and max_val
    :param min_val: minimum value
    :param max_val: maximum value
    :param digits: number of digits
    :return: random number between min_val and max_val
    """
    return round(random.uniform(min_val, max_val), digits)


def generate_sensor_data(num_records: int, last_data: datetime, interval: int):
    """
    Generates a CSV file to simulate sensor's data
    :param num_records: number of records to generate
    :param last_data: last data timestamp
    :param interval: interval between records
    :return: file_path
    """
    with open('sensor_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["SensorID", "Timestamp", "CO (ppm)", "O3 (ppm)", "Latitude", "Longitude"])

        for i in range(num_records):
            # Assuming that sensors sends data every 8 hours
            time_interval = timedelta(hours=interval)
            timestamp = (last_data - i * time_interval)
            # ISO format is a date format that JSON supports (this format might make easier future implementations)
            timestamp_iso = timestamp.isoformat()
            sensor_id = int(gen_random_value(0, 10, 0))
            lat = gen_random_value(-10.27167, -13.32111, 6)
            lon = gen_random_value(-75.50500, -77.88389, 6)
            co = gen_random_value(0, 50.5, 3)
            o3 = gen_random_value(0.000, 0.400, 3)
            writer.writerow([f'Sensor{sensor_id}', timestamp_iso, co, o3, lat, lon])


if __name__ == '__main__':
    generate_sensor_data(100, datetime.now(), 8)
    print("Archivo 'sensor_data.csv' generado con éxito.")
