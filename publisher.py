import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
import time
from datetime import datetime
import random


#configuration
BROKER="localhost"
PORT=1883
TOPIC_PREFIX="solar/panel"

# callback functions 
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with reason code {reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"Message {mid} published")

# create MQTT client and set callbacks
client = mqtt.Client(client_id="publisher", callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_publish = on_publish

# connect to broker
print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    panel_id = 1
    while True:
        # simulate solar panel data
        data = {
            "panel_id": panel_id,
            "power": round(random.uniform(100, 400), 2),
            "voltage": round(random.uniform(30, 48), 2),
            "current": round(random.uniform(3, 10), 2),
            "temperature": round(random.uniform(20, 60), 2),
            "timestamp": datetime.now().isoformat()
        }
        
        topic = f"{TOPIC_PREFIX}/{panel_id}/data"
        payload = json.dumps(data)
        
        result = client.publish(topic, payload)
        print(f"Publishing to {topic}: {payload}")
        
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nDisconnecting from broker...")
    client.loop_stop()
    client.disconnect()
    print("Exiting...")