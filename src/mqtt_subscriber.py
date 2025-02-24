import asyncio
import json
import argparse
import time
import os
from threading import Lock
from collections import deque
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# Keep last 100 messages
MAX_ENTRIES = 100  

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


# Use a deque for efficient appending and trimming
message_queue = deque(maxlen=MAX_ENTRIES)
file_lock = Lock()

def save_message(log_filepath, new_data):
    try:
        # Append new message to the queue
        message_queue.append(new_data)

        # Use a lock to ensure thread-safety when writing to the file
        with file_lock:
            # Load existing data if file exists, otherwise use the current queue
            if os.path.exists(log_filepath):
                with open(log_filepath, "r") as file:
                    data = json.load(file)
                    # Update data with new messages from the queue
                    data.extend(list(message_queue))
                    # Trim to keep only the last MAX_ENTRIES
                    data = data[-MAX_ENTRIES:]
            else:
                data = list(message_queue)

            # Save updated log
            with open(log_filepath, "w") as file:
                json.dump(data, file, indent=4)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from log file: {e}")
    except IOError as e:
        print(f"Error reading or writing to log file: {e}")
    except Exception as e:
        print(f"Unexpected error saving message: {e}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

# Callback when the subscribed topic receives a message
def create_message_handler(log_filepath):
    def on_message_received(topic, payload, dup, qos, retain, **kwargs):
        print(f"Received message from topic '{topic}': {payload}")
        try:
            message_json = json.loads(payload)
            print(f"📥 Received: {json.dumps(message_json, indent=2)}")
            save_message(log_filepath, message_json)
        except json.JSONDecodeError:
            print(f"Received message is not valid JSON: {payload}")
    return on_message_received

def main():
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
        # client_id=args.clientId,
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
        # This will keep the main thread alive, which will keep the event loop running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()  # Wait for disconnection to complete

if __name__ == "__main__":
    main()
