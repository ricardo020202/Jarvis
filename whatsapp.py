#archivo para funcion de mandar mensajes por whatsapp

#librerias del archivo
import webbrowser
import pyautogui as pa
import time

#funcion para mandar mensajes por whatsapp
def send_message(contact, message):
    webbrowser.open(f"https://web.whatsapp.com/send?phone={contact}&text={message}")
    time.sleep(4)
    pa.press('enter')