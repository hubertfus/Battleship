# board.py

"""
Moduł zawierający klasę Board, która odpowiada za logikę planszy gry „Statki”:
- przechowuje stan pól (woda, statek, trafienie, pudło),
- umożliwia umieszczanie statków,
- obsługuje przyjmowanie strzałów,
- sprawdza, czy wszystkie statki zostały zatopione.
"""

BOARD_SIZE = 10

class Board:
    """
    Reprezentacja logiki planszy gry „Statki” (10×10).

    Atrybuty:
    ----------
    grid : list[list[str]]
        Dwuwymiarowa lista 10×10, w której:
            '~' – pole wody (pustego),
            'S' – fragment statku,
            'X' – trafione (fragment statku zmieniony z 'S'),
            'O' – pudło (strzał w wodę zmieniony z '~').
    ships : list[dict]
        Lista słowników opisujących każdy umieszczony statek:
            {
                "cells": [(r1, c1), (r2, c2), ...],  # wszystkie współrzędne statku
                "hits": set()                        # trafione fragmenty tego statku
            }
    """

    def __init__(self):
        """
        Inicjalizuje nową planszę, wypełnioną wodą ('~') i pustą listę statków.
        """
        self.grid = [["~"] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ships = []  # Lista słowników opisujących każdy statek

    def can_place(self, row, col, length, orient):
        """
        Sprawdza, czy można umieścić statek o zadanej długości i orientacji
        na polu zaczynającym się w wierszu `row`, kolumnie `col`.

        Parametry:
        ----------
        row : int
            Wiersz początkowy (0-indeks).
        col : int
            Kolumna początkowa (0-indeks).
        length : int
            Długość statku (ilość kolejnych pól).
        orient : str
            Orientacja: 'H' (poziomo) lub 'V' (pionowo).

        Zwraca:
        --------
        bool
            True, jeśli statek mieści się w granicach planszy i nie nachodzi na inne,
            False – w przeciwnym razie.
        """
        if orient == "H":
            if col + length > BOARD_SIZE:
                return False
            for c in range(col, col + length):
                if self.grid[row][c] == "S":
                    return False
        else:  # orientacja "V"
            if row + length > BOARD_SIZE:
                return False
            for r in range(row, row + length):
                if self.grid[r][col] == "S":
                    return False
        return True

    def place_ship(self, row, col, length, orient):
        """
        Umieszcza statek na planszy, oznaczając pola jako 'S' i rejestruje go w self.ships.

        Parametry:
        ----------
        row : int
            Wiersz początkowy (0-indeks) pola, od którego zaczyna się statek.
        col : int
            Kolumna początkowa (0-indeks).
        length : int
            Długość statku.
        orient : str
            'H' – poziomo; 'V' – pionowo.
        """
        cells = []
        if orient == "H":
            for c in range(col, col + length):
                self.grid[row][c] = "S"
                cells.append((row, c))
        else:  # orientacja "V"
            for r in range(row, row + length):
                self.grid[r][col] = "S"
                cells.append((r, col))

        self.ships.append({
            "cells": cells,
            "hits": set()
        })

    def receive_attack(self, row, col):
        """
        Przyjmuje strzał w pole (row, col), aktualizuje stan i zwraca rezultat.

        Parametry:
        ----------
        row : int
            Wiersz trafionego pola (0-indeks).
        col : int
            Kolumna trafionego pola (0-indeks).

        Zwraca:
        --------
        (hit, sunk) : tuple
            hit : bool lub None
                True  – trafienie w statek,
                False – pudło,
                None  – w to pole już wcześniej strzelano.
            sunk : bool
                True  – jeśli trafienie zatopiło cały dany statek,
                False – w przeciwnym razie.
        """
        cell = self.grid[row][col]
        # 1) Sprawdzamy, czy w to pole już wcześniej strzelano
        if cell in ("X", "O"):
            return None, False

        # 2) Trafienie w statek
        if cell == "S":
            self.grid[row][col] = "X"
            for ship in self.ships:
                if (row, col) in ship["cells"]:
                    ship["hits"].add((row, col))
                    sunk = set(ship["cells"]) == ship["hits"]
                    return True, sunk
            return True, False

        # 3) Pudło
        if cell == "~":
            self.grid[row][col] = "O"
            return False, False

        return None, False

    def all_sunk(self):
        """
        Sprawdza, czy wszystkie fragmenty statków zostały trafione (czy żaden 'S' nie pozostał).

        Zwraca:
        --------
        bool
            True, jeśli w grid nie ma już żadnego 'S'; False w przeciwnym razie.
        """
        for row in self.grid:
            if "S" in row:
                return False
        return True
