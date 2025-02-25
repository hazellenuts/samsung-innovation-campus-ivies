#IVIES-Samsung Innovation Campus
#visualizing ultrasonic sensor data

import network
import time
from umqtt.simple import MQTTClient
from hcsr04 import HCSR04

# MQTT Server Parameters
MQTT_CLIENT_ID = "gabrielleee"
MQTT_BROKER    = "broker.emqx.io"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "ivies/ultrasonic/sensor"

# Wifi connection
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("herucakra", "87654321")

while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.5)

print("\nConnected to WiFi!")

# MQTT Connection
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD, keepalive=60)
client.connect()
print("Connected to MQTT broker!")

# Inisialisasi sensor ultrasonik
sensor = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=10000)

while True:
    distance = sensor.distance_cm()
    print('Distance:', distance, 'cm')

    # Mengirim data ke MQTT
    client.publish(MQTT_TOPIC, str(distance))
    print("Data terkirim ke MQTT:", distance, "cm")

    time.sleep(1)

