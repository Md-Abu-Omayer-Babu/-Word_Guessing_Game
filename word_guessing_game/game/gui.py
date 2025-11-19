from __future__ import annotations

import string
from pathlib import Path
from typing import Dict, List, Optional

import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

from .data import (
    ALPHABET,
    BACKGROUNDS_DIR,
    BUTTONS_DIR,
    HANGMAN_DIR,
    HANGMAN_IMAGE_FILENAMES,
    SOUNDS_DIR,
    initial_hangman_index,
)
from .game_logic import GameLogic
from .sounds import SoundManager


def _load_image(path: Path, size: Optional[tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
    if not path.exists():
        return None
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def _placeholder(size: tuple[int, int], text: str) -> ImageTk.PhotoImage:
    img = Image.new("RGB", size, color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    w, h = d.textbbox((0, 0), text, font=font)[2:]
    d.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(200, 200, 200), font=font)
    return ImageTk.PhotoImage(img)


class GameGUI:
    def __init__(self) -> None:
        self.selected_difficulty: Optional[str] = None
        self.difficulty_root: Optional[tk.Tk] = None
        self.game_root: Optional[tk.Tk] = None

        self.sound_manager = SoundManager(SOUNDS_DIR)

        # Game window state
        self.logic: Optional[GameLogic] = None
        self.hangman_images: List[Path] = [HANGMAN_DIR / f for f in HANGMAN_IMAGE_FILENAMES]
        self.hangman_index: int = 0
        self.hangman_label: Optional[tk.Label] = None
        self.board_label: Optional[tk.Label] = None
        self.guesses_label: Optional[tk.Label] = None
        self.lives_label: Optional[tk.Label] = None
        self.buttons: Dict[str, tk.Button] = {}

    def start(self) -> None:
        self._show_difficulty_window()

    # Difficulty window
    def _show_difficulty_window(self) -> None:
        self.difficulty_root = tk.Tk()
        self.difficulty_root.title("Word Guessing Game")
        self.difficulty_root.geometry("950x630")

        bg = _load_image(BACKGROUNDS_DIR / "background_image.png")
        if bg:
            label = tk.Label(self.difficulty_root, image=bg)
            label.image = bg
            label.place(relwidth=1, relheight=1)

        x_position = 530
        y_beginner = 250
        y_intermediate = 320
        y_advanced = 390

        beginner_img = _load_image(BUTTONS_DIR / "beginner_image.png")
        intermediate_img = _load_image(BUTTONS_DIR / "intermediate_image.png")
        advanced_img = _load_image(BUTTONS_DIR / "advanced_image.png")
        play_img = _load_image(BUTTONS_DIR / "play_image.png")

        beginner_btn = ttk.Button(
            self.difficulty_root,
            command=lambda: self._set_selected_difficulty("Beginner"),
            image=beginner_img,
            compound=tk.LEFT,
        )
        beginner_btn.image = beginner_img
        intermediate_btn = ttk.Button(
            self.difficulty_root,
            command=lambda: self._set_selected_difficulty("Intermediate"),
            image=intermediate_img,
            compound=tk.LEFT,
        )
        intermediate_btn.image = intermediate_img
        advanced_btn = ttk.Button(
            self.difficulty_root,
            command=lambda: self._set_selected_difficulty("Advanced"),
            image=advanced_img,
            compound=tk.LEFT,
        )
        advanced_btn.image = advanced_img

        beginner_btn.place(x=x_position, y=y_beginner)
        intermediate_btn.place(x=x_position, y=y_intermediate)
        advanced_btn.place(x=x_position, y=y_advanced)

        play_btn = ttk.Button(
            self.difficulty_root,
            command=self._start_game,
            image=play_img,
            compound=tk.LEFT,
        )
        play_btn.image = play_img
        play_btn.place(x=525, y=y_advanced + 70)

        self.difficulty_root.mainloop()

    def _set_selected_difficulty(self, difficulty: str) -> None:
        self.selected_difficulty = difficulty

    # Game window
    def _start_game(self) -> None:
        if not self.selected_difficulty:
            messagebox.showinfo("Select Difficulty", "Please select a difficulty first.")
            return

        if self.difficulty_root:
            self.difficulty_root.destroy()
            self.difficulty_root = None

        self._show_game_window(self.selected_difficulty)

    def _show_game_window(self, difficulty: str) -> None:
        self.game_root = tk.Tk()
        self.game_root.title("Word Guessing Game")
        self.game_root.geometry("950x630")
        self.game_root.resizable(True, True)

        bg = _load_image(BACKGROUNDS_DIR / "background_image.png")
        if bg:
            label = tk.Label(self.game_root, image=bg)
            label.image = bg
            label.place(x=0, y=0, relwidth=1, relheight=1)

        self.logic = GameLogic(difficulty)

        hint = tk.Label(self.game_root, text=self.logic.hint_text, font=("Verdana", 12, "bold"))
        hint.pack(side="top")

        # Hangman image
        self.hangman_index = initial_hangman_index(len(self.logic.word))
        img = self._current_hangman_photo()
        self.hangman_label = tk.Label(self.game_root, image=img)
        self.hangman_label.image = img
        self.hangman_label.pack(pady=(5, 5))

        # Board + meta
        # Match legacy: board label displays the raw list representation
        self.board_label = tk.Label(self.game_root, text=self._legacy_board_text(), font=("Verdana", 30, "bold"))
        self.board_label.pack(side="top")

        # Match legacy: guesses shown as a Python list-like string with 'Guesses:' prefix
        self.guesses_label = tk.Label(self.game_root, text=self._legacy_guesses_text(), font=("Verdana", 10, "bold"))
        self.guesses_label.place(x=100, y=300)

        # Match legacy: lives shown as ['Lives(5):', 'x', ...]
        self.lives_label = tk.Label(self.game_root, text=self._legacy_lives_text(), font=("Verdana", 10, "bold"))
        self.lives_label.place(x=100, y=330)

        # Alphabet buttons grid similar to original layout
        self.buttons = {}
        self._populate_alpha_buttons()

        self.game_root.mainloop()

    def _current_hangman_photo(self) -> ImageTk.PhotoImage:
        size = (600, 250)
        if 0 <= self.hangman_index < len(self.hangman_images):
            img = _load_image(self.hangman_images[self.hangman_index], size=size)
            if img is not None:
                return img
        return _placeholder(size, "Hangman")

    def _advance_hangman(self) -> None:
        if self.hangman_index < len(self.hangman_images) - 1:
            self.hangman_index += 1
            if self.hangman_label:
                img = self._current_hangman_photo()
                self.hangman_label.configure(image=img)
                self.hangman_label.image = img

    def _populate_alpha_buttons(self) -> None:
        # Layout: 5 rows up to 26 letters, like original placements
        xpos = 150
        ypos = 370
        col_w = 100
        row_h = 50
        per_row = 6

        row_breaks = {6, 12, 18, 24}
        c = 0
        for letter in ALPHABET:
            if c in row_breaks:
                ypos += 50
                xpos = 150
            btn = tk.Button(
                self.game_root,
                text=letter.upper(),
                # Match legacy font used in original code
                font=("Pacifico", 16),
                command=lambda l=letter: self._on_letter(l),
            )
            btn.place(height=50, width=100, x=xpos, y=ypos)
            self.buttons[letter] = btn
            xpos += col_w
            c += 1

    def _on_letter(self, letter: str) -> None:
        if not self.logic:
            return
        btn = self.buttons.get(letter)
        if btn:
            btn.configure(state=tk.DISABLED)

        result = self.logic.guess(letter)

        # Update UI texts (legacy-style formatting)
        self.board_label.configure(text=self._legacy_board_text())
        self.guesses_label.configure(text=self._legacy_guesses_text())
        self.lives_label.configure(text=self._legacy_lives_text())

        # Sounds + image animation
        if result.status == "correct":
            self.sound_manager.play_correct()
            self._advance_hangman()
        elif result.status == "wrong":
            self.sound_manager.play_wrong()

        # End state checks
        if result.complete:
            self.sound_manager.play_win()
            again = messagebox.askyesno("Congrats!", "You won! Play again?")
            self._handle_restart(again)
            return
        if result.game_over:
            self.sound_manager.play_game_over()
            answer = getattr(self.logic, 'word', '')
            again = messagebox.askyesno("GAME OVER!", f"GAME OVER: Thanks for playing!\nAnswer:\t{answer}\nPlay again?")
            self._handle_restart(again)
            return

    def _handle_restart(self, again: bool) -> None:
        if self.game_root:
            self.game_root.destroy()
            self.game_root = None
        if again:
            # Reset selected difficulty to allow a fresh pick, or reuse last
            self.selected_difficulty = None
            self._show_difficulty_window()
        else:
            # Exit application
            pass

    # Helpers to mimic legacy label text style
    def _legacy_board_text(self) -> str:
        # Legacy showed the raw Python list of underscores
        if not self.logic:
            return "[]"
        return str(self.logic.gameboard)

    def _legacy_guesses_text(self) -> str:
        if not self.logic:
            return "['Guesses:']"
        items = ['Guesses:'] + sorted(self.logic.guessed_letters)
        return str(items)

    def _legacy_lives_text(self) -> str:
        if not self.logic:
            return "['Lives(5):']"
        xs = ['x'] * self.logic.wrong_guesses
        return str([f"Lives({self.logic.max_wrong}):"] + xs)
