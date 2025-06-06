# main.py

"""
Główna część aplikacji, która integruje moduły:
- board.py  → logika planszy,
- network.py → komunikacja TCP w trybie host/klient,
- gui.py     → rysowanie interfejsu w Pygame.

Schemat działania:
1. Inicjalizacja Pygame oraz połączenia sieciowego (host/klient).
2. Faza "placement" – każdy gracz (host to gracz 1, klient to gracz 2) ustawia swoje statki.
3. Gdy gracz zakończy ustawianie i naciśnie ENTER, wysyła {"type":"ready"} i czeka na gotowość przeciwnika.
4. Po obu komunikatach "ready" przechodzimy bezpośrednio do fazy "game" → rozgrywka on-line:
   - Host (gracz 1) atakuje pierwszy, klient czeka.
   - Strzał to wysłanie {"type":"attack","row":r,"col":c}.
   - Przeciwnik odbiera, wywołuje receive_attack() dla własnej planszy → zwraca (hit, sunk).
   - Na tej podstawie odtwarzamy dźwięk trafienia/pudła/zatopienia statku → odsyłamy {"type":"result","hit":..., "sunk":..., "gameover":...}.
   - W tle leci muzyka.
   - Zwycięzca/przegrany zobaczy odpowiedni komunikat, a gra zakończy się.
"""

import pygame
import pygame.mixer
import sys
from board import Board
from network import send_json, try_receive_from_buffer, init_network
from gui import (
    draw_grid,
    get_cell_coords,
    info_text,
    BOARD_SIZE,
    CELL_SIZE,
    MARGIN,
    GRID_GAP,
    INFO_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLOR_BG,
    COLOR_GRID_BG, COLOR_INVALID, COLOR_HIGHLIGHT, COLOR_TEXT,
)
import json

# Lista statków (nazwa, długość)
SHIPS = [
    ("Lotniskowiec", 5),
    ("Okręt liniowy", 4),
    ("Krążownik", 3),
    ("Podwodny", 3),
    ("Niszczyciel", 2),
]


def main():
    """
    Funkcja uruchamiająca grę:
    - Inicjalizuje Pygame.
    - Tworzy instancje planszy dla obu graczy.
    - Inicjalizuje połączenie sieciowe (host/klient).
    - Obsługuje pętlę główną, uwzględniając:
       * fazę 'placement',
       * fazę 'waiting_opponent',
       * fazę 'game'.
    - Po zakończeniu (zwycięstwo/przegrana) zamyka socket i kończy działanie Pygame.
    """
    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load("sounds/bg_music.mp3")
    pygame.mixer.music.set_volume(0.0)
    pygame.mixer.music.play(-1)

    miss_sound = pygame.mixer.Sound("sounds/miss.mp3")
    hit_sound  = pygame.mixer.Sound("sounds/hit.mp3")
    sink_sound = pygame.mixer.Sound("sounds/sink.mp3")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Statki Sieciowe (Pygame)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)
    small_font = pygame.font.SysFont("arial", 18)

    # Plansze: player_boards[1] – plansza hosta; player_boards[2] – plansza klienta
    player_boards = {
        1: Board(),
        2: Board()
    }
    # guess_boards przechowują strzały skierowane do przeciwnika
    guess_boards = {
        1: [["~"] * BOARD_SIZE for _ in range(BOARD_SIZE)],
        2: [["~"] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    }

    global current_phase, ship_index, orientation, my_turn, ready_received, net_buffer, my_player
    current_phase = "placement"     # Początkowo obie strony w fazie ustawiania
    orientation = "H"               # Domyślna orientacja statku: poziomo
    ship_index = 0                  # Indeks pierwszego statku do ustawienia
    my_turn = False                 # W fazie 'game' host zacznie turę, więc ustawimy niżej
    ready_received = False          # Czy otrzymaliśmy {"type":"ready"} od przeciwnika
    net_buffer = ""                 # Bufor do odczytu JSON

    connection_sock, my_player, is_host = init_network()


    my_turn = False

    running = True
    while running:
        clock.tick(30)
        screen.fill(COLOR_BG)

        left_top = (MARGIN, MARGIN)
        right_top = (MARGIN + BOARD_SIZE * CELL_SIZE + GRID_GAP, MARGIN)

        mx, my = pygame.mouse.get_pos()
        highlight = None

        # 0) Jeśli w fazie 'game', odczytujemy komunikaty sieciowe (attack/result)
        if current_phase == "game" and connection_sock:
            msgs, net_buffer = try_receive_from_buffer(connection_sock, net_buffer)
            for msg in msgs:
                if msg["type"] == "attack":
                    """
                    Obserwujemy ruch przeciwnika:
                    - Otrzymaliśmy r, c → wykonujemy receive_attack() dla własnej planszy.
                    - Sprawdzamy, czy dany statek został zatopiony (sunk) oraz czy cała flota przegrała (all_sunk).
                    - Odsylamy reply: {"type":"result", "row":r, "col":c, "hit":..., "sunk":..., "gameover":...}.
                    - Jeśli przegrałem całą flotę, wyświetlam komunikat przegranego i kończymy.
                    - W przeciwnym razie, my_turn = True.
                    """
                    r = msg["row"]
                    c = msg["col"]
                    res, sunk = player_boards[my_player].receive_attack(r, c)
                    lost = False

                    if res and player_boards[my_player].all_sunk():
                        lost = True

                    if res is True:
                        if sunk:
                            sink_sound.play()
                        else:
                            hit_sound.play()
                    elif res is False:
                        miss_sound.play()

                    reply = {
                        "type": "result",
                        "row": r,
                        "col": c,
                        # jeśli res jest None, to zwracamy False
                        "hit": False if res is None else res,
                        "sunk": True if sunk else False,
                        "gameover": lost
                    }
                    send_json(connection_sock, reply)

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

                    my_turn = True

                elif msg["type"] == "result":
                    """
                    Odpowiedź na mój atak:
                    - msg["hit"] → prawda/fałsz, msg["sunk"] → czy mój atak zatopił cały okręt,
                      msg["gameover"] → czy cała flota przeciwnika właśnie przegrała.
                    - Aktualizujemy guess_boards: 'X' jeśli trafienie, 'O' jeśli pudło.
                    - Odtwarzamy odpowiedni dźwięk (hit/miss/sink).
                    - Jeśli gameover == True → wyświetlamy komunikat zwycięzcy i kończymy.
                    - W przeciwnym razie: my_turn = False.
                    """
                    r = msg["row"]
                    c = msg["col"]
                    hit = msg.get("hit", False)
                    sunk = msg.get("sunk", False)
                    gameov = msg.get("gameover", False)

                    if hit:
                        if sunk:
                            sink_sound.play()
                        else:
                            hit_sound.play()
                        guess_boards[my_player][r][c] = "X"
                    else:
                        miss_sound.play()
                        guess_boards[my_player][r][c] = "O"

                    if gameov:
                        screen.fill(COLOR_BG)
                        win_lines = [
                            f"Player {my_player} wygrał!",
                            "Gratulacje!"
                        ]
                        for i, line in enumerate(win_lines):
                            text_surf = font.render(line, True, (50, 255, 50))
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

                    my_turn = False

        # 1) FAZA "placement" – rysowanie własnej planszy i podgląd statku
        if current_phase == "placement":
            draw_grid(
                screen,
                left_top,
                board_matrix=player_boards[my_player].grid,
                hide_ships=False,
                highlight_cell=None
            )
            draw_grid(
                screen,
                right_top,
                board_matrix=None,
                hide_ships=False,
                highlight_cell=None
            )

            r_h, c_h = get_cell_coords((mx, my), left_top)
            if r_h is not None and ship_index < len(SHIPS):
                highlight = (r_h, c_h)
                name, length = SHIPS[ship_index]
                preview_cells = []
                valid_placement = True

                if orientation == "H":
                    for dc in range(length):
                        rr = r_h
                        cc = c_h + dc
                        if cc >= BOARD_SIZE:
                            valid_placement = False
                            break
                        if player_boards[my_player].grid[rr][cc] == "S":
                            valid_placement = False
                        preview_cells.append((rr, cc))
                else:  # orientacja "V"
                    for dr in range(length):
                        rr = r_h + dr
                        cc = c_h
                        if rr >= BOARD_SIZE:
                            valid_placement = False
                            break
                        if player_boards[my_player].grid[rr][cc] == "S":
                            valid_placement = False
                        preview_cells.append((rr, cc))

                for (rr, cc) in preview_cells:
                    cell_rect = pygame.Rect(
                        left_top[0] + cc * CELL_SIZE,
                        left_top[1] + rr * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    if valid_placement and len(preview_cells) == length:
                        overlay.fill((*COLOR_HIGHLIGHT, 100))
                    else:
                        overlay.fill((*COLOR_INVALID, 100))
                    screen.blit(overlay, cell_rect.topleft)

        # 2) FAZA "waiting_opponent" – czekanie na "ready"
        elif current_phase == "waiting_opponent":
            screen.fill(COLOR_BG)
            pygame.draw.rect(
                screen,
                COLOR_GRID_BG,
                (0, WINDOW_HEIGHT - INFO_HEIGHT, WINDOW_WIDTH, INFO_HEIGHT)
            )
            info_surf = small_font.render(info_text(current_phase, my_player, my_turn, ship_index, SHIPS), True, COLOR_TEXT)
            screen.blit(info_surf, (MARGIN, WINDOW_HEIGHT - INFO_HEIGHT + 15))
            pygame.display.flip()

            msgs, net_buffer = try_receive_from_buffer(connection_sock, net_buffer)
            for msg in msgs:
                if msg.get("type") == "ready":
                    ready_received = True

            if ready_received:
                current_phase = "game"
                my_turn = is_host

            continue

        # 3) FAZA "game" – rysujemy obie plansze
        else:
            draw_grid(
                screen,
                left_top,
                board_matrix=player_boards[my_player].grid,
                hide_ships=False,
                highlight_cell=None
            )
            draw_grid(
                screen,
                right_top,
                board_matrix=guess_boards[my_player],
                hide_ships=False,
                highlight_cell=None
            )

        # 4) Pasek informacyjny
        pygame.draw.rect(
            screen,
            COLOR_GRID_BG,
            (0, WINDOW_HEIGHT - INFO_HEIGHT, WINDOW_WIDTH, INFO_HEIGHT)
        )
        info_surf = small_font.render(info_text(current_phase, my_player, my_turn, ship_index, SHIPS), True, COLOR_TEXT)
        screen.blit(info_surf, (MARGIN, WINDOW_HEIGHT - INFO_HEIGHT + 15))

        # 5) Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Faza "placement"
            if current_phase == "placement":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Zmiana orientacji H ↔ V
                    orientation = "V" if orientation == "H" else "H"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Gdy wszystkie statki położone, wysyłamy "ready" i czekamy
                    if ship_index >= len(SHIPS):
                        send_json(connection_sock, {"type": "ready"})
                        current_phase = "waiting_opponent"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and ship_index < len(SHIPS):
                    r, c = get_cell_coords((mx, my), left_top)
                    if r is not None:
                        name, length = SHIPS[ship_index]
                        if player_boards[my_player].can_place(r, c, length, orientation):
                            player_boards[my_player].place_ship(r, c, length, orientation)
                            ship_index += 1
                        else:
                            # Wyświetlamy krótki komunikat o nieprawidłowym położeniu
                            err = small_font.render("Nieprawidłowe miejsce!", True, (255, 100, 100))
                            screen.blit(err, (MARGIN, WINDOW_HEIGHT - INFO_HEIGHT + 35))
                            pygame.display.flip()
                            pygame.time.delay(600)

            # Faza "game" – wysyłamy atak, jeśli moja tura
            elif current_phase == "game" and my_turn:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    r2, c2 = get_cell_coords((mx, my), right_top)
                    if r2 is not None and guess_boards[my_player][r2][c2] not in ("X", "O"):
                        send_json(connection_sock, {"type": "attack", "row": r2, "col": c2})
                        my_turn = False

        pygame.display.flip()

    # Po zakończeniu gry zatrzymujemy muzykę, zamykamy socket i kończymy Pygame
    pygame.mixer.music.stop()
    try:
        connection_sock.close()
    except:
        pass
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
