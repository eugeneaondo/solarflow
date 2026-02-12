import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json


#configuration
BROKER="localhost"
PORT=1883
TOPIC="solar/panel/+/data"

# callback functions 
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with reason code {reason_code}")
    client.subscribe(TOPIC)
    print(f"Subscribed to topic: {TOPIC}")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}")

    try:
        payload = json.loads(msg.payload.decode())
        print(f"Panel ID: {payload['panel_id']}")
        print(f"Power : {payload['power']} W")
        print(f"Voltage: {payload['voltage']} V")
        print(f"Current: {payload['current']} A")
        print(f"Temperature: {payload['temperature']} °C")
        print(f"Timestamp: {payload['timestamp']}")
        print()
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Raw payload: {msg.payload}")

# create MQTT client and set callbacks
client = mqtt.Client(client_id="subscriber", callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message


# connect to broker and start loop
print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
client.connect(BROKER, PORT, 60)

try:    
    client.loop_forever()
except KeyboardInterrupt:
    print("Disconnecting from broker...")
    client.disconnect()
    print("Exiting...")