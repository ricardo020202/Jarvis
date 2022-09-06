#Projecto asistente virtual "Jarvis" GUI
#este projecto consiste en crear un asistente virtual
#con funciones parecidas a siri o alexa

#librerias y archivos usadas para el projecto
import speech_recognition as sr
import subprocess as sub
import pyttsx3
import pywhatkit
import wikipedia
import datetime
import keyboard
import os
from tkinter import *
from PIL import Image
from pygame import mixer
import threading as tr
import whatsapp as wh
import browser as br
import datos
from chatterbot import ChatBot, preprocessors
from chatterbot.trainers import ListTrainer


#configurando ventana GUI
main_window = Tk()
main_window.title("Jarvis")
main_window.geometry("975x540")
main_window.resizable(0,0)
main_window.configure(bg = "#040204")

#string de comandos disponibles
comandos = """
    Comandos disponibles:

    -Reproduce + cancion
    -Busca + tema a buscar
    -Entra + pagina o app
    -Alarma + hora
    -Abre + archivo
    -Anota + nota
    -Mensaje + mensaje
    -Investiga + busqueda
"""

#desplegar comandos
canvas_comandos = Canvas(bg = "#040204", height = 270, width = 200, highlightthickness=0)
canvas_comandos.place(x = 5, y = 0)
canvas_comandos.create_text(95, 120, text = comandos, fill = "white", font = 'Arial 10 bold')

text_info = Text(main_window, bg = "#040204", fg = "white", relief="flat")
text_info.place(x = 10, y = 270, height = 270, width = "200")

#abriendo imagen de la GUI
file = "jarvis-iron-man.gif"
info = Image.open(file)
frames = info.n_frames

#lista de frames del gif
im = [PhotoImage(file=file,format = f"gif -index {i}") for i in range(frames)]
count = 0
anim = None

#ejecutar animacion
def animation(count):
    global anim
    im2 = im[count]
    gif_label.configure(image=im2)
    count += 1
    if count == frames:
        count = 0
    anim = main_window.after(95,lambda :animation(count))

gif_label = Label(main_window,image="", bg = "#040204")
gif_label.pack(pady = 110)
main_window.after(0, animation, 0)
main_window.mainloop

#inicializando libreria pyttsx3 para convertir de texto a voz
name = "yarbiss"
listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[4].id)
engine.setProperty('rate', 145)

#Cargar los datos guardados, de las apps, páginas o archivos, en los documentos de texto
def charge_data(name_dict, name_file):
    try:
        with open(name_file) as f:
            for line in f:
                (key, val) = line.split(",")
                val = val.rstrip("\n")
                name_dict[key] = val
    except FileNotFoundError:
        pass

#diccionario de sitios a los que se puede acceder
sites = dict()
charge_data(sites, "pages.txt")

#diccionario de archivos disponlibles para abrir
files = dict()
charge_data(files, "archivos.txt")

#diccionario de programas que se pueden ejecutar
programs = dict()
charge_data(programs, "apps.txt")

#diccionario de contactos
contacts = dict()
charge_data(contacts, "contacts.txt")


#funcion para convertir de texto a voz
def talk(text):
    engine.say(text)
    engine.runAndWait()

def read_and_talk():
    text = text_info.get("1.0", "end")
    talk(text)

def write_text(text_wiki):
    text_info.insert(INSERT, text_wiki)

#funcion para recibir informacion del microfono
def listen(phrase = None):
    listener =sr.Recognizer()
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        talk(phrase)
        pc = listener.listen(source)
    try:
        rec = listener.recognize_google(pc, language="es")
        rec = rec.lower()
    except sr.UnknownValueError:
        print("lo siento no te entendi, repitelo nuevamente")
    except sr.RequestError as e:
        print("could not request results from Google Speech Recognition service; {0}".format(e))
    return rec

#funcion para poner una alarma a la hora especificada
def clock(rec):
    num = rec.replace('pon una alarma a las', '')
    num = num.strip()
    talk("Alarma activada a las " + num + " horas")
    if num[0]  != '0' and len(num) < 5:
        num = '0' + num
    while True:
        if datetime.datetime.now().strftime('%H:%M') == num:
            print("DESPIERTA!!!")
            mixer.init()
            mixer.music.load("alarma.mp3")
            mixer.music.play()
        else:
            continue
        if keyboard.read_key == "s":
                mixer.music.stop()
                break

#funcion para reproducir musica
def reproduce(rec):
    music = rec.replace('reproduce', '')
    print("Reproduciendo " + music)
    talk("Reproduciendo " + music)
    pywhatkit.playonyt(music)

#funcion para buscar en google
def busca(rec):
    search = rec.replace('busca', '')
    wikipedia.set_lang("es")
    wiki = wikipedia.summary(search, 1)
    talk(wiki)
    write_text(search + ": " + wiki)

#funcion para para poner alarma
def thread_alarma(rec):
    t = tr.Thread(target = clock, args = (rec,))
    t.start()

#funcion para entrar a apps o paginas
def entra_a(rec):
    task = rec.replace('entra a', '').strip()
    if task in sites:
        for task in sites:
            if task in rec:
                sub.call(f'start chrome.exe {sites[task]}', shell=True)
                talk(f'Entrando a {task}')
    elif task in  programs:
        for task in programs:
            if task in rec:
                talk(f'Entrando a {task}')
                sub.Popen(programs[task])
    else:
                talk("No se encontró la app o la página que deseas abrir, usa los botones de agregar página o app")

#funcion para abrir archivos
def abre_el_archivo(rec):
    file = rec.replace('abre el archivo', '').strip()
    if file in files:
        for file in files:
            if file in rec:
                sub.Popen([files[file]], shell=True)
                talk(f'Abriendo {file}')
    else:
        talk("No se encontró el archivo que deseas abrir, usa el boton de agregar archivo")

#funcion para anotar cosas
def anota(rec):
    try:
        with open("nota.txt", 'a') as f:
            write(f)
    except FileNotFoundError as e:
        file = open("nota.txt", 'w')
        write(file)

#funcion para anotar cosas en bloc de notas
def write(f):
    talk("¿Qué quiere que escriba?")
    rec_write = listen("Te escucho")
    f.write(rec_write + os.linesep)
    f.close()
    print("Anotado")
    talk("Anotado")
    sub.Popen("nota.txt", shell=True)

#funcion para enviar mensajes por whatsapp
def enviar_mensaje(rec):
    talk("¿A quien le quieres mandar el mensaje?")
    contact = listen("Te escucho")
    contact = contact.strip()

    if contact in contacts:
        for cont in contacts:
            if cont == contact:
                contact = contacts[cont]
                talk("¿qué mensaje quieres que le mande?")
                message = listen("Te escucho")
                talk("Enviando mensaje...")
                wh.send_message(contact, message)
                talk("Mensaje enviado")
    else:
        talk("No se encontro el contacto deseado, agregalo con el boton de agregar contactos")

#funcion para buscar en google
def investiga(rec):
    something = rec.replace('investiga', '')
    talk(f"Buscando {something}")
    br.search(something) 

#diccionario palabras clave 
key_words = {
    'reproduce': reproduce,
    'busca': busca,
    'alarma': thread_alarma,
    'entra': entra_a,
    'abre': abre_el_archivo,
    'anota': anota,
    'mensaje': enviar_mensaje,
    'investiga': investiga
}

#funcion principal
def run_jarvis():
    chat = ChatBot("yarbiss", datos_uri = None)
    trainer = ListTrainer(chat)
    trainer.train(datos.get_q_and_a())
    talk("Te escucho")
    while True:
        try:
            rec = listen("")
        except UnboundLocalError:
            talk("lo siento no te entendi, repitelo nuevamente")
            continue
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        elif rec.split()[0] in key_words:
            key_words[rec.split()[0]](rec)
        else:
            print(f"Tú: {rec}")
            answer = chat.get_response(rec)
            print(f"Jarvis: {rec}")
            talk(answer)
            if 'nos vemos' in rec:
                break
    main_window.update()

#abrir ventana secundaria para poder cargar archivos
def open_w_files():
    global name_file_entry, path_file_entry
    window_files = Toplevel()
    window_files.title("Agregar archivos")
    window_files.configure(bg = "#040204")
    window_files.geometry("487x270")
    window_files.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_files)} center')

    title_label = Label(window_files, text = "Agrega un archivo", fg = "white", bg = "black", font = ('Arial', 15, 'bold'))
    title_label.pack(pady = 20)

    name_label = Label(window_files, text = "Nombre del archivo", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    name_label.pack(pady = 3)

    name_file_entry = Entry(window_files, width = 35)
    name_file_entry.pack(pady = 2)

    path_label = Label(window_files, text = "Ruta del archivo", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    path_label.pack(pady = 3)

    path_file_entry = Entry(window_files, width = 35)
    path_file_entry.pack(pady = 2)

    save_button = Button(window_files, text = "Guardar", bg = 'white', fg = 'black', width = 8, height = 1, command = add_files)
    save_button.pack(pady = 10)

#abrir ventana secundaria para poder cargar apps
def open_w_apps():
    global name_app_entry, path_app_entry
    window_apps = Toplevel()
    window_apps.title("Agregar apps")
    window_apps.configure(bg = "#040204")
    window_apps.geometry("487x270")
    window_apps.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_apps)} center')

    title_label = Label(window_apps, text = "Agrega una app", fg = "white", bg = "black", font = ('Arial', 15, 'bold'))
    title_label.pack(pady = 20)

    name_label = Label(window_apps, text = "Nombre de la app", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    name_label.pack(pady = 3)

    name_app_entry = Entry(window_apps, width = 35)
    name_app_entry.pack(pady = 2)

    path_label = Label(window_apps, text = "Ruta de la app", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    path_label.pack(pady = 3)

    path_app_entry = Entry(window_apps, width = 35)
    path_app_entry.pack(pady = 2)

    save_button = Button(window_apps, text = "Guardar", bg = 'white', fg = 'black', width = 8, height = 1, command = add_apps)
    save_button.pack(pady = 10)

#abrir ventana secundaria para poder cargar paginas    
def open_w_pages():
    global name_pages_entry, path_pages_entry
    window_pages = Toplevel()
    window_pages.title("Agregar paginas")
    window_pages.configure(bg = "#040204")
    window_pages.geometry("487x270")
    window_pages.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_pages)} center')

    title_label = Label(window_pages, text = "Agrega una pagina", fg = "white", bg = "black", font = ('Arial', 15, 'bold'))
    title_label.pack(pady = 20)

    name_label = Label(window_pages, text = "Nombre de la pagina", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    name_label.pack(pady = 3)

    name_pages_entry = Entry(window_pages, width = 35)
    name_pages_entry.pack(pady = 2)

    path_label = Label(window_pages, text = "URL de la pagina", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    path_label.pack(pady = 3)

    path_pages_entry = Entry(window_pages, width = 35)
    path_pages_entry.pack(pady = 2)

    save_button = Button(window_pages, text = "Guardar", bg = 'white', fg = 'black', width = 8, height = 1, command = add_pages)
    save_button.pack(pady = 10)

#abrir ventana secundaria para poder cargar contactos   
def open_w_contact():
    global name_contact_entry, phone_entry
    window_contact = Toplevel()
    window_contact.title("Agregar contacto")
    window_contact.configure(bg = "#040204")
    window_contact.geometry("487x270")
    window_contact.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_contact)} center')

    title_label = Label(window_contact, text = "Agrega un contacto", fg = "white", bg = "black", font = ('Arial', 15, 'bold'))
    title_label.pack(pady = 20)

    name_label = Label(window_contact, text = "Nombre del contacto", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    name_label.pack(pady = 3)

    name_contact_entry = Entry(window_contact)
    name_contact_entry.pack(pady = 2)

    path_label = Label(window_contact, text = "Telefono", fg = "white", bg = "black", font = ('Arial', 10, 'bold'))
    path_label.pack(pady = 3)

    phone_entry = Entry(window_contact)
    phone_entry.pack(pady = 2)

    save_button = Button(window_contact, text = "Guardar", bg = 'white', fg = 'black', width = 8, height = 1, command = add_contact)
    save_button.pack(pady = 10)

#funcion para guadar los datos del archivo a cargar en un archivo de texto que funge como base de datos
def add_files():
    name_file = name_file_entry.get().strip()
    path_file = path_file_entry.get().strip()

    files[name_file] = path_file
    save_data(name_file, path_file, "archivos.txt")
    name_file_entry.delete(0, "end")
    path_file_entry.delete(0, "end")

#funcion para guadar los datos de la app a cargar en un archivo de texto que funge como base de datos
def add_apps():
    name_app = name_app_entry.get().strip()
    path_app = path_app_entry.get().strip()

    programs[name_app] = path_app
    save_data(name_app, path_app, "apps.txt")
    name_app_entry.delete(0, "end")
    path_app_entry.delete(0, "end")

#funcion para guadar los datos de la página a cargar en un archivo de texto que funge como base de datos
def add_pages():
    name_pages = name_pages_entry.get().strip()
    path_pages = path_pages_entry.get().strip()

    sites[name_pages] = path_pages
    name_pages_entry.delete(0, "end")
    save_data(name_pages, path_pages, "pages.txt")
    path_pages_entry.delete(0, "end")

#funcion para guadar los datos del archivo a cargar en un archivo de texto que funge como base de datos
def add_contact():
    name_contact = name_contact_entry.get().strip()
    phone = phone_entry.get().strip()

    contacts[name_contact] = phone
    save_data(name_contact, phone, "contacts.txt")
    name_contact_entry.delete(0, "end")
    phone_entry.delete(0, "end")

#funcion para el boton de guardar datos
def save_data(key, value, file_name):
    try:
        with open(file_name, 'a') as f:
            f.write(key + ',' + value + "\n")
    except FileNotFoundError:
        file = open(file_name, 'a')
        file.write(key + ',' + value + "\n")

#funcion para decir paginas guardadas
def tell_pages():
    if bool(sites) == True:
        talk("Tus paginas guardadas son")
        for site in sites:
            talk(site)
    else:
        talk("Aún no has agregado páginas web!")

#funcion para decir apps guardadas
def tell_apps():
    if bool(programs) == True:
        talk("Tus apps guardadas son")
        for app in programs:
            talk(app)
    else:
        talk("Aún no has agregado apps!")

#funcion para decir archivos guardadas
def tell_files():
    if bool(files) == True:
        talk("Tus archivos agregados son")
        for file in files:
            talk(file)
    else:
        talk("Aún no has agregado archivos!")

#funcion para decir contactos guardadas
def tell_contact():
    if bool(contacts) == True:
        talk("Tus contactos agregados son")
        for contact in contacts:
            talk(contact)
    else:
        talk("Aún no has agregado contactos!")

#funcion para gardar nombre
def tell_name():
    talk("Hola, ¿cómo te llamas?")
    rec = listen("Te escucho")
    name = rec.strip()
    talk(f"Bienvenido {name}")

    try:
        with open("name.txt", 'w') as f:
            f.write(name)
    except FileNotFoundError:
        file = open("name.txt", 'w')
        file.write(name)

#funcion de vienvenida
def welcome():
    if os.path.exists("name.txt"):
        with open("name.txt") as f:
            for name in f:
                talk(f"Bienvenido nuevamente {name}!")
    else:
        tell_name()

#activar funcion de bienvenida
def thread_welcome():
    t = tr.Thread(target = welcome)
    t.start()
    
thread_welcome()

#boton para activar a jarvis
button_listen =  Button(main_window, text = "Escuchar", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = run_jarvis)
button_listen.pack()

#botn para hablar lo que este escrito en un cuadro de texto
button_speak =  Button(main_window, text = "Hablar", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = read_and_talk)
button_speak.place(x = 750, y = 10)

#boton para abrir ventana secndaria para cargar archivos
button_add_files =  Button(main_window, text = "Agregar archivos", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = open_w_files)
button_add_files.place(x = 750, y = 70)

#boton para abrir ventana secndaria para cargar apps
button_add_apps =  Button(main_window, text = "Agregar apps", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = open_w_apps)
button_add_apps.place(x = 750, y = 130)

#boton para abrir ventana secndaria para agregar páginas 
button_add_contact =  Button(main_window, text = "Agregar Paginas", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = open_w_pages)
button_add_contact.place(x = 750, y = 190)

#boton para abrir ventana secndaria para agregar contactos
button_add_pages =  Button(main_window, text = "Agregar contactos", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = open_w_contact)
button_add_pages.place(x = 750, y = 250)

#boton para consultar páginas guardadas
button_tell_pages =  Button(main_window, text = "Paginas guardadas", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = tell_pages)
button_tell_pages.place(x = 750, y = 310)

#boton para consultar apps guardadas
button_tell_apps =  Button(main_window, text = "Apps guardadas", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = tell_apps)
button_tell_apps.place(x = 750, y = 370)

#boton para consultar archivos guardados
button_tell_files =  Button(main_window, text = "Archivos guardados", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = tell_files)
button_tell_files.place(x = 750, y = 430)

#boton para consultar contactos guardados
button_tell_contact =  Button(main_window, text = "contactos guardados", fg = "black", bg = "white",
                        font = ("Arial", 15, "bold"), command = tell_contact)
button_tell_contact.place(x = 750, y = 490)

#ventana principal
main_window.mainloop()