import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
from datetime import datetime
from database import Database
import os
from dotenv import load_dotenv

load_dotenv()

class MQTTDatabaseSubscriber:
    def __init__(self):
        self.db = Database()
        self.broker = os.getenv('MQTT_BROKER', 'localhost')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        
        # v2: Must specify callback API version
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id="solarflow_db_subscriber"
        )
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.messages_received = 0
        self.messages_stored = 0
    
    def on_connect(self, client, userdata, flags, reason_code, properties):
        """v2: Updated callback signature"""
        if reason_code == 0:
            print(f"✓ Connected to MQTT broker at {self.broker}:{self.port}")
            client.subscribe("solar/panel/+/data")
            print("✓ Subscribed to solar/panel/+/data")
            print("\nWaiting for messages...\n")
        else:
            print(f"✗ Connection failed: {reason_code}")
    
    def on_message(self, client, userdata, msg):
        """Process incoming MQTT messages"""
        self.messages_received += 1
        
        try:
            data = json.loads(msg.payload.decode())
            
            # Insert into database
            record_id = self.db.insert_solar_data(data)
            
            if record_id:
                self.messages_stored += 1
                print(f"✓ Stored Panel {data['panel_id']}: "
                      f"{data['power_w']}W "
                      f"(Total: {self.messages_stored})")
            else:
                print(f"✗ Failed to store data for Panel {data['panel_id']}")
                
        except Exception as e:
            print(f"✗ Error processing message: {e}")
    
    def run(self):
        """Start the subscriber"""
        print("="*60)
        print("SolarFlow MQTT to Database Subscriber")
        print("="*60)
        
        # Test database connection
        if not self.db.test_connection():
            print("\n✗ Cannot start - database connection failed")
            return
        
        print(f"\nConnecting to MQTT broker...")
        self.client.connect(self.broker, self.port, 60)
        
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print(f"\n\nShutting down...")
            print(f"  Messages received: {self.messages_received}")
            print(f"  Messages stored: {self.messages_stored}")
            self.client.disconnect()

if __name__ == "__main__":
    subscriber = MQTTDatabaseSubscriber()
    subscriber.run()