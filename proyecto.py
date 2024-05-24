from pyfirmata import Arduino, util
import time

# Configuración de los pines
led_pins = [3, 4, 5]  # Pines para los LEDs verde, amarillo y rojo
servo_pin = 10  # Pin para el servo motor
button_pin = 8  # Pin para el botón

# Configuración de la conexión con Arduino
board = Arduino('COM3')  # Reemplaza 'COM3' con el puerto correspondiente a tu Arduino
it = util.Iterator(board)
it.start()

# Configuración de los componentes
leds = [board.get_pin(f'd:{pin}:o') for pin in led_pins]
servo = board.get_pin(f'd:{servo_pin}:s')
button = board.get_pin(f'd:{button_pin}:i')
button.enable_reporting()

duracion_encendido = 5

# Función para encender un LED y controlar el servo
def encender_led(pin, duracion):
    leds[pin - 3].write(1)
    if pin == 4:  # Verifica si el LED del pin 4 se enciende
        servo.write(90)  # Gira el servo a 90 grados
        print("Servo motor encendido.")
    time.sleep(duracion)
    leds[pin - 3].write(0)
    if pin == 4:  # Verifica si el LED del pin 4 se apaga
        servo.write(0)  # Gira el servo a 0 grados
    print(f"LED en pin {pin} apagado.")

# Apagar todos los LEDs al inicio
for led in leds:
    led.write(0)

try:
    # Esperar hasta que el botón sea presionado
    print("Esperando a que el botón sea presionado...")
    while True:
        button_state = button.read()
        if button_state == 1:
            print("Botón presionado, iniciando ciclo.")
            break
        time.sleep(0.1)  # Pequeña espera para evitar la saturación de la CPU

    # Cola de tareas (orden FCFS)
    tasks = [
        (3, duracion_encendido),
        (4, duracion_encendido),
        (5, duracion_encendido)
    ]

    # Ejecutar tareas en orden FCFS
    for pin, duracion in tasks:
        encender_led(pin, duracion)

    print("Ciclo de tareas completado.")

except KeyboardInterrupt:
    pass
finally:
    board.exit()
    print("Programa terminado.")
