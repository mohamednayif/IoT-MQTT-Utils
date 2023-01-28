# pyinstaller --onefile --console --name="MQTT Credentials Installer" "Credentials Installer.py"
import json
import getpass
from Credentials import Credentials
import sys
from time import sleep
from constants import *

class Credentials_Installer(Credentials):
    def __init__(self):
        super().__init__()
    
    def install(self):
        try:            
            username = getpass.getpass("MQTT Broker Username: ")
            password = getpass.getpass("MQTT Broker Password: ")
            self.host = getpass.getpass("MQTT Broker Host: ")
            self.port = getpass.getpass("MQTT Broker Port: ")
            self.topic = input("MQTT Broker Topic: ")       
            with open(f"{ASSETS_PATH}{CREDENTIALS_FILE}", "w") as f:
                credentials = {
                    USERNAME: self.encrypt(username),
                    PASSWORD: self.encrypt(password),
                    HOST: self.encrypt(self.host),
                    PORT: self.encrypt(str(self.port)),
                    TOPIC: self.encrypt(self.topic)
                }
                json.dump(credentials, f)
            print("Credentials installed successfully")
            sleep(2)
        except Exception as e:
            print(f"Failed to install credentials: {e}")
            sleep(5)
            
def main():
    credentials = Credentials_Installer()
    credentials.install()        
    sys.exit()

if __name__ == "__main__":
    main()