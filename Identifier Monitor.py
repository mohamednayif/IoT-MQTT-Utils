# pyinstaller --onefile --console --name="MQTT Identifier Monitor" "Identifier Monitor.py" --specpath=build
from MQTT import MQTT
import os
import sys
from time import sleep
import platform
import subprocess


def identifier_monitor(Mqtt: MQTT):
    Mqtt.subscribe_topic = input("Topic to Subscribe (Optional) : ")
    Mqtt.identifier_to_monitor = input("Identifier to Monitor (Required)   : ")
    if Mqtt.identifier_to_monitor is not "":
        try:
            print("\nPress Ctrl+C to stop\n")
            Mqtt.connect()
            Mqtt.client.loop_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Identifier Monitor ::: Error ::: {e}")
        finally:
            Mqtt.disconnect()
            print("Application will be closed in 5 seconds.")
            sleep(5)
            sys.exit()
    else:
        clear_terminal()
        print("No Identifier to Monitor. Please try again.\n")
        identifier_monitor(Mqtt)


def clear_terminal():
    if platform.system() == "Windows":
        subprocess.run(["C:\\Windows\\System32\\cmd.exe", "/c", "cls"], check=True)
    else:
        subprocess.run(["/usr/bin/clear"], check=True)


def main():
    Mqtt = MQTT(on_connect_funcs=["subscribe"], on_message_funcs=["identifier_monitor"])
    identifier_monitor(Mqtt)


if __name__ == "__main__":
    main()
