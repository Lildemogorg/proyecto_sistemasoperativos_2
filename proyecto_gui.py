from pyfirmata import Arduino, util
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading

# Configuración de los pines
led_pins = [3, 4, 5]  # Pines para los LEDs verde, amarillo y rojo
servo_pin = 10  # Pin para el servo motor
button_pin = 8  # Pin para el botón de inicio
stop_button_pin = 9  # Pin para el botón de parada

# Configuración de la conexión con Arduino
board = Arduino('COM3')  # Reemplaza 'COM3' con el puerto correspondiente a tu Arduino
it = util.Iterator(board)
it.start()

# Configuración de los componentes
leds = [board.get_pin(f'd:{pin}:o') for pin in led_pins]
servo = board.get_pin(f'd:{servo_pin}:s')
button = board.get_pin(f'd:{button_pin}:i')
stop_button = board.get_pin(f'd:{stop_button_pin}:i')
button.enable_reporting()
stop_button.enable_reporting()

duracion_encendido = 5
stop_flag = False

# Función para encender un LED y controlar el servo
def encender_led(pin, duracion):
    global stop_flag
    leds[pin - 3].write(1)
    if pin == 4:  # Verifica si el LED del pin 4 se enciende
        servo.write(90)  # Gira el servo a 90 grados
        print_to_gui("Servo motor encendido.")
    start_time = time.time()
    while time.time() - start_time < duracion:
        if stop_flag:
            break
        time.sleep(0.1)
    leds[pin - 3].write(0)
    if pin == 4:  # Verifica si el LED del pin 4 se apaga
        servo.write(0)  # Gira el servo a 0 grados
    print_to_gui(f"LED en pin {pin} apagado.")

# Apagar todos los LEDs al inicio
for led in leds:
    led.write(0)

# Función para redirigir la salida de print a la interfaz gráfica
def print_to_gui(text):
    text_box.configure(state='normal')
    text_box.insert(tk.END, text + '\n')
    text_box.configure(state='disabled')
    text_box.see(tk.END)

# Función que ejecuta el código de Arduino en un hilo separado
def run_arduino_code():
    global stop_flag
    try:
        # Esperar hasta que el botón sea presionado
        print_to_gui("Esperando a que el botón sea presionado...")
        while True:
            button_state = button.read()
            stop_button_state = stop_button.read()
            if button_state == 1:
                print_to_gui("Botón presionado, iniciando ciclo.")
                break
            if stop_button_state == 1:
                print_to_gui("Botón de parada presionado, deteniendo.")
                stop_flag = True
                break
            time.sleep(0.1)  # Pequeña espera para evitar la saturación de la CPU

        if not stop_flag:
            # Cola de tareas (orden FCFS)
            tasks = [
                (3, duracion_encendido),
                (4, duracion_encendido),
                (5, duracion_encendido)
            ]

            # Ejecutar tareas en orden FCFS
            for pin, duracion in tasks:
                encender_led(pin, duracion)
                if stop_flag:
                    print_to_gui("Ciclo de tareas detenido.")
                    break

            if not stop_flag:
                print_to_gui("Ciclo de tareas completado.")

    except KeyboardInterrupt:
        pass
    finally:
        board.exit()
        print_to_gui("Programa terminado.")

# Función para monitorizar el botón de parada en un hilo separado
def monitor_stop_button():
    global stop_flag
    while not stop_flag:
        stop_button_state = stop_button.read()
        if stop_button_state == 1:
            print_to_gui("Botón de parada presionado, deteniendo.")
            stop_flag = True
        time.sleep(0.1)

# Configuración de la interfaz gráfica con tkinter
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal por ahora

# Crear una ventana secundaria para nuestra interfaz gráfica
window = tk.Toplevel(root)
window.title("Grupo #5 Proyecto final")
window.geometry("400x300")

# Crear un widget de texto con desplazamiento
text_box = ScrolledText(window, width=50, height=20, state='disabled', bg='turquoise')
text_box.pack(padx=10, pady=10)

# Iniciar el hilo para ejecutar el código de Arduino
arduino_thread = threading.Thread(target=run_arduino_code)
arduino_thread.start()

# Iniciar el hilo para monitorizar el botón de parada
stop_button_thread = threading.Thread(target=monitor_stop_button)
stop_button_thread.start()

# Ejecutar el bucle principal de tkinter
root.mainloop()
