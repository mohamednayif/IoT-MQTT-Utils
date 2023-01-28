# pyinstaller --onefile --console --name="MQTT Message Size Optimizer" "Message Size Optimizer.py"
from MQTT import MQTT 
import pandas as pd
import sys
from time import sleep
from constants import *

def main():
    Mqtt = MQTT(on_connect_funcs=['subscribe'], on_message_funcs=['message_size_monitor'])      
    Mqtt.subscribe_topic = input("Topic to Subscribe: ")
    try:
        standard_point = pd.read_csv(f"{ASSETS_PATH}{STANDARD_POINT_FILE}")
        Mqtt.point_shorten = standard_point.set_index(POINT_NAME_COLUMN).to_dict(orient='dict')[POINT_SHORTEN_COLUMN]
    except Exception as e:
        print(f"Message Size Optimizer ::: Error ::: {e}")  
        sleep(5)
        sys.exit()      
    Mqtt.module_shorten = MODULE_SHORTEN
    print("\nPress Ctrl+C to stop\n")
    try:
        Mqtt.connect()
        Mqtt.client.loop_forever()
    except KeyboardInterrupt:
        print("Stopping")
        Mqtt.client.disconnect()
        Mqtt.client.loop_stop()
    
if __name__ == "__main__":
    main()