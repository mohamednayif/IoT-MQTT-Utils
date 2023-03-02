# pyinstaller -w --onefile --console --name="Ambient Sensor" "Ambient Sensor.py"  --specpath=build
import sys
import subprocess
from Credentials import Credentials
import paho.mqtt.client as mqtt
import ssl
import json
from time import sleep, time
import os
from constants import *
import logging

class MQTT(Credentials):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.client = mqtt.Client()
        if 'on_connect_funcs' in kwargs:
            # print("MQTT ::: On Connect ::: Enabled")
            self.on_connect_funcs = kwargs['on_connect_funcs']
            self.client.on_connect = self.on_connect
        if 'on_message_funcs' in kwargs:
            # print("MQTT ::: On Message ::: Enabled")
            self.on_message_funcs = kwargs['on_message_funcs']            
            self.client.on_message = self.on_message
        self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS, ciphers=None)
        self.client.tls_insecure_set(True)
        self.load_credentials()
        self.subscribe_topic = None
        self.identifier_to_monitor = None
        self.module_shorten = None
        self.point_shorten = None
        self.telemetry_topic = None
        self.telemetry_source_topic = None
        
    def load_credentials(self):
        if os.path.exists(f"{ASSETS_PATH}{CREDENTIALS_FILE}"):
            print("MQTT ::: Credentials ::: Loading credentials from file.")
            with open(f"{ASSETS_PATH}{CREDENTIALS_FILE}", "r") as secrets:
                credentials = json.load(secrets)
            try:
                username = self.decrypt(credentials[USERNAME])
                password = self.decrypt(credentials[PASSWORD])
                self.host = self.decrypt(credentials[HOST])
                self.port = int(self.decrypt(credentials[PORT]))
                self.topic = self.decrypt(credentials[TOPIC])
                self.client.username_pw_set(username=username, password=password)  
                del username, password
                return
            except Exception as e:
                print("MQTT ::: Credentials ::: Error ::: Invalid Credentials ::: Please install another credential and try again")
                sleep(2)
                sys.exit()
        else:                
            try:
                self.credentials_installer()
            except Exception as e:
                print(f"MQTT ::: Credentials ::: Error ::: {e}")

    def credentials_installer(self):
        try:
            if os.path.exists(CREDENTIALS_INSTALLER):     
                process = subprocess.Popen(f"start {CREDENTIALS_INSTALLER}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    print("MQTT ::: Credentials Installer ::: Success")
                    self.load_credentials()
            else:
                print("MQTT ::: Credentials Installer ::: Error ::: Installation file not found")  
                sleep(2)
                sys.exit()
        except Exception as e:
            print(f"MQTT ::: Credentials Installer ::: Error ::: {e}")
            sys.exit()

    def connect(self, final = False):
        try:            
            self.client.connect(self.host, self.port)
            return True
        except Exception as e:
            if final:
                print(f"MQTT ::: Connect ::: Error ::: Final ::: {e}")
                sleep(10)
                sys.exit()
            print(f"MQTT ::: Connect ::: Error ::: {e}")
            sleep(60)
            return self.connect(final=True)
    
    def on_connect(self, client, userdata, flags, rc):
        # print("MQTT ::: On Connect ::: Success")
        self.multi_call(functions = self.on_connect_funcs, client = client, userdata = userdata, flags = flags, rc = rc)

    def on_message(self, client, userdata, msg):
        # print("MQTT ::: On Message ::: Success")
        self.multi_call(functions = self.on_message_funcs, client = client, userdata = userdata, msg = msg)

    def multi_call(self, *args, **kwargs):
        for function in kwargs["functions"]:
            getattr(self, function)(*args, **kwargs)

    def publish(self, points, identifier, final = False):  
        payload = {
                        "reason": "CHANGE_OF_VALUE",  # REALTIME_UPDATE
                        "time": int(time()*1000),
                        "id": identifier,
                        "points": points
                    }
        try:        
            data = self.client.publish(topic=self.topic, 
                    payload = json.dumps(payload)
                )
            data = self.client.publish(topic=self.topic, 
                    payload = json.dumps(payload)
                )
            if data[0] != 0:
                raise Exception("Response code not 0")
            else:
                # print(f"MQTT ::: Publish ::: Success ::: {payload}")
                return True
        except Exception as e:
            if final:
                print(f"MQTT ::: Publish ::: Error ::: Final ::: {e}")
                return False
            print(f"MQTT ::: Publish ::: Error ::: {e}")
            if self.connect():
                return self.publish(points, identifier, final = True)
    
    def subscribe(self, *args, **kwargs):
        if self.subscribe_topic:
            self.client.subscribe(self.subscribe_topic)
        else:
            self.client.subscribe("#")

    def identifier_monitor(self, *args, **kwargs):
        if self.identifier_to_monitor in str(kwargs["msg"].payload):
            print({kwargs['msg'].payload})
    
    def message_size_monitor(self, *args, **kwargs):
        raw_message = str(kwargs['msg'].payload) 
        module_optimized = raw_message
        if self.module_shorten:
            for module_name, shorten_name in self.module_shorten.items():
                module_optimized = module_optimized.replace(module_name, shorten_name)

        point_optimized = raw_message
        optimum_message = module_optimized
        if self.point_shorten:
            for point_name, shorten_name in self.point_shorten.items():
                point_optimized = point_optimized.replace(point_name, shorten_name)
                optimum_message = optimum_message.replace(point_name, shorten_name)
            
        print(f"MQTT ::: Message Size Monitor ::: Original_size ::: {len(raw_message)} ::: Module_Optimized_size ::: {len(module_optimized)} ::: Point_Optimized_size ::: {len(point_optimized)} ::: Optimum_size ::: {len(optimum_message)} ::: Percentage Optimized ::: {round((1-len(optimum_message)/len(raw_message))*100, 2)}%")
    
    def disconnect(self):
        self.client.disconnect()

    def telemetry(self, *args, **kwargs):
        # print(str(kwargs['msg'].payload))
        from_topic = (str(kwargs['msg'].topic))
        # Find the start and end indices of the matching substring
        start_index = from_topic.find(self.telemetry_source_topic)
        end_index = start_index + len(self.telemetry_source_topic)
        if start_index >= 0:
            # Replace the matching substring with z
            new_x = from_topic[:start_index] + self.telemetry_topic + from_topic[end_index:]
            # print(new_x)  # Output: "dfhsjdkfhk"
        else:
            # Handle case where y is not found in x
            # logging.ERROR("Substring not found in string.")
            print("Substring not found in string.")
        
        to_topic = new_x
        logging.info(kwargs['msg'].payload)
        self.client.publish(topic=to_topic, payload=kwargs['msg'].payload)

