from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Dict

from .data import MAX_WRONG_GUESSES, pick_word


@dataclass
class GuessResult:
    status: str  # 'correct' | 'wrong' | 'repeat'
    positions: List[int]
    complete: bool
    game_over: bool


class GameLogic:
    def __init__(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.category, self.word = pick_word(difficulty)
        self.gameboard: List[str] = ["_"] * len(self.word)
        self.guessed_letters: Set[str] = set()
        self.wrong_guesses: int = 0
        self.max_wrong: int = MAX_WRONG_GUESSES

    # Presentation helpers
    @property
    def hint_text(self) -> str:
        return f"Hint- Category: {self.category.capitalize()}\nFirst letter: {self.word[0].upper()}"

    @property
    def board_text(self) -> str:
        return " ".join(self.gameboard)

    @property
    def guesses_text(self) -> str:
        if not self.guessed_letters:
            return "Guesses:"
        return "Guesses: " + ", ".join(sorted(self.guessed_letters))

    @property
    def lives_text(self) -> str:
        return f"Lives({self.max_wrong}): " + "x " * self.wrong_guesses

    def is_complete(self) -> bool:
        return "_" not in self.gameboard

    def is_game_over(self) -> bool:
        return self.wrong_guesses >= self.max_wrong

    def guess(self, letter: str) -> GuessResult:
        letter = letter.lower()
        if not (len(letter) == 1 and letter.isalpha()):
            return GuessResult(status="wrong", positions=[], complete=self.is_complete(), game_over=self.is_game_over())

        if letter in self.guessed_letters or letter in self.gameboard:
            return GuessResult(status="repeat", positions=[], complete=self.is_complete(), game_over=self.is_game_over())

        self.guessed_letters.add(letter)

        positions: List[int] = []
        for i, ch in enumerate(self.word):
            if ch == letter:
                positions.append(i)
                self.gameboard[i] = letter

        if positions:
            return GuessResult(status="correct", positions=positions, complete=self.is_complete(), game_over=self.is_game_over())
        else:
            self.wrong_guesses += 1
            return GuessResult(status="wrong", positions=[], complete=self.is_complete(), game_over=self.is_game_over())

    def reset(self) -> None:
        self.category, self.word = pick_word(self.difficulty)
        self.gameboard = ["_"] * len(self.word)
        self.guessed_letters.clear()
        self.wrong_guesses = 0
