# pyinstaller -w --onefile --console --name="Ambient Sensor" "Ambient Sensor.py"
import datetime
import os
from time import sleep
from meteostat import Point, Hourly
from datetime import timedelta, datetime
import warnings
warnings.filterwarnings("ignore")

class AmbientSensor:
    def __init__(self, longitude, latitude):
        self.longitutde = longitude
        self.latitude = latitude

    def collect_latest(self):
        try:
            start, end = datetime.today()- timedelta(days=1), datetime.today()
            data = Hourly(Point(self.longitutde, self.latitude), start = start, end = end)
            data = data.fetch()
            data = data[['temp', 'rhum']]
            temperature = data.iloc[-1][0]
            humidity = data.iloc[-1][1]
            points = [{"data": temperature, "pointName": "Outside Air Temperature", "status": "ok"},
                    {"data": humidity, "pointName": "Outside Air Humidity", "status": "ok"}]
            print(f"Ambient Sensor ::: Data Collection ::: Success ::: {points}")
            return points
        except Exception as e:
            print(f"Ambient Sensor ::: Data Collection ::: Error ::: {e}")
            return None

def main():
    result = None
    while True:
        try:
            if result:
                print (f"Last Search Result: {result}\n")
            longitude = float(input("Enter longitude: "))
            latitude = float(input("Enter latitude: "))
            result = AmbientSensor(longitude=longitude, latitude=latitude).collect_latest()
            os.system('cls')
        except Exception as e:
            print(f"Error: {e}")
            sleep(5)
            os.system('cls')

if __name__ == "__main__":
    main()