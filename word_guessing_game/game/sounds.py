from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None  # type: ignore


class SoundManager:
    def __init__(self, sounds_dir: Path) -> None:
        self.sounds_dir = sounds_dir
        self.enabled = False
        self.correct = None
        self.wrong = None
        self.win = None
        self.game_over = None

        if pygame is None:
            print("Pygame not available; audio disabled.")
            return

        try:
            pygame.mixer.init()
            self.enabled = True
        except Exception as e:  # pragma: no cover
            print(f"Audio init failed; audio disabled. Error: {e}")
            self.enabled = False

        self.correct = self._load("correct_guess.wav")
        self.wrong = self._load("wrong_guess.wav")
        self.win = self._load("win_sound.mp3")
        self.game_over = self._load("game_over.wav")

    def _load(self, filename: str):
        if not self.enabled:
            return None
        path = self.sounds_dir / filename
        if not path.exists():
            print(f"Sound not found: {path}")
            return None
        try:
            return pygame.mixer.Sound(str(path))  # type: ignore[attr-defined]
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            return None

    def play_correct(self) -> None:
        if self.correct:
            self.correct.play()

    def play_wrong(self) -> None:
        if self.wrong:
            self.wrong.play()

    def play_win(self) -> None:
        if self.win:
            self.win.play()

    def play_game_over(self) -> None:
        if self.game_over:
            self.game_over.play()
