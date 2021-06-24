#!/usr/bin/env python3
"""Script Python : Server multithread per Chatgame - Nave pirata.
Corso di Programmazione di Reti - Università di Bologna"""

import sys
import random as rnd
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from time import sleep
from collections import defaultdict

def server_func(host, port):
    """ Funzione che accetta le connessioni dei client in entrata."""
    def accept_incoming_connections():
        while playing:
            client, client_address = SERVER.accept()
            print("%s:%s si è collegato." % client_address)
            if(not roles):
                # Comunico al client che non ci sono ruoli disponibili
                client.send(bytes(prefix + "Al momento non ci sono più ruoli disponibili, riprovo tra poco...", "utf8"))
                # Comunico al client che deve uscire
                client.send(bytes("\n{quit}", "utf8"))
                # Chiudo il client
                client.close()
                print("%s:%s è uscito." % client_address)
                sleep(5)
                continue
            client.send(bytes(prefix + "Benvenuto nella nave!", "utf8"))
            # Uso un dizionario per registrare i client
            addresses[client] = client_address
            # Avvio Thread - uno per ciascun client
            Thread(target=handle_client, args=(client,)).start()

    """ Funzione che gestisce la connessione di un singolo client."""
    def handle_client(client):  # Prende il socket del client come argomento della funzione.
        # Estraggo il ruolo casualmente e lo rimuovo dalla lista dei ruoli disponibili
        role = rnd.choice(roles)
        roles.remove(role)
        # Invio il ruolo al client 
        client.send(bytes(prefix + "Il tuo ruolo è : %s." % role, "utf8"))

        # Aggiorno il dizionario dei clients 
        clients[client] = role
        # Assegno al client il punteggio iniziale (0)
        scores[client] = 0

        # Notifico tutti i client connessi che un nuovo ruolo è stato assegnato
        broadcast("%s si è unito!" %  role)

        # Ciclo che chiede il quiz al client finchè non viene eliminato o scade il tempo
        while(playing and client in scores):  
            quiz(client)
        
        # Controllo se il tempo è scaduto, in tal caso, esco dalla funzione
        if not playing:
            return
        # Dato che il client è uscito dal ciclo e il tempo non è scaduto, allora 
        # vuol dire che è stato eliminato...

        # Attendo un po' prima di espellere 
        sleep(3)

        # Comunico al client che deve uscire
        client.send(bytes("\n{quit}", "utf8"))
        # Chiudo il socket del client
        client.close()

        print("%s:%s uscito." % (addresses[client]))

        # Rimuovo il client dai vari dizionari 
        del addresses[client]
        del clients[client]
        
        # Comunico a tutti che il client è stato eliminato
        broadcast("%s è uscito." % role)

        # Rendo disponibile il ruolo del client espulso
        roles.append(role)

    ''' Funzione che fa il quiz al client '''
    def quiz(client):
        menu = "Scegli una delle opzioni: 1 2 3"
        # Chiedo scelta menù
        client.send(bytes(prefix + menu, "utf8"))
        valid = False # Booleano che mi indica se l'input del client è valido
        while(not valid):
            # Aspetto di ricevere la scelta dal client
            choice = client.recv(BUFSIZ).decode("utf8")
            # Controllo se input valido
            if choice and (choice[0] == '1' or choice[0] == '2' or choice[0] == '3') :
                #rnd.shuffle(options) # Mischio la lista con le 3 opzioni
                option = get_options()[int(choice[0]) - 1] 
                valid = True
            elif choice == "{quit}": # Controllo se è stata chiesta la disconnessione
                option = "Uscita in corso..."
                valid = True
            else: # Se l'input non è valido, invio il menu con la richiesta
                option = "Input non valido. " + menu
            # Mando la scelta al client oppure richiedo con menù
            client.send(bytes(prefix + option, "utf8"))
        
        # Se è stata scelta una delle domande allora faccio il controllo della risposta
        if(option in answers):
            check_answer(client, option)
        else : # È stato beccato il trabocchetto --> Espulsione del client
            del scores[client]

    ''' Funzione che controlla se il client risponde correttamente alla domanda in input'''
    def check_answer(client, question):
        # Controllo se è effettivamente una delle domande 
        if (question in questions):
            # Chiedo il client la risposta alla domanda
            answer = client.recv(BUFSIZ).decode("utf8")
            if answer == answers[question] :
                result = "Indovinato! Hai guadagnato un punto!"
                point = 1
            elif answer == "{quit}":
                del scores[client]
            else :
                result = "Sbagliato! Hai perso un punto!"
                point = -1
            # Invio al client il risultato della sua risposta
            client.send(bytes(prefix + result, "utf8"))
            # Incremento o decremento il punteggio del client in base alla risposta data
            scores[client] += point

    """ Funzione con cui il Server invia un messaggio in broadcast a tutti i client."""
    def broadcast(msg): 
        for utente in clients:
            utente.send(bytes("\n" + msg, "utf8"))

    ''' Funzione per timer'''
    def countdown(timer):
        if(timer < 0):
            print("Valore timer negativo")
            exit()
        while timer > - 1 :
            print(timer)
            sleep(1)
            timer -= 1
        
    ''' Funzione per avere una lista dei massimi elementi di un dizionario'''
    def get_max_value(data):
        if not data : # Dizionario vuoto
            return []
        d = defaultdict(list) # Dizionario ausiliario che vado a riempire
        for key, value in data.items(): # Ciclo in cui costruisco un dizionario partendo dai valori
            d[value].append(key)
        return max(d.items())[1] # Prendo solo le chiavi con valori massimi
    
    ''' Funzione per avere una lista dei ruoli vincitori '''
    def get_winners():
        list = []
        for v in get_max_value(scores): # Prendo i client con punteggio più alto
            list.append(clients[v])     # e metto i relativi ruoli in una lista
        return list
    
    ''' Funzione per ottenere la lista delle 3 scelte del menù '''
    def get_options():
        # Estraggo due domande a caso
        o = [rnd.choice(questions), rnd.choice(questions), trick]
        rnd.shuffle(o) # Mischio la lista
        return o

    clients = {}    # Dizionario in cui salvo il ruolo di ciascun Client
    addresses = {}  # Dizionario in cui salvo l'indirizzo di ciascun Client
    scores = {}     # Dizionario in cui salvo il punteggio di ciascun Client

    HOST = host   # Da input
    PORT = port   # Da inpur
    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    # Creo socket server per connessione TCP
    SERVER = socket(AF_INET, SOCK_STREAM)
    # Lego il socket con l'indirizzo dato in input
    SERVER.bind(ADDR)

    # Prefisso dei messaggi del Server sulle chat dei client
    prefix = "\nMaster(Server):"

    # Lista contenente i vari ruoli disponibili
    roles = ["Il Capitano", "Lo Spadaccino", "Il Navigatore", "Il Cecchino", "Il Cuoco", "Il Dottore", "L'Archeologo",
                     "Il Carpentiere", "Il Musicista", "Il Timoniere"]

    # Prefisso per le domande dei quiz
    pre_domanda = "Domanda(Rispondi con la lettera selezionata) - "

    q1 = pre_domanda + "Come si chiama questo corso?\n---------a)Programmazione di Reti\n---------b)Basi di Dati\n---------c)Sistemi Operativi"
    q2 = pre_domanda + "Quanti CFU ha questo corso?\n---------a)3CFU\n---------b)6CFU\n---------c)9CFU"
    q3 = pre_domanda + "Il linguaggio scelto per il laboratorio è:\n---------a)C#\n---------b)Python\n---------c)Java"
    q4 = pre_domanda + "Quali sono i professori di questo corso?\n---------a)Mirko Viroli-Pianini Danilo\n---------b)Maio Dario-Franco Annalisa\n---------c)Pau Giovanni- Piroddi Andrea"
    q5 = pre_domanda + "Le lezioni del corso sono state svolte sulla piattaforma:\n---------a)Teams\n---------b)Zoom\n---------c)Meet"

    # Lista che contiene le domande
    questions = [q1, q2, q3, q4, q5]
    # Dizionario in cui ogni domanda ha la sua risposta corretta
    answers = {q1 : "a", q2 : "b", q3 : "b", q4 : "c", q5 : "a"}

    # Opzione Trabocchetto
    trick = "Trabocchetto - Sei eliminato!"

    # Tempo del gioco
    timer = 30

    # Booleano che indica se il gioco è in corso oppure no (Tempo scaduto)
    playing = True

    SERVER.listen(5)
    print("In attesa di connessioni...")

    # Creo Thread in cui il Server accetta i client che si collegano
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()

    TIMER_THREAD = Thread(target=countdown(timer))
    TIMER_THREAD.start()
    TIMER_THREAD.join()  # Attendo il termine del thread del timer

    playing = False # Tempo Scaduto
    print("Timer finito")
    broadcast(prefix + "Tempo Scaduto!")

    SERVER.close() # Chiudo il server

    #-----Calcolo dei vincitori
    winners = get_winners()
    # In base al numero dei vincitori mando il messaggio idoneo
    if(not winners):
        final_msg = "Non ci sono vincitori"
    elif(len(winners) == 1):
        final_msg = ("Il vincitore è " + winners[0])
    else :
        final_msg = "I vincitori sono " + ', '.join(winners)

    # Comunico i vincitori
    print(final_msg)
    broadcast(prefix + final_msg)

# Stampo messaggio di avviso nel caso qualcuno tentasse di eseguire questa classe 
# come uno script normale
if __name__ == "__main__":
    print("File non eseguibile")
