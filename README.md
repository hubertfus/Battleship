## **1. Strona tytułowa**

```
--------------------------------------------------------------------------
|                              GRA STATKI                                |
|                        (Battleship – Pygame LAN)                       |
|                                                                        |
| Autorzy:                                                               |
|  – Emilia Szczęch (interfejs graficzny, Pygame, integracja)            |
|  – Nadia Schiffer (logika planszy, moduł board.py, integracja)         |
|  – Hubert Fusiarz (komunikacja sieciowa, moduł network.py)             |
|                                                                        |
--------------------------------------------------------------------------
```

---

## **2. Spis treści**

1. [Strona tytułowa](#1-strona-tytułowa)
2. [Spis treści](#2-spis-treści)
3. [Opis projektu](#3-opis-projektu)

   1. [Cel projektu i zakres](#31-cel-projektu-i-zakres)
   2. [Technologie i narzędzia](#32-technologie-i-narzędzia)
   3. [Instrukcja instalacji](#33-instrukcja-instalacji)
4. [Struktura projektu](#4-struktura-projektu)

   1. [Opis plików i katalogów](#41-opis-plików-i-katalogów)
5. [Opis działania aplikacji i jej funkcjonalności](#5-opis-działania-aplikacji-i-jej-funkcjonalności)

   1. [Faza „placement” (ustawianie statków)](#51-faza-placement-ustawianie-statków)
   2. [Faza „waiting\_opponent” (oczekiwanie na przeciwnika)](#52-faza-waiting_opponent-oczekiwanie-na-przeciwnika)
   3. [Faza „game” (rozgrywka)](#53-faza-game-rozgrywka)
   4. [Komunikat o wyniku gry](#54-komunikat-o-wyniku-gry)
6. [Bibliografia](#6-bibliografia)

---

## **3. Opis projektu**

### **3.1. Cel projektu i zakres**

Projekt „Statki – Battleship” stanowi implementację klasycznej, dwuosobowej gry w „statki” z wykorzystaniem połączenia sieciowego LAN. Każdy z uczestników rozgrywki rozmieszcza pięć jednostek na planszy o rozmiarze 10×10 (lotniskowiec, okręt liniowy, krążownik, okręt podwodny oraz niszczyciel), a następnie, na przemian, oddaje strzały próbując zatopić wszystkie statki przeciwnika.

**Główne założenia projektu:**

* Opracowanie modułu `board.py`, który realizuje logikę planszy: sprawdzanie poprawności rozmieszczenia jednostek, przetwarzanie strzałów oraz wykrywanie stanu końcowego gry (zatopienia wszystkich statków).
* Stworzenie graficznego interfejsu użytkownika w bibliotece Pygame (`gui.py`), umożliwiającego wyświetlanie planszy, interakcję poprzez mysz oraz prezentację informacji prawidłowości wyboru pól (np. kolory podświetlenia).
* Zaimplementowanie modułu `network.py`, odpowiedzialnego za komunikację sieciową w oparciu o protokół JSON po TCP, co umożliwi tryb host–klient w sieci lokalnej.
* Połączenie wszystkich składowych projektu w skrypcie `main.py`, który koordynuje poszczególne fazy rozgrywki: ustawianie statków, oczekiwanie na gotowość przeciwnika, przeprowadzanie ataków oraz zakończenie gry.

### **3.2. Technologie i narzędzia**

* **Język programowania**: Python 3.12
* **Biblioteki i moduły**:

  * **Pygame 2.6.1** – odpowiedzialna za rysowanie planszy, obsługę zdarzeń myszy i klawiatury oraz renderowanie tekstu.
  * **`socket`** (wbudowany) – realizacja nieblokującej komunikacji TCP dla hosta i klienta.
  * **`json`** (wbudowany) – serializacja i deserializacja komunikatów sieciowych pomiędzy hostem a klientem.
* **Środowisko uruchomieniowe**:

  * Zgodność z wytycznymi PEP 8; praca na systemach Windows oraz Linux w Pythonie 3.12.
  * Rekomendowane utworzenie wirtualnego środowiska Python (`.venv`) oraz instalacja biblioteki Pygame poprzez `pip install pygame`.

### **3.3. Instrukcja instalacji**

1. **Wymagania wstępne**

   * Interpreter Python w wersji 3.12 lub wyższej.
   * Utworzenie wirtualnego środowiska (opcjonalnie, lecz zalecane).

2. **Utworzenie i aktywacja środowiska wirtualnego**

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

4. **Struktura katalogu projektu**

   ```
   battleship/
   ├── board.py
   ├── network.py
   ├── gui.py
   └── main.py
   ```

5. **Uruchomienie trybu hosta**

   ```bash
   python main.py
   ```

   Po uruchomieniu program wyświetli monit w konsoli. Należy wprowadzić literę `h`, aby uruchomić aplikację w roli hosta (nasłuchiwanie na porcie 5000).

6. **Uruchomienie trybu klienta**

   ```bash
   python main.py
   ```

   Po uruchomieniu należy w konsoli wpisać literę `j`, a następnie podać adres IP hosta oraz port (standardowo 5000).

7. **Rozpoczęcie rozgrywki**

   * Host i klient przechodzą do fazy „placement” (ustawianie statków).
   * Po rozmieszczeniu wszystkich jednostek każdy z graczy naciska klawisz `ENTER`, co wysyła komunikat `{"type": "ready"}`.
   * Gdy obie strony odbiorą sygnał „ready”, następuje faza „game” (rozgrywka sieciowa).
   * Inicjatorem pierwszego strzału jest host.

---

## **4. Struktura projektu**

```
battleship/
├── board.py
├── network.py
├── gui.py
└── main.py
```

### **4.1. Opis plików i katalogów**

* **`board.py`**
  Zawiera klasę `Board`, odpowiadającą za całą logikę związanej z planszą gry:

  * `__init__()` – inicjalizacja pustej planszy wypełnionej „wodą”.
  * `can_place(row, col, length, orient)` – weryfikacja poprawności umieszczenia jednostki o długości `length` w pozycji (`row`, `col`) z orientacją `orient`.
  * `place_ship(row, col, length, orient)` – faktyczne rozmieszczenie jednostki na siatce `self.grid`.
  * `receive_attack(row, col)` – obsługa oddanego strzału i zwrócenie odpowiedniego wyniku (`True` – trafienie, `False` – pudło, `None` – pole już wcześniej ostrzelane).
  * `all_sunk()` – sprawdzenie, czy wszystkie jednostki zostały zatopione (warunek zwycięstwa).

* **`network.py`**
  Realizuje komunikację TCP między hostem a klientem:

  * `init_network()` – wyświetlenie menu wyboru roli hosta lub klienta, wykonywanie operacji `bind()`, `listen()`, `accept()` lub `connect()`, ustawienie trybu nieblokującego (`sock.setblocking(False)`), zwracanie krotki `(sock, my_player, is_host)`.
  * `send_json(sock, obj)` – serializacja słownika Pythona do formatu JSON wraz ze znakami końca linii `\n` i wysłanie go przez socket.
  * `try_receive_from_buffer(sock, buffer)` – nieblokujące odbieranie danych z gniazda, gromadzenie w buforze i wyodrębnianie pełnych linii w formacie JSON.

* **`gui.py`**
  Zawiera funkcje związane z rysowaniem interfejsu oraz pomocnicze stałe:

  * `draw_grid(surface, top_left, board_matrix=None, hide_ships=False, highlight_cell=None)` – rysowanie planszy 10×10 na wskazanej powierzchni (`surface`), z uwzględnieniem stanu pól (`board_matrix`), ewentualnym ukryciem jednostek (`hide_ships`) oraz podświetleniem wskazanego pola (`highlight_cell`).
  * `get_cell_coords(mouse_pos, top_left)` – przeliczanie współrzędnych kursora myszy (`mouse_pos`) na wiersz i kolumnę planszy, biorąc pod uwagę położenie lewego górnego rogu planszy (`top_left`).
  * `info_text(current_phase, my_player, my_turn, ship_index, ships_list)` – generowanie tekstu informacyjnego umieszczanego pod planszą, zależnie od aktualnej fazy gry oraz stanu rozgrywki.
  * Definicje stałych, określających wymiary planszy (np. `BOARD_SIZE`, `CELL_SIZE`, `MARGIN`, `GRID_GAP`, `INFO_HEIGHT`, `WINDOW_WIDTH`, `WINDOW_HEIGHT`) oraz paletę kolorów utrzymaną w tonacji różowej.

* **`main.py`**
  Moduł koordynujący przebieg całej gry, integrujący pozostałe moduły:

  1. Inicjalizacja biblioteki Pygame oraz zestawienie połączenia w trybie host–klient (`init_network()`).
  2. Utworzenie obiektów `Board` dla obu graczy (`player_boards[1]` oraz `player_boards[2]`), a także struktur przechowujących stany planszy zgadywań (`guess_boards[1]`, `guess_boards[2]`).
  3. Faza „placement”: rysowanie własnej planszy, podświetlanie proponowanego położenia jednostki, obsługa zdarzeń myszy i klawiatury w celu rozmieszczania statków.
  4. Faza „waiting\_opponent”: oczekiwanie na sygnał gotowości od przeciwnika (`{"type": "ready"}`).
  5. Faza „game”: wyświetlanie obu plansz (własnej i przeciwnika), przesyłanie komunikatów JSON reprezentujących ataki, odbiór odpowiedzi, aktualizacja stanów plansz oraz wyświetlanie komunikatów o trafieniach, pudłach i sytuacji zwycięstwa/przegranej.
  6. Zamykanie połączenia sieciowego i zamknięcie okna Pygame po zakończeniu rozgrywki.

---

## **5. Opis działania aplikacji i jej funkcjonalności**

### **5.1. Faza „placement” (ustawianie statków)**

* Gracz obserwuje swoją planszę 10×10 utrzymaną w tonacji różowej (tło pól wody w pastelowym różu, obramowania w odcieniu ciemnego fioletu).

* W momencie, gdy kursor myszy znajduje się nad dowolnym polem, następuje podświetlenie tego pola oraz wyświetlenie półprzezroczystego kształtu statku, który aktualnie jest ustawiany.

  * Podgląd w kolorze jasnego różu (zielony odcień) oznacza, że w danym położeniu można poprawnie umieścić jednostkę.
  * Podgląd w intensywnym odcieniu różu (czerwony odcień) sygnalizuje, że zaproponowana lokalizacja jest niepoprawna (np. kolizja z innym statkiem lub wykraczanie poza zakres planszy).

* Fragment kodu odpowiedzialny za podświetlenie wyróżnionego pola przedstawia się następująco (zawartość pliku `gui.py`):

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

* Po rozmieszczeniu ostatniego statku, gracz naciska klawisz `ENTER`. Wówczas wysyłany jest komunikat:

  ```json
  {"type": "ready"}
  ```

  i następuje przejście do fazy „waiting\_opponent” (oczekiwanie na gotowość przeciwnika).

---

### **5.2. Faza „waiting\_opponent” (oczekiwanie na przeciwnika)**

* W tej fazie na ekranie wyświetlany jest jednolity ekran z komunikatem:

  ```
  Czekaj, aż przeciwnik również będzie gotowy...
  ```

  umieszczonym w dolnej części ekranu na pasku informacyjnym.
* Gdy program odbierze od drugiej strony sygnał:

  ```json
  {"type": "ready"}
  ```

  obustronnie, natychmiast przełączane jest środowisko do fazy „game” (rozgrywka sieciowa). Nie występuje wówczas żaden dodatkowy ekran przekazywania sterowania.

---

### **5.3. Faza „game” (rozgrywka)**

* Widok ekranu w tej fazie jest podzielony na dwie części:

  * Po lewej stronie widoczna jest własna plansza z rozmieszczonymi statkami (statki w kolorze szarym, tło wody w pastelowym różu, trafione pola w intensywnym różu, pudła w jasnym różu).
  * Po prawej stronie wyświetlana jest plansza przeciwnika, na której statki pozostają niewidoczne (widoczne jedynie trafienia i pudła – „X” w kolorze intensywnego różu, „O” w odcieniu jasnego różu).

* Gdy jest tura gracza (`my_turn == True`), pasek informacyjny prezentuje komunikat:

  ```
  Player 1: kliknij w prawą planszę, aby wykonać atak
  ```

  lub

  ```
  Player 2: kliknij w prawą planszę, aby wykonać atak
  ```

* Jeśli nie jest tura gracza, tekst przyjmuje formę:

  ```
  Player X: oczekiwanie na ruch przeciwnika
  ```

* W przypadku trafienia fragmentu statku („hit”), odpowiednie pole zostaje wypełnione kolorem intensywnego różu (COLOR\_HIT). Natomiast w przypadku pudła („miss”) pole przybiera barwę jasnego różu (COLOR\_MISS).

* Fragment kodu odpowiedzialny za wysyłanie komunikatu o ataku znajduje się w pliku `main.py` i jest wykonywany, gdy aktualna faza to „game” oraz `my_turn == True`:

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

* Po wysłaniu komunikatu `{"type": "attack", "row": r2, "col": c2}`, program oczekuje na odpowiedź od przeciwnika, informującą o wyniku strzału („hit”, „miss” lub „gameover”).

---

### **5.4. Komunikat o wyniku gry**

* Jeśli przeciwnik zatopi ostatni statek gracza, po otrzymaniu od niego komunikatu zwrotnego zawierającego klucz `"gameover": True`, natychmiast wyświetlany jest komunikat o przegranej w kolorze intensywnego różu:

  ```
  Player X przegrał!
  Dziękujemy za grę.
  ```

* Analogicznie, gdy gracz zatopi ostatni statek przeciwnika (otrzyma od niego `"gameover": True`), wyświetlany jest komunikat o zwycięstwie w kolorystyce pastelowego zielonego (ewentualnie biało-różowym tle):

  ```
  Player X wygrał!
  Gratulacje!
  ```

* Przykładowy fragment kodu odpowiedzialny za wyświetlenie treści przegranej:

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
   – Oficjalna dokumentacja: [https://www.pygame.org/docs/](https://www.pygame.org/docs/)
   – Instrukcje instalacji oraz przykłady użycia modułów `pygame.draw`, `pygame.Rect` i obsługi zdarzeń.

2. **Python Socket Programming HOWTO**
   – Oficjalna strona dokumentacji: [https://docs.python.org/3/howto/sockets.html](https://docs.python.org/3/howto/sockets.html)
   – Szczegółowe informacje na temat tworzenia serwera i klienta TCP oraz wykorzystywania nieblokujących gniazd.

3. **JSON w Pythonie**
   – Dokumentacja biblioteki: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)
   – Opis metod serializacji obiektów Python (np. słowników) do formatu JSON oraz deserializacji.
