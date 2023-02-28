from MQTT import MQTT

MQTT_CLIENT = MQTT()
MQTT_CLIENT.connect()

points = [{"data": 40, "pointName": "Gas Temperature", "status": "ok"},
# {"data": 'Running', "pointName": "Pre Filter Status", "status": "ok"},
]

MQTT_CLIENT.publish(points=points, identifier='2b53c571-3e7f-43fb-a8b3-f9b1973b8a14')