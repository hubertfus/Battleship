"""
network.py

Moduł odpowiadający za komunikację sieciową między hostem a klientem w grze „Statki”.

Zawiera funkcje:
- init_network(): menu wyboru host/klient i nawiązywanie połączenia TCP,
- send_json(): wysyła słownik Python jako JSON zakończony '\n',
- try_receive_from_buffer(): odczytuje z nieblokującego socketu pełne linie JSON rozdzielone '\n'.
"""

import socket
import sys
import json

PORT = 5000  # Domyślny port do komunikacji gry


def send_json(sock, obj):
    """
    Wysyła obiekt Python (słownik) jako JSON-owy wiadomość zakończoną '\n'.

    Parametry:
    ----------
    sock : socket.socket
        Aktywny, nieblokujący socket TCP.
    obj : dict
        Słownik do wysłania. Funkcja serializuje go do JSON i dołącza '\n'.

    Mechanizm:
    ----------
    1. json.dumps(obj) → ciąg tekstowy,
    2. dodanie '\n', aby druga strona mogła podzielić bufor na pełne wiadomości,
    3. sock.sendall(…).
    """
    data = json.dumps(obj) + "\n"
    sock.sendall(data.encode())


def try_receive_from_buffer(sock, buffer):
    """
    Nieblokujący odczyt pełnych wiadomości JSON-owych zakończonych '\n' z socketu.

    Parametry:
    ----------
    sock : socket.socket
        Nieblokujący socket TCP, skonfigurowany sock.setblocking(False).
    buffer : str
        Bufor, który przechowuje nieprzetworzone fragmenty danych (może zawierać części JSON).

    Zwraca:
    --------
    messages : list[dict]
        Lista zdekodowanych obiektów Python (słowników) odczytanych z bufora.
    buffer : str
        Pozostały fragment tekstu po ostatnim '\n', do ponownego wykorzystania.

    Szczegóły implementacji:
    ------------------------
    - Wywołujemy sock.recv(4096), które zwraca ciąg bajtów lub rzuca BlockingIOError,
      jeśli nie ma nic do odczytu.
    - Jeśli recv() zwróci pusty ciąg "", oznacza to zerwanie połączenia.
    - Doklejamy odczytane dane do buffer, a następnie dzielimy bufor po '\n':
      * Każda linia przed '\n' jest parsowana za pomocą json.loads(),
      * pozostałość (fragment po ostatnim '\n') zachowujemy w bufferze.
    """
    messages = []
    try:
        data = sock.recv(4096).decode()
        if data == "":
            # Połączenie zostało zerwane po stronie przeciwnej
            raise ConnectionError("Połączenie zerwane")
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.strip() != "":
                obj = json.loads(line)
                messages.append(obj)
    except BlockingIOError:
        # Brak danych do odczytu – pomijamy
        pass
    return messages, buffer


def init_network():
    """
    Urządza proste menu konsolowe, w którym użytkownik wybiera:
    - [h] – host: bind, listen, accept() → czekamy na klienta,
    - [j] – join (klient): connect(host_ip, PORT).

    Po nawiązaniu połączenia ustawia socket jako nieblokujący i zwraca:
        (socket, my_player, is_host)

    Zwraca:
    --------
    sock : socket.socket
        Połączony, nieblokujący socket TCP.
    my_player : int
        Numer gracza w bieżącej instancji (1 = host, 2 = klient).
    is_host : bool
        True, jeśli to host; False, jeśli klient.
    """
    choice = ""
    while choice not in ("h", "j"):
        choice = input("Host [h] czy Join [j]? (h/j): ").strip().lower()

    if choice == "h":
        is_host = True
        my_player = 1
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("", PORT))
        server.listen(1)
        print(f"Host: nasłuchuję na porcie {PORT}...")
        conn, addr = server.accept()
        print(f"Klient połączony: {addr}")
        server.close()
        sock = conn
    else:
        is_host = False
        my_player = 2
        host_ip = input("Podaj adres IP hosta: ").strip()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host_ip, PORT))
        except Exception as e:
            print(f"Nie udało się połączyć: {e}")
            sys.exit(1)
        print("Połączono z hostem.")
        sock = client

    sock.setblocking(False)
    return sock, my_player, is_host
