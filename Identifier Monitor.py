# pyinstaller --onefile --console --name="MQTT Identifier Monitor" "Identifier Monitor.py"
from MQTT import MQTT 
import os
import sys
from time import sleep

def identifier_monitor(Mqtt: MQTT):
    Mqtt.subscribe_topic = input("Topic to Subscribe: ")
    Mqtt.identifier_to_monitor = input("Identifier to Monitor: ")
    print("\nPress Ctrl+C to stop\n")
    if Mqtt.identifier_to_monitor is not None:
        try:
            Mqtt.connect()
            Mqtt.client.loop_forever()
        except KeyboardInterrupt:
            Mqtt.disconnect()
            sys.exit()
        except Exception as e:
            Mqtt.disconnect()
            print(f"Identifier Monitor ::: Error ::: {e}")
            sleep(10)
            sys.exit()
    else:
        os.system('cls')      
        print("No Identifier to Monitor. Please try again.")  
        identifier_monitor(Mqtt)

def main():
    Mqtt = MQTT(on_connect_funcs=['subscribe'], on_message_funcs=['identifier_monitor'])     
    identifier_monitor(Mqtt) 
    
    
if __name__ == "__main__":
    main()