"""
board.py

Moduł zawierający klasę Board, która odpowiada za logikę planszy gry „Statki”:
- przechowuje stan pól (woda, statek, trafienie, pudło),
- umożliwia umieszczanie statków,
- obsługuje przyjmowanie strzałów,
- sprawdza, czy wszystkie statki zostały zatopione.
"""

BOARD_SIZE = 10  # Standardowy rozmiar planszy: 10×10


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
    """

    def __init__(self):
        """
        Inicjalizuje nową planszę, wypełnioną wodą ('~').
        """
        self.grid = [["~"] * BOARD_SIZE for _ in range(BOARD_SIZE)]

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
            # Sprawdzamy, czy statek nie wyjdzie poza planszę w poziomie
            if col + length > BOARD_SIZE:
                return False
            # Sprawdzamy nakładanie się na inne statki
            for c in range(col, col + length):
                if self.grid[row][c] == "S":
                    return False
        else:  # orientacja "V"
            # Sprawdzamy, czy statek nie wyjdzie poza planszę w pionie
            if row + length > BOARD_SIZE:
                return False
            # Sprawdzamy nakładanie się na inne statki
            for r in range(row, row + length):
                if self.grid[r][col] == "S":
                    return False
        return True

    def place_ship(self, row, col, length, orient):
        """
        Umieszcza statek na planszy, oznaczając pola jako 'S'.

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
        if orient == "H":
            for c in range(col, col + length):
                self.grid[row][c] = "S"
        else:  # orientacja "V"
            for r in range(row, row + length):
                self.grid[r][col] = "S"

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
        True, jeśli trafił w fragment statku ('S'),
        False, jeśli chybił (pole było wody '~'),
        None, jeśli w to pole już wcześniej strzelano ('X' lub 'O').
        """
        cell = self.grid[row][col]
        if cell == "S":
            # Trafienie w statek
            self.grid[row][col] = "X"
            return True
        elif cell == "~":
            # Pudło (strzał w wodę)
            self.grid[row][col] = "O"
            return False
        else:
            # Już wcześniej strzelano w to pole
            return None

    def all_sunk(self):
        """
        Sprawdza, czy wszystkie fragmenty statków zostały trafione (czy nie ma już 'S').

        Zwraca:
        --------
        bool
            True, jeśli w grid nie ma już żadnego 'S'; False w przeciwnym razie.
        """
        for row in self.grid:
            if "S" in row:
                return False
        return True
