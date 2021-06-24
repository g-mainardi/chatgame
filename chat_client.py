#!/usr/bin/env python3
"""Script chat del client utilizzato per lanciare la GUI Tkinter."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt

''' Funzione per far partire il client con i dati in ingresso '''
def client_func(host, port):

    """ Funzione che ha il compito di gestire la ricezione dei messaggi."""
    def receive():
        while True:
            try:
                # Quando viene chiamata la funzione receive, si mette in ascolto dei messaggi che
                # arrivano sul socket
                msg = client_socket.recv(BUFSIZ).decode("utf8")
                # Il messaggio ricevuto lo divido in stringhe, dove occorre, tramite il 
                # separatore "\n". Ogni stringa la inserisco in fondo alla chat
                for s in msg.split("\n"):
                    if s : # Controllo che non sia una stringa vuota
                        msg_list.insert(tkt.END, s)
                        # Se il messaggio è "{quit}" allora esce
                        check_quit(s)

                # Nel caso di errore e' probabile che il client abbia abbandonato la chat.
            except OSError:  
                break

    """ Funzione che gestisce l'invio dei messaggi."""
    def send(event=None):
        # Gli eventi vengono passati dai binders.
        msg = my_msg.get()
        if msg :
            # Pulisco la casella di input.
            my_msg.set("")
            try:
                # Invia il messaggio sul socket
                client_socket.send(bytes(msg, "utf8"))
            finally:
                # Stampo il messaggio nella mia chat
                msg_list.insert(tkt.END, "Tu:" + msg)
                # Se il messaggio è "{quit}" allora esce
                check_quit(msg)
        
    ''' Funzione che controlla se l'input è una richiesta d'uscita'''
    def check_quit(msg):
        if msg == "{quit}":
            client_socket.close()
            window.quit()
            SystemExit

    """ Funzione invocata quando viene chiusa la finestra della chat."""
    def on_closing(event=None):
        my_msg.set("{quit}")
        send()

    #----Creazione GUI----

    # Creo la finestra e le do il titolo
    window = tkt.Tk()
    window.title("Chat_Laboratorio")

    # Frame per contenere i messaggi
    messages_frame = tkt.Frame(window)
    # Stringa per i messaggi da inviare.
    my_msg = tkt.StringVar()
    # Inizializzo stringa
    my_msg.set("Scrivi qui")
    # Scrollbar per navigare tra i messaggi precedenti.
    scrollbar = tkt.Scrollbar(messages_frame)

    # Creo la lista che rappresenta la chat
    msg_list = tkt.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
    msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    # Integro la chat nel pacchetto
    msg_list.pack()
    # Integro il frame nel pacchetto
    messages_frame.pack()

    # Campo di input e associato alla stringa
    entry_field = tkt.Entry(window, textvariable=my_msg)
    # Lego la funzione send al tasto Return (/Enter/Invio)
    entry_field.bind("<Return>", send)
    # Integro l'entry nel pacchetto
    entry_field.pack()

    # Creo tasto invio e associo alla funzione "send"
    send_button = tkt.Button(window, text="Invio", command=send)
    # Integro il tasto nel pacchetto
    send_button.pack()

    # Creo tasto Quit e associo alla funzione "on_closing"
    quit_button = tkt.Button(window, text="Quit", command=on_closing)
    # Integro il tasto nel pacchetto
    quit_button.pack()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    #----Connessione al Server----

    HOST = host # "127.0.0.1"
    PORT = port # 53000
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    # Creo socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    # Creo thread e lo avvio
    receive_thread = Thread(target=receive)
    receive_thread.start()
    
    # Avvia il loop principale della finestra
    tkt.mainloop()

if __name__ == "__main__":
    print("File non eseguibile")
