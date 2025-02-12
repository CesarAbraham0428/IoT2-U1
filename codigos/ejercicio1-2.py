# Import para acceso a red
import network
# Para usar protocolo MQTT
from umqtt.simple import MQTTClient

# Importamos módulos necesarios
from machine import Pin
from time import sleep
from hcsr04 import HCSR04

# Propiedades para conectar a un cliente MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "utng/sensors"

MQTT_PORT = 1883

# Creo el objeto que me controlará el sensor con los pines actualizados
sensor = HCSR04(trigger_pin=13, echo_pin=12, echo_timeout_us=24000)

# Declaro el pin LED
led = Pin(2, Pin.OUT)
led.value(0)

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('INFINITUM5B5A', '4DbxQ7eGDG')
    while not sta_if.isconnected():
        print(".", end="")
        sleep(0.3)
    print("WiFi Conectada!")

# Función para suscribirse al broker y topic
def subscribir():
    client = MQTTClient(MQTT_CLIENT_ID,
                        MQTT_BROKER, port=MQTT_PORT,
                        user=MQTT_USER,
                        password=MQTT_PASSWORD,
                        keepalive=0)
    client.set_callback(llegada_mensaje)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Conectado a %s, en el tópico %s" % (MQTT_BROKER, MQTT_TOPIC))
    return client

# Función encargada de encender un LED cuando un mensaje lo indique
def llegada_mensaje(topic, msg):
    print("Mensaje:", msg)
    if msg == b'true':
        led.value(1)
    if msg == b'false':
        led.value(0)

# Conectar a WiFi
conectar_wifi()
# Suscripción a un broker MQTT
client = subscribir()

distancia_anterior = 0
# Ciclo infinito
while True:
    client.check_msg()
    distancia = int(sensor.distance_cm())
    if distancia != distancia_anterior:
        print(f"La distancia es {distancia} cms.")
        client.publish(MQTT_TOPIC, str(distancia))
    distancia_anterior = distancia
    sleep(2)
