import asyncio
import csv
import json
import argparse
import time
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# CLI Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", action="store", required=True, dest="csv_path", help="CSV file path")
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="AWS IoT endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", required=True, dest="certPath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", required=True, dest="keyPath", help="Private key file path")
parser.add_argument("-t", "--topic", action="store", required=True, dest="topic", help="MQTT topic")
parser.add_argument("-d", "--delay", action="store", default=2, type=float, dest="delay", help="Delay in seconds")
parser.add_argument("-i", "--clientId", action="store", dest="clientId", default="SmartMeter01", help="MQTT Client ID")
parser.add_argument("-l", "--loop", action="store_true", dest="loop", help="Loop through the CSV file")
args = parser.parse_args()

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

async def publish_csv_data(mqtt_connection, csv_path, topic, delay, loop):
    with open(csv_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        iterate = True
        
        while iterate:
            for row in reader:
                payload = {
                    "timestamp": row["Date"],
                    "energy_kW": row["Value (kW)"]
                }
                message_json = json.dumps(payload)
                publish_future, _ = mqtt_connection.publish(
                    topic=topic,
                    payload=message_json,
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )
                publish_future.result()  # Wait for the result
                print(f"📤 Published: {message_json}")
                await asyncio.sleep(delay)

            if loop:
                csvfile.seek(0)
                next(reader)  # Skip header row
            else:
                iterate = False

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
        client_id=f"publisher_{args.clientId}_{int(time.time())}",
        # client_id=args.clientId,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
    )

    print(f"Connecting to AWS IoT @ {args.host}")
    connect_future = mqtt_connection.connect()
    connect_future.result()  # Wait for connection
    print("✅ Connected to AWS IoT, Publishing Data...")

    try:
        asyncio.get_event_loop().run_until_complete(
            publish_csv_data(mqtt_connection, args.csv_path, args.topic, args.delay, args.loop)
        )
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()  # Wait for disconnection

if __name__ == "__main__":
    main()
