ASSETS_PATH = "assets/"

# MQTT Credentials
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"
TOPIC = "TOPIC"
CREDENTIALS_FILE = "credentials.json"

# Credentials Installer
CREDENTIALS_INSTALLER = "CredentialsInstaller.exe"

# Message Size Optimizer
STANDARD_POINT_FILE = "Standard Point Name.csv" # Standard Point Name.csv is a csv file with the following columns: Point Name, point_shorten
POINT_SHORTEN_COLUMN = "point_shorten"
POINT_NAME_COLUMN = "Point Name"
MODULE_SHORTEN = {'reason': 'r', 'time': 't', 'points': 'p', 'pointName': 'pt', 'data': 'd', 'status': 's', 'CHANGE_OF_VALUE': 'COV', 'REALTIME_UPDATE': 'RU'}

# Common Columns
IDENTIFIER_COLUMN = "Identifier"
DISPLAY_NAME_COLUMN = "Display Name"

# Noise Sensor
NOISE_SENSOR_DATA_FILE = 'Noise Sensor Data.csv.gz'
NOISE_SENSOR_DEVICE_ID_COLUMN = "dev-id"
NOISE_DATA_URL = 'https://iot.fvh.fi/opendata/noise/LAeq-2020-all.csv.gz'
NOISE_SENSOR_FILE = 'Noise Sensors.csv' # Noise Sensors.csv is a csv file with the following columns: Display Name, Identifier
READABLE_TIME_COLUMN = "readable_time"
NOISE_SENSOR_DATA_COLUMN = "dBA"
USECOLS = [READABLE_TIME_COLUMN, NOISE_SENSOR_DATA_COLUMN, NOISE_SENSOR_DEVICE_ID_COLUMN]
NOISE_DATA_DTYPES = {NOISE_SENSOR_DATA_COLUMN: 'float', NOISE_SENSOR_DEVICE_ID_COLUMN: 'str'}

# Air Quality Sensor
AIR_QUALITY_SENSOR_FILE = 'Air Quality Sensors.csv' # Air Quality Sensors.csv is a csv file with the following columns: Display Name, Identifier, openaqid
OPENAQID_COLUMN = "openaqid"

# Ambient Sensor
AMBIENT_SENSOR_FILE = 'Ambient Sensors.csv' # Ambient Sensors.csv is a csv file with the following columns: Display Name, Identifier, openweathermapid
LONGITUDE_COLUMN = "Longitude"
LATITUDE_COLUMN = "Latitude"