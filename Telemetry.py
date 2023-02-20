# pyinstaller -w --onefile --console --name="Telemetry" "Telemetry.py"  --specpath=build
# pyinstaller -w --onefile --name="Telemetry" Telemetry.py --specpath=build
from MQTT import MQTT 
import pandas as pd
import asyncio
from time import sleep


async def main():
    Mqtt = MQTT(on_connect_funcs=['subscribe'], on_message_funcs=['telemetry'])      
    # Mqtt.telemetry_source_topic = input("Topic to Subscribe: ")
    # Mqtt.telemetry_topic = input("Topic to Publish: ")

    Mqtt.telemetry_source_topic = "Netix/Tridium"
    Mqtt.telemetry_topic = "netix/Tridium"
    Mqtt.subscribe_topic =  Mqtt.telemetry_source_topic+"/#"

    while True:
        try:
            Mqtt.connect()
            Mqtt.client.loop_forever()
        except KeyboardInterrupt:
            # print("Stopping")
            Mqtt.client.disconnect()
            Mqtt.client.loop_stop()
            sleep(5)
        except Exception as e:
            print(e)
            sleep(5)

if __name__ == "__main__":
    asyncio.run(main())