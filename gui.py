"""
gui.py

Moduł zawierający funkcje rysujące planszę oraz interfejs gry w Pygame:
- draw_grid(): rysuje siatkę 10×10 wraz z zawartością (woda, statek, trafienie, pudło),
- get_cell_coords(): przetwarza współrzędne myszy na indeksy wiersza i kolumny,
- info_text(): generuje tekst informacyjny do wyświetlenia w dolnym pasku ekranu.
"""

import pygame

# Stałe odpowiadające kolorom w formacie RGB
COLOR_BG        = (30, 10, 40)    # ciemny fioletoworóżowy jako tło całego okna
COLOR_GRID_BG   = (50, 20, 60)    # ciemniejszy fiolet na obramowania siatki i dolny pasek
COLOR_WATER     = (255, 200, 230) # pastelowy jasnoróżowy na pola wody
COLOR_SHIP      = (200, 100, 150) # średni róż na fragmenty statków
COLOR_HIT       = (255, 100, 180) # intensywny róż na trafienia
COLOR_MISS      = (255, 220, 240) # bardzo jasny róż na pudła
COLOR_TEXT      = (250, 250, 255) # niemal biały, lekko różowawy na tekst
COLOR_HIGHLIGHT = (255, 150, 200) # jasny róż na obwódkę pola podświetlonego
COLOR_INVALID   = (255, 50, 120)  # mocny róż-puźnia na nieprawidłowe podświetlenie

# Wymiary interfejsu
BOARD_SIZE     = 10    # plansza 10×10
CELL_SIZE      = 40    # rozmiar jednego pola w pikselach
MARGIN         = 40    # margines od krawędzi okna do planszy
GRID_GAP       = 80    # odstęp między dwoma planszami
INFO_HEIGHT    = 60    # wysokość paska informacyjnego u dołu
WINDOW_WIDTH   = MARGIN * 2 + BOARD_SIZE * CELL_SIZE * 2 + GRID_GAP
WINDOW_HEIGHT  = MARGIN * 2 + BOARD_SIZE * CELL_SIZE + INFO_HEIGHT


def draw_grid(surface, top_left, board_matrix=None, hide_ships=False, highlight_cell=None):
    """
    Rysuje planszę 10×10 na podanej powierzchni Pygame.

    Parametry:
    ----------
    surface : pygame.Surface
        Obszar Pygame, na którym będzie rysowana plansza.
    top_left : tuple[int, int]
        Współrzędne (x0, y0) lewego górnego rogu, skąd zaczynamy rysować siatkę.
    board_matrix : list[list[str]] lub None
        Jeśli nie None, to dwuwymiarowa lista 10×10 z wartościami "~","S","X","O".
        None oznacza rysowanie samej siatki (woda).
    hide_ships : bool
        Jeśli True, pola oznaczone 'S' traktujemy jako wodę (funkcja przydatna do rysowania siatki
        przeciwnika, ukrywając statki).
    highlight_cell : tuple[int,int] lub None
        Jeśli nie None, zawiera (r,c) pojedynczego pola, które ma być podświetlone obwódką koloru
        COLOR_HIGHLIGHT. Używane przy ustawianiu statków do wyraźnego pokazania, gdzie stanie statek.

    Mechanika:
    ----------
    1. Dla każdego wiersza r w [0,BOARD_SIZE) i każdej kolumny c w [0,BOARD_SIZE):
       - Obliczamy prostokąt (pygame.Rect) o wymiarach CELL_SIZE×CELL_SIZE
         przesunięty o (top_left[0] + c*CELL_SIZE, top_left[1] + r*CELL_SIZE).
       - Domyślnie wypełniamy wodą (COLOR_WATER).
       - Jeśli board_matrix[r][c] istnieje, dobieramy kolor:
         '~' → COLOR_WATER,
         'S' → COLOR_SHIP (chyba że hide_ships=True → COLOR_WATER),
         'X' → COLOR_HIT,
         'O' → COLOR_MISS.
       - Rysujemy wypełniony prostokąt, a następnie obrys (COLOR_GRID_BG, szer. 1 px).
    2. Po narysowaniu całej siatki, jeśli `highlight_cell` jest podane i mieści się w zakresach,
       rysujemy obrys prostokąta kolorem COLOR_HIGHLIGHT (grubość 3 px) wokół danego pola.
    """
    x0, y0 = top_left
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(
                x0 + c * CELL_SIZE,
                y0 + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            color = COLOR_WATER

            if board_matrix:
                val = board_matrix[r][c]
                if val == "~":
                    color = COLOR_WATER
                elif val == "S":
                    color = COLOR_SHIP if not hide_ships else COLOR_WATER
                elif val == "X":
                    color = COLOR_HIT
                elif val == "O":
                    color = COLOR_MISS

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, COLOR_GRID_BG, rect, 1)

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


def get_cell_coords(mouse_pos, top_left):
    """
    Konwertuje współrzędne kursora (x,y) na współrzędne pola (r,c) na planszy.

    Parametry:
    ----------
    mouse_pos : tuple[int, int]
        Pozycja kursora myszy w oknie Pygame (x, y).
    top_left : tuple[int, int]
        Współrzędne (x0, y0) lewego górnego rogu planszy.

    Zwraca:
    --------
    (r, c) : tuple[int, int] lub (None, None)
        Indeksy wiersza i kolumny (0..9). Jeśli kursor jest poza zakresem planszy,
        zwraca (None, None).
    """
    x, y = mouse_pos
    x0, y0 = top_left
    rel_x = x - x0
    rel_y = y - y0
    if 0 <= rel_x < BOARD_SIZE * CELL_SIZE and 0 <= rel_y < BOARD_SIZE * CELL_SIZE:
        c = rel_x // CELL_SIZE
        r = rel_y // CELL_SIZE
        return int(r), int(c)
    return None, None


def info_text(current_phase, my_player, my_turn, ship_index, ships_list):
    """
    Generuje tekst informacyjny do wyświetlenia w dolnym pasku ekranu, w zależności od fazy gry.

    Parametry:
    ----------
    current_phase : str
        Aktualna faza gry: "placement", "waiting_opponent" lub "game".
    my_player : int
        Numer bieżącego gracza (1 lub 2).
    my_turn : bool
        True, jeśli to bieżąca tura (tylko w fazie "game").
    ship_index : int
        Indeks kolejnego statku do położenia (tylko w fazie "placement").
    ships_list : list[tuple[str,int]]
        Lista statków (nazwa, długość).

    Zwraca:
    --------
    str
        Sformatowany tekst do wyświetlenia w dolnej części ekranu.
    """
    if current_phase == "placement":
        if ship_index < len(ships_list):
            name, length = ships_list[ship_index]
            return f"Player {my_player}: ustawiasz '{name}' (długość {length}). R=rotuj. ENTER=gotowe"
        else:
            return f"Player {my_player}: naciśnij ENTER, gdy skończysz"
    elif current_phase == "waiting_opponent":
        return "Czekaj, aż przeciwnik też będzie gotowy..."
    else:  # "game"
        if my_turn:
            return f"Player {my_player}: kliknij w prawą planszę, aby atakować"
        else:
            return f"Player {my_player}: czekaj na ruch przeciwnika"
