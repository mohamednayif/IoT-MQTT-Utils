# pyinstaller -w --onefile --name "Virtual Sensors" "Virtual Sensors.py"
import asyncio
import datetime
from meteostat import Point, Hourly
from datetime import timedelta, datetime
import aiohttp
import pandas as pd
from itertools import cycle
import requests
import os
from MQTT import MQTT
from constants import *
import warnings
warnings.filterwarnings("ignore")

class AirQualitySensors:
    def __init__(self, name, MQTT: MQTT, identifier, openaqid, delay=60):
        self.delay = delay
        self.name = name
        self.MQTT = MQTT
        self.identifier = identifier
        self.openaqid = openaqid
        self.aqi_pm25_breakpoints = [    (0, 12, 50),    (12, 35, 100),    (35, 55, 150),    (55, 150, 200),    (150, 250, 300),    (250, 350, 400),    (350, 500, 500)]
        self.aqi_pm10_breakpoints = [    (0, 54, 50),    (54, 154, 100),    (154, 254, 150),    (254, 354, 200),    (354, 424, 300),    (424, 504, 400),    (504, 604, 500)]
        self.aqi_co_breakpoints = [    (0, 4.4, 50),    (4.4, 9.4, 100),    (9.4, 12.4, 150),    (12.4, 15.4, 200),    (15.4, 30.4, 300),    (30.4, 40.4, 400),    (40.4, 50.4, 500)]
        self.aqi_o3_breakpoints = [    (0, 0.054, 50),    (0.054, 0.070, 100),    (0.070, 0.085, 150),    (0.085, 0.105, 200),    (0.105, 0.200, 300),    (0.200, 0.605, 400),    (0.605, 0.805, 500)]
        self.aqi_so2_breakpoints = [    (0, 0.035, 50),    (0.035, 0.075, 100),    (0.075, 0.185, 150),    (0.185, 0.304, 200),    (0.304, 0.604, 300),    (0.604, 0.804, 400),    (0.804, 1.004, 500)]
        self.aqi_no2_breakpoints = [    (0, 0.053, 50),    (0.053, 0.100, 100),    (0.100, 0.360, 150),    (0.360, 0.649, 200),    (0.649, 1.249, 300),    (1.249, 1.649, 400),    (1.649, 1.999, 500)]
        self.headers = {"accept": "application/json"}
        self.have_latest = False
        self.sleep_time = 60

    async def collect_latest(self): 
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.openaq.org/v2/latest/{self.openaqid}?limit=1&page=1&offset=0&sort=desc&radius=1000&order_by=lastUpdated&dumpRaw=false", headers=self.headers) as response:
                    response = await response.json()
            measurements = {} 
            for i in range(len(response['results'][0]['measurements'])):
                measurements[response['results'][0]['measurements'][i]['parameter']] = response['results'][0]['measurements'][i]['value']

            AQI_PM10 = self.calculate_aqi(measurements['pm10'], self.aqi_pm10_breakpoints)
            AQI_PM25 = self.calculate_aqi(measurements['pm25'], self.aqi_pm25_breakpoints)
            AQI_CO = self.calculate_aqi(measurements['co'], self.aqi_co_breakpoints)
            AQI_O3 = self.calculate_aqi(measurements['o3'], self.aqi_o3_breakpoints)
            AQI_SO2 = self.calculate_aqi(measurements['so2'], self.aqi_so2_breakpoints)
            AQI_NO2 = self.calculate_aqi(measurements['no2'], self.aqi_no2_breakpoints)
            AQI = max(AQI_PM10, AQI_PM25, AQI_CO, AQI_O3, AQI_SO2, AQI_NO2)    

            points = [
                        {"data": measurements['pm10'], "pointName": "PM 10", "status": "ok"},
                        {"data": measurements['o3'], "pointName": "O3", "status": "ok"},
                        {"data": measurements['co'], "pointName": "CO", "status": "ok"},
                        {"data": measurements['so2'], "pointName": "SO2", "status": "ok"},
                        {"data": measurements['pm25'], "pointName": "PM 2.5", "status": "ok"},
                        {"data": measurements['no2'], "pointName": "NO2", "status": "ok"},
                        {"data": AQI, "pointName": "AQI", "status": "ok"},
                    ]  
            self.have_latest = True
            # print(f"Air Quality Sensor ::: Data Collection ::: Success ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute} ::: {points}")
            return points
        except Exception as e:
            print(f"Air Quality Sensor ::: Data Collection ::: Error ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute} ::: {e}")
            return None
    
    async def publish_latest(self):
        error_count = 0
        while True:
            try:
                self.now = datetime.now() 
                if self.now.minute % self.delay <= 1: 
                    points = await self.collect_latest()
                    self.MQTT.publish(points=points, identifier=self.identifier)
                    print(f"Air Quality Sensor ::: Publish Latest ::: Success ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute}")
                    self.sleep_time = 30  
                    error_count = 0
                else:
                    self.sleep_time = 60
            except Exception as e:
                print(f"Air Quality Sensor ::: Publish Latest ::: Error ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute} ::: {e}")
                error_count += 1
                if error_count > 5:
                    break
            await asyncio.sleep(self.sleep_time)
    
    def calculate_aqi(self, concentration, aqi_breakpoints):
        """
        Calculates the AQI using the formula provided by the US EPA.
        
        Parameters:
        - concentration: The concentration of PM2.5 in the air (µg/m3)
        - aqi_breakpoints: A list of AQI breakpoints for PM2.5 in the form [(lower, upper, index), ...]
        
        Returns:
        - The AQI as an integer.
        """
        for i, (a, b, c) in enumerate(aqi_breakpoints):
            if concentration >= a and concentration <= b:
                return int(((c - a) / (b - a)) * (concentration - a) + a)
        return None

class AmbientSensor:
    def __init__(self, longitude, latitude, identifier, name, MQTT, delay=60):
        self.longitutde = longitude
        self.latitude = latitude
        self.identifier = identifier
        self.name = name
        self.MQTT = MQTT
        self.delay = delay
        self.sleep_time = 60

    async def collect_latest(self):
        try:
            start, end = datetime.today()- timedelta(days=1), datetime.today()
            data = Hourly(Point(self.longitutde, self.latitude), start = start, end = end)
            data = data.fetch()
            data = data[['temp', 'rhum']]
            temperature = data.iloc[-1][0]
            humidity = data.iloc[-1][1]
            points = [{"data": temperature, "pointName": "Outside Air Temperature", "status": "ok"},
                    {"data": humidity, "pointName": "Outside Air Humidity", "status": "ok"}]
            # print(f"Ambient Sensor ::: Data Collection ::: Success ::: {self.name} ::: {self.identifier} ::: {points}")
            return points
        except Exception as e:
            print(f"Ambient Sensor ::: Data Collection ::: Error ::: {self.name} ::: {self.identifier} ::: {e}")
            return None
    
    async def publish_latest(self):
        while True:
            try:
                self.now = datetime.now()
                if self.now.minute % self.delay <= 1:
                    points = await self.collect_latest()
                    self.MQTT.publish(points=points, identifier=self.identifier)
                    print(f"Ambient Sensor ::: Publish Latest ::: Success ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute}")
                    self.sleep_time = 30
                    error_count = 0
                else:
                    self.sleep_time = 60
            except Exception as e:
                print(f"Ambient Sensor ::: Publish Latest ::: Error ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute} ::: {e}")
                error_count += 1
                if error_count > 5:
                    break
            await asyncio.sleep(self.sleep_time)

class NoiseSensor:
    def __init__(self, identifier, name, MQTT, data_noise_sensor, delay=3):
        self.identifier = identifier
        self.name = name
        self.MQTT = MQTT
        self.delay = delay
        self.data_noise_sensor = data_noise_sensor
        self.sleep_time = 60
        self.data_noise = noise_data[noise_data[NOISE_SENSOR_DEVICE_ID_COLUMN] == self.data_noise_sensor][NOISE_SENSOR_DATA_COLUMN].tolist()

    async def collect_latest(self):
        try:
            try:
                self.noise = self.data_noise.pop(0)
            except:
                # print(f"Noise Sensor ::: Data Collection ::: Bucket Empty ::: {self.name} ::: {self.identifier} ::: Loading New Bucket")
                self.data_noise = noise_data[noise_data[NOISE_SENSOR_DEVICE_ID_COLUMN] == self.data_noise_sensor][NOISE_SENSOR_DATA_COLUMN].tolist()
                self.noise = self.data_noise.pop(0)
            points = [{"data": self.noise, "pointName": "Level", "status": "ok"}]
            # print(f"Noise Sensor ::: Data Collection ::: Success ::: {self.name} ::: {self.identifier} ::: {points}")
            return points
        except Exception as e:
            print(f"Noise Sensor ::: Data Collection ::: Error ::: {self.name} ::: {self.identifier} ::: {e}")
            return None
    
    async def publish_latest(self):
        while True:
            try:
                self.now = datetime.now()
                if self.now.minute % self.delay <= 1:
                    points = await self.collect_latest()
                    self.MQTT.publish(points=points, identifier=self.identifier)
                    print(f"Noise Sensor ::: Publish Latest ::: Success ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute}")
                    self.sleep_time = 30
                    error_count = 0
                else:
                    self.sleep_time = 60
            except Exception as e:
                print(f"Noise Sensor ::: Publish Latest ::: Error ::: {self.name} ::: {self.identifier} ::: {self.now.hour}:{self.now.minute} ::: {e}")
                error_count += 1
                if error_count > 5:
                    break
            await asyncio.sleep(self.sleep_time)
    
async def main():
    MQTT_CLIENT = MQTT()
    MQTT_CLIENT.connect()
    tasks = []

    try:
        air_quality_sensors = pd.read_csv(f"{ASSETS_PATH}{AIR_QUALITY_SENSOR_FILE}") 
        air_quality_sensors = air_quality_sensors[air_quality_sensors[OPENAQID_COLUMN].notna()]
        for i in range(len(air_quality_sensors)):
            task = asyncio.create_task(AirQualitySensors(name = air_quality_sensors[DISPLAY_NAME_COLUMN][i], MQTT=MQTT_CLIENT, identifier=air_quality_sensors[IDENTIFIER_COLUMN][i], openaqid=int(air_quality_sensors[OPENAQID_COLUMN][i])).publish_latest())
            tasks.append(task)
    except Exception as e:
        print(f"Air Quality Sensor ::: Main ::: Error ::: {e}")
    
    try:
        ambient_temperature_sensors = pd.read_csv(f"{ASSETS_PATH}{AMBIENT_SENSOR_FILE}")
        ambient_temperature_sensors = ambient_temperature_sensors[ambient_temperature_sensors[LONGITUDE_COLUMN].notna() & ambient_temperature_sensors[LATITUDE_COLUMN].notna()]
        for i in range(len(ambient_temperature_sensors)):
            task = asyncio.create_task(AmbientSensor(name = ambient_temperature_sensors[DISPLAY_NAME_COLUMN][i], MQTT=MQTT_CLIENT, identifier=ambient_temperature_sensors[IDENTIFIER_COLUMN][i], longitude=ambient_temperature_sensors[LONGITUDE_COLUMN][i], latitude=ambient_temperature_sensors[LATITUDE_COLUMN][i]).publish_latest())
            tasks.append(task)
    except Exception as e:
        print(f"Ambient Sensor ::: Main ::: Error ::: {e}")
    
    try:
        global noise_data        
        if not os.path.isfile(f"{ASSETS_PATH}{NOISE_SENSOR_DATA_FILE}"):
            response = requests.get(NOISE_DATA_URL)
            with open(f"{ASSETS_PATH}{NOISE_SENSOR_DATA_FILE}", 'wb') as f:
                f.write(response.content)
            del response
        noise_data = pd.read_csv(f"{ASSETS_PATH}{NOISE_SENSOR_DATA_FILE}", compression='gzip', header=0, 
                 usecols=USECOLS, dtype=NOISE_DATA_DTYPES,
                 parse_dates=[READABLE_TIME_COLUMN], sep=',').drop(columns=[READABLE_TIME_COLUMN])
        noise_temperature_sensors = pd.read_csv(f"{ASSETS_PATH}{NOISE_SENSOR_FILE}")
        data_noise_sensors = noise_data[NOISE_SENSOR_DEVICE_ID_COLUMN].unique().tolist()
        noise_sensors = noise_temperature_sensors.to_dict('records')
        izip_noise_sensor = zip(cycle(data_noise_sensors), noise_sensors)
        for data_noise_sensor_name, noise_sensors in izip_noise_sensor:
            task = asyncio.create_task(
                    NoiseSensor(name = noise_sensors[DISPLAY_NAME_COLUMN], identifier=noise_sensors[IDENTIFIER_COLUMN], data_noise_sensor = data_noise_sensor_name, MQTT=MQTT_CLIENT).publish_latest())
            tasks.append(task)        
    except Exception as e:
        print(f"Noise Sensor ::: Main ::: Error ::: {e}")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())