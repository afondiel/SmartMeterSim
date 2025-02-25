import asyncio
import json
import argparse
import time
import os
from collections import deque
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# Keep last 100 messages
MAX_ENTRIES = 100
# Use a deque for efficient appending and trimming
message_queue = deque(maxlen=MAX_ENTRIES)

# CLI Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="AWS IoT endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", required=True, dest="certPath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", required=True, dest="keyPath", help="Private key file path")
parser.add_argument("-l", "--logFile", action="store", required=True, dest="logPath", help="Received MQTT data path")
parser.add_argument("-t", "--topic", action="store", required=True, dest="topic", help="MQTT topic")
parser.add_argument("-i", "--clientId", action="store", dest="clientId", default="SmartMeter01", help="MQTT Client ID")
args = parser.parse_args()

def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

def save_message_to_file(log_filepath, message):
    try:
        with open(log_filepath, "r+") as file:
            # Read existing content
            file.seek(0)
            content = file.read()
            data = json.loads(content) if content else []
            
            # Append new message
            data.append(message)
            
            # Keep only the last MAX_ENTRIES
            data = data[-MAX_ENTRIES:]
            
            # Write updated content
            file.seek(0)
            file.truncate()
            json.dump(data, file, indent=2)
        
        print(f"Appended new message to log file. Total entries: {len(data)}")
    except IOError as e:
        print(f"Error writing to log file: {e}")
    except Exception as e:
        print(f"Unexpected error saving message: {e}")

def create_message_handler(log_filepath):
    def on_message_received(topic, payload, dup, qos, retain, **kwargs):
        print(f"Received message from topic '{topic}': {payload}")
        try:
            message_json = json.loads(payload)
            print(f"📥 Received: {json.dumps(message_json, indent=2)}")
            message_queue.append(message_json)
            # Write only the new message to file in real-time
            save_message_to_file(log_filepath, message_json)
        except json.JSONDecodeError:
            print(f"Received message is not valid JSON: {payload}")
    return on_message_received

def main():
    # Initialize the log file with an empty list
    with open(args.logPath, 'w') as file:
        json.dump([], file)
    print(f"Initialized log file: {args.logPath}")    

    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args.host,
        cert_filepath=args.certPath,
        pri_key_filepath=args.keyPath,
        client_bootstrap=client_bootstrap,
        ca_filepath=args.rootCAPath,
        client_id=f"subscriber_{args.clientId}_{int(time.time())}",
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
    )

    print(f"Connecting to AWS IoT @ {args.host}")
    connect_future = mqtt_connection.connect()
    connect_future.result()  # Wait for connection
    print("Connected!")

    # Subscribe
    print(f"Subscribing to topic '{args.topic}'...")
    message_handler = create_message_handler(args.logPath)
    subscribe_future, _ = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=message_handler
    )
    
    subscribe_future.result()  # Wait for subscription to complete
    print(f"Subscribed to topic '{args.topic}'")

    # Wait for messages
    print("Waiting for messages. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()  # Wait for disconnection to complete
        print("Final save completed. Exiting.")

if __name__ == "__main__":
    main()
