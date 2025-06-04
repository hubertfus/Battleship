
## **1. Strona tytułowa**

```
--------------------------------------------------------------------------
|                              GRA STATKI                                |
|                        (Battleship – Pygame LAN)                       |
|                                                                        |
| Autorzy:                                                               |
|  - Emilia Szczęch (GUI, Pygame, Integracja)                            |
|  - Nadia Schiffer (Logika planszy, moduł board.py, Integracja)         |
|  - Hubert Fusiarz (Komunikacja sieciowa, moduł network.py)             |
|                                                                        |
--------------------------------------------------------------------------
```

---

## **2. Spis treści**

1. [Strona tytułowa](#1-strona-tytułowa)
2. [Spis treści](#2-spis-treści)
3. [Opis projektu](#3-opis-projektu)

   1. [Cel projektu i czego dotyczy](#31-cel-projektu-i-czego-dotyczy)
   2. [Technologie i narzędzia](#32-technologie-i-narzędzia)
   3. [Kto wykonał którą część projektu](#33-kto-wykonał-którą-część-projektu)
   4. [Instrukcja instalacji](#34-instrukcja-instalacji)
4. [Struktura projektu](#4-struktura-projektu)

   1. [Opis katalogów i plików](#41-opis-katalogów-i-plików)
5. [opisy działania aplikacji oraz funkcjonalności](#5-zdjęcia--opisy-działania-aplikacji-oraz-funkcjonalności)
6. [Bibliografia](#6-bibliografia)

---

## **3. Opis projektu**

### **3.1. Cel projektu i czego dotyczy**

Projekt “Statki – Battleship” to klasyczna gra w stylu „statki” przeznaczona do rozgrywki dwuosobowej przez sieć LAN. Każdy gracz ustawia pięć statków na planszy 10×10 (po jednym Lotniskowcu, Okręcie Liniowym, Krążowniku, Podwodnym i Niszczycielu), a następnie naprzemiennie oddaje strzały w pola przeciwnika.

**Główne cele projektu**:

* Zaimplementowanie logiki planszy w oddzielnym module (`board.py`), w tym funkcjonalności
  sprawdzania poprawności ustawienia statków, przyjmowania strzałów oraz wykrywania zwycięzcy.
* Stworzenie graficznego interfejsu użytkownika (GUI) w Pygame (`gui.py`), umożliwiającego
  podgląd planszy, interakcję myszką i wyświetlanie informacji (podświetlenie pola, kolorystyka).
* Dodanie komunikacji sieciowej w module `network.py`, opartej na prostym protokole JSON po TCP,
  by pozwolić na rozgrywkę host–klient w lokalnej sieci.
* Integracja wszystkich modułów w skrypcie `main.py`, który steruje przepływem gry: faza
  ustawiania, faza oczekiwania na przeciwnika, faza oddawania strzałów oraz zakończenie gry.

### **3.2. Technologie i narzędzia**

* **Język programowania**: Python 3.12
* **Biblioteki/Frameworki**:

  * **Pygame 2.6.1** – rysowanie planszy, obsluga zdarzeń myszy i klawiatury, wyświetlanie tekstu.
  * **socket** (wbudowany) – nieblokująca komunikacja TCP dla hosta i klienta.
  * **json** (wbudowany) – serializacja/deserializacja komunikatów między hostem a klientem.
* **Środowisko uruchomieniowe**:

  * PEP8-friendly, uruchamiane na systemach Windows/Linux w Pythonie 3.12.
  * Virtual environment (zalecane utworzenie `.venv` oraz instalacja Pygame: `pip install pygame`).

### **3.3. Kto wykonał którą część projektu**

* **GUI – Pygame (gui.py)**:

  * Jan Kowalski – projekt kolorystyki (różowa paleta), podgląd położenia statku, rysowanie siatki, obramowania,
    pasek informacyjny, wyszarzanie pól przeciwnika, wyświetlanie komunikatów o zwycięstwie/przegranej.

* **Logika planszy (board.py)**:

  * Anna Nowak – klasa `Board` wraz z metodami:

    * `can_place()` (sprawdza poprawność ustawienia statku),
    * `place_ship()` (umieszczanie statku),
    * `receive_attack()` (obsługa trafień i pudel),
    * `all_sunk()` (sprawdzenie warunku zwycięstwa).

* **Komunikacja sieciowa (network.py)**:

  * Piotr Wiśniewski – funkcje TCP:

    * `init_network()` (menu host/klient, połączenie, nieblokujący socket),
    * `send_json()` (wysyłanie JSON z ‘\n’),
    * `try_receive_from_buffer()` (buforowany, nieblokujący odbiór JSON).

* **Integracja i sterowanie grą (main.py)**:

  * Marta Zielińska – pętla główna, zarządzanie fazami gry (ustawianie, oczekiwanie, rozgrywka),
    wywoływanie funkcji GUI i sieci oraz testy integracyjne.

* **Testy manualne i akceptacyjne**:

  * Wszyscy członkowie zespołu brali udział w testowaniu:

    * Weryfikacja wieloosobowej rozgrywki w LAN,
    * Sprawdzanie poprawności wyświetlania kolorów,
    * Obserwacja zachowania w przypadku utraty połączenia,
    * Testy graniczne (ustawianie statku tuż przy krawędzi planszy, strzelanie w to samo pole dwa razy).

### **3.4. Instrukcja instalacji**

1. **Wymagania wstępne**

   * Python 3.12.x lub nowszy.
   * Środowisko wirtualne (opcjonalnie, ale zalecane).

2. **Utworzenie i aktywacja wirtualnego środowiska**

   ```bash
   cd /ścieżka/do/projektu/battleship
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```

3. **Instalacja zależności**

   ```bash
   pip install pygame
   ```

4. **Struktura katalogu**

   ```
   battleship/
   ├── board.py
   ├── network.py
   ├── gui.py
   └── main.py
   ```

5. **Uruchomienie hosta**

   ```bash
   python main.py
   ```

   → W konsoli wpisz `h`, by uruchomić w trybie hosta (nasłuchiwanie na porcie 5000).

6. **Uruchomienie klienta**

   ```bash
   python main.py
   ```

   → W konsoli wpisz `j`, podaj adres IP hosta i port (domyślnie 5000).

7. **Rozpoczęcie gry**

   * Host i klient przechodzą do fazy „placement” (ustawianie statków).
   * Po zakończeniu ustawiania każdy gracz (host i klient) naciska `ENTER`, wysyła komunikat `ready`.
   * Gdy oba sygnały „ready” zostaną odebrane, następuje od razu faza „game” (rozgrywka sieciowa).
   * Host zaczyna pierwszym strzałem.

---

## **4. Struktura projektu**

```
battleship/
├── board.py
├── network.py
├── gui.py
└── main.py
```

### **4.1. Opis katalogów i plików**

* **`board.py`**
  Zawiera klasę `Board`, odpowiadającą za logikę planszy:

  * `__init__()` – tworzy pustą planszę z samą wodą,
  * `can_place(row, col, length, orient)` – weryfikuje, czy można umieścić statek,
  * `place_ship(row, col, length, orient)` – umieszcza statek na `self.grid`,
  * `receive_attack(row, col)` – przyjmuje strzał i zwraca `True/False/None`,
  * `all_sunk()` – sprawdza warunek zwycięstwa (czy wszystkie statki zostały zatopione).

* **`network.py`**
  Obsługuje komunikację TCP:

  * `init_network()` – menu host/klient, `bind()`, `listen()`, `accept()` lub `connect()`, `sock.setblocking(False)`, zwraca `(sock, my_player, is_host)`,
  * `send_json(sock, obj)` – serializuje i wysyła słownik Python jako JSON z `\n`,
  * `try_receive_from_buffer(sock, buffer)` – nieblokujący odbiór ze socketu, buforowanie i wyciąganie pełnych linii JSON-owych.

* **`gui.py`**
  Zawiera funkcje rysujące i pomocnicze:

  * `draw_grid(surface, top_left, board_matrix=None, hide_ships=False, highlight_cell=None)` – rysuje planszę 10×10 wg przekazanej macierzy,
  * `get_cell_coords(mouse_pos, top_left)` – przelicza współrzędne myszy na indeksy r,c pola,
  * `info_text(current_phase, my_player, my_turn, ship_index, ships_list)` – generuje pasek tekstu w zależności od fazy gry,
  * Stałe definiujące wymiary (BOARD\_SIZE, CELL\_SIZE, MARGIN, GRID\_GAP, INFO\_HEIGHT, WINDOW\_WIDTH, WINDOW\_HEIGHT) oraz kolorystykę (w tonacji różowej).

* **`main.py`**
  Integruje wszystkie moduły i zarządza przebiegiem gry:

  1. Inicjalizacja Pygame i połączenia sieciowego (`init_network()`),
  2. Tworzy obiekty `Board` dla `player_boards[1]` i `player_boards[2]`, oraz słowniki `guess_boards[1]`, `guess_boards[2]`,
  3. Faza “placement”: rysowanie planszy własnej, podświetlanie ustawianego statku, obsługa klawiatury i myszy,
  4. Faza “waiting\_opponent”: czekanie na komunikat `{"type":"ready"}`,
  5. Faza “game”: rysowanie obu plansz, wysyłanie ataków JSON, odbiór ataków i wyników, wyświetlanie komunikatów
     o zwycięstwie lub przegranej,
  6. Zamykanie socketu i Pygame po zakończeniu gry.

### **4.2. Diagram bazy danych**

Projekt nie wykorzystuje bazy danych. Całe przechowywanie stanu gry odbywa się w pamięci RAM, w strukturach Python (listy i słowniki).

---

## **5. Zdjęcia / opisy działania aplikacji oraz funkcjonalności**

### **5.1. Ekran ustawiania statków („placement”)**

* Gracz widzi swoją planszę 10×10 w tonacji różowej (pola wody – pastelowy róż, obramowania – ciemny fiolet).
* Po najechaniu kursorem na pole widać podświetlenie i podgląd kształtu wybranego statku w półprzezroczystym różu.
* Zielony (jasny róż) podgląd oznacza, że można tam umieścić statek; czerwone (mocny róż) – miejsce niepoprawne.
* Przykład kodu odpowiedzialnego za podświetlenie:

  ```python
    # W gui.py:
    if highlight_cell:
        hr, hc = highlight_cell
        if 0 <= hr < BOARD_SIZE and 0 <= hc < BOARD_SIZE:
            hrect = pygame.Rect(
                x0 + hc * CELL_SIZE,
                y0 + hr * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(surface, COLOR_HIGHLIGHT, hrect, 3)
  ```
* Po ułożeniu ostatniego statku gracz naciska `ENTER`, wysyła `{"type":"ready"}` i przechodzi do fazy „waiting\_opponent”.

---

### **5.2. Ekran oczekiwania na przeciwnika („waiting\_opponent”)**

* Wyświetlany jest tylko formularz z pustym tłem i dolnym paskiem:

  ```
  Czekaj, aż przeciwnik też będzie gotowy...
  ```
* Po otrzymaniu od drugiej strony `{"type":"ready"}` (oba „ready” odebrane), następuje bezpośrednie przejście do fazy „game” (bez dodatkowego ekranu przekazywania komputera).

---

### **5.3. Ekran rozgrywki („game”)**

* Po lewej stronie – własna plansza (statki szare, woda pastelowa różowa, trafienia intensywny róż, pudła jasny róż).
* Po prawej – plansza przeciwnika (pola trafień/pudła: X = intensywny róż, O = jasny róż; statki ukryte).
* Gdy jest moja tura (`my_turn = True`), w pasku informacyjnym pojawia się:

  ```
  Player 1: kliknij w prawą planszę, aby atakować
  ```

  lub

  ```
  Player 2: kliknij w prawą planszę, aby atakować
  ```
* Gdy nie jest moja tura:

  ```
  Player X: czekaj na ruch przeciwnika
  ```
* Gdy trafiony zostaje fragment statku (wynik „hit”), to trafione pole zmienia kolor na intensywny róż (COLOR\_HIT).
* Gdy pudło („miss”), to pole staje się jasny róż (COLOR\_MISS).

**Fragment kodu wysyłania ataku**:

```python
# W main.py, gdy current_phase == "game" i my_turn == True:
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    r2, c2 = get_cell_coords((mx, my), right_top)
    if r2 is not None and guess_boards[my_player][r2][c2] not in ("X", "O"):
        send_json(connection_sock, {
            "type": "attack",
            "row": r2,
            "col": c2
        })
        my_turn = False
```

---

### **5.4. Komunikat o wygranej / przegranej**

* Jeśli przeciwnik zatopi ostatni mój statek, po otrzymaniu „gameover”\:True w odpowiedzi
  od razu wyświetla się wieloliniowy komunikat w kolorze intensywnego różu:

  ```
  Player X przegrał!
  Dziękujemy za grę.
  ```
* Jeśli ja zatapiam ostatni statek przeciwnika, po otrzymaniu od niego „gameover”\:True
  wyświetla się komunikat w pastelowym zielonym (ewentualnie biało-różowym tle):

  ```
  Player X wygrał!
  Gratulacje!
  ```

**Przykład kodu wyświetlającego komunikat o przegranej**:

```python
if lost:
    screen.fill(COLOR_BG)
    lose_lines = [
        f"Player {my_player} przegrał!",
        "Dziękujemy za grę."
    ]
    for i, line in enumerate(lose_lines):
        text_surf = font.render(line, True, (255, 50, 50))
        screen.blit(
            text_surf,
            (
                WINDOW_WIDTH // 2 - text_surf.get_width() // 2,
                WINDOW_HEIGHT // 2 - 20 + i * 30
            )
        )
    pygame.display.flip()
    pygame.time.delay(3000)
    running = False
    break
```

---

## **6. Bibliografia**

1. **Pygame Documentation**

   * Oficjalna dokumentacja: [https://www.pygame.org/docs/](https://www.pygame.org/docs/)
   * Instrukcje instalacji i przykłady użycia modułu pygame.draw, pygame.Rect, obsługa zdarzeń.

2. **Python Socket Programming HOWTO**

   * Oficjalne źródło Python: [https://docs.python.org/3/howto/sockets.html](https://docs.python.org/3/howto/sockets.html)
   * Opis tworzenia serwera TCP, klienta TCP, trybu nieblokującego socket.

3. **JSON w Pythonie**

   * Oficjalna dokumentacja: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)
   * Serializacja obiektów Python (słowników) do JSON, deserializacja.
