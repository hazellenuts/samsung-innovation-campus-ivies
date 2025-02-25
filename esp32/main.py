# IVIES-Samsung Innovation Campus
# Visualizing ultrasonic sensor data for flood detection

import network
import time
import urequests
from umqtt.simple import MQTTClient
from hcsr04 import HCSR04
import ujson

# MQTT Server Parameters
MQTT_CLIENT_ID = "gabrielleee"
MQTT_BROKER    = "broker.emqx.io"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "ivies/ultrasonic/sensor"

# Ubidots API Parameters (STEM Version)
UBIDOTS_TOKEN = "BBUS-7Te8n5DxSFvO1WsWOzSPAWAWCb9H8t"
UBIDOTS_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/ivies-esp32/"

# Wifi connection
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("herucakra", "87654321")  # Ganti jika pakai ESP32 asli

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

# Tinggi tangki (misalnya 12 cm)
TANK_HEIGHT = 12  # cm

def calculate_flood_height(distance):
    """
    Menghitung ketinggian banjir berdasarkan jarak sensor ke permukaan air.
    """
    # Ketinggian banjir = tinggi tangki - jarak sensor ke permukaan air
    flood_height = TANK_HEIGHT - distance
    # Pastikan ketinggian banjir tidak lebih kecil dari 0 cm
    flood_height = max(flood_height, 0)
    return flood_height

def calculate_flood_percentage(flood_height):
    """
    Menghitung ketinggian banjir dalam bentuk persentase.
    """
    # Ketinggian banjir dalam persen
    flood_percentage = (flood_height / TANK_HEIGHT) * 100
    # Pastikan persentase berada antara 0% dan 100%
    flood_percentage = max(0, min(100, flood_percentage))
    return flood_percentage

def send_to_ubidots(distance, flood_height, flood_percentage):
    payload = {
        "Distance": {"value": distance},  # Mengirimkan jarak sensor
        "Flood_Height": {"value": flood_height},  # Mengirimkan ketinggian banjir (cm)
        "Flood_Percentage": {"value": flood_percentage}  # Mengirimkan ketinggian banjir (persen)
    }
    headers = {
        'X-Auth-Token': UBIDOTS_TOKEN,
        'Content-Type': 'application/json'  # Tambahkan Content-Type
    }

    print(f"Sending to Ubidots: {payload}")  # Debug payload
    try:
        response = urequests.post(UBIDOTS_URL, json=payload, headers=headers)
        print(f"Data sent to Ubidots: {response.status_code}")
        print(f"Ubidots Response: {response.status_code}, {response.text}")  # Debug response
        response.close()
    except Exception as e:
        print(f"Failed to send data to Ubidots: {e}")

while True:
    try:
        print("Getting distance from sensor...")
        distance = sensor.distance_cm()
        print("Distance received:", distance, "cm")

        # Hitung ketinggian banjir
        flood_height = calculate_flood_height(distance)
        # Hitung ketinggian banjir dalam persen
        flood_percentage = calculate_flood_percentage(flood_height)

        print(f"Flood height: {flood_height} cm")
        print(f"Flood percentage: {flood_percentage}%")

        # Kirim data ke Ubidots
        print("Publishing to Ubidots...")
        send_to_ubidots(distance, flood_height, flood_percentage)
        print("Data terkirim ke Ubidots!")

        # Hapus sementara bagian MQTT jika diperlukan untuk pengujian Ubidots saja
        print("Publishing to MQTT...")
        client.publish(MQTT_TOPIC, str(distance))
        print("Data terkirim ke MQTT:", distance, "cm")

    except Exception as e:
        print(f"Error in loop: {e}")

    time.sleep(1)

