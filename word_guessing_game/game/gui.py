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


def _load_image(path: Path, size: Optional[tuple[int, int]] = None, master: Optional[tk.Misc] = None) -> Optional[ImageTk.PhotoImage]:
    if not path.exists():
        return None
    try:
        with Image.open(path) as im:
            img = im.copy()
        if size:
            img = img.resize(size)
        return ImageTk.PhotoImage(img, master=master)
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

        # Base design size for responsive scaling
        self.BASE_W: int = 950
        self.BASE_H: int = 630

        # Difficulty window assets and widgets for responsive layout
        self._diff_bg_path: Optional[Path] = None
        self._diff_bg_label: Optional[tk.Label] = None
        self._diff_btn_paths: Dict[str, Path] = {}
        self._diff_btn_sizes: Dict[str, tuple[int, int]] = {}
        self._diff_btn_widgets: Dict[str, ttk.Button] = {}
        self._diff_layout_job: Optional[str] = None
        self._game_layout_job: Optional[str] = None

    def start(self) -> None:
        self._show_difficulty_window()

    # Difficulty window
    def _show_difficulty_window(self) -> None:
        self.difficulty_root = tk.Tk()
        self.difficulty_root.title("Word Guessing Game")
        self.difficulty_root.geometry("850x630")

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
        self.game_root.geometry(f"{self.BASE_W}x{self.BASE_H}")
        self.game_root.resizable(True, True)

        # Background
        self._game_bg_path: Path = BACKGROUNDS_DIR / "background_image.png"
        bg = _load_image(self._game_bg_path, master=self.game_root)
        if bg:
            self._game_bg_label = tk.Label(self.game_root, image=bg)
            self._game_bg_label.image = bg
            self._game_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.logic = GameLogic(difficulty)

        self.hint_label = tk.Label(self.game_root, text=self.logic.hint_text, font=("Verdana", 12, "bold"))
        self.hint_label.pack(side="top")

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

        # Initial responsive layout and bindings
        self._layout_game_window()
        self.game_root.bind("<Configure>", self._on_game_configure)

        self.game_root.mainloop()

    def _current_hangman_photo(self) -> ImageTk.PhotoImage:
        # Scale hangman image relative to window size
        size = (600, 250)
        if self.game_root:
            try:
                w = max(self.game_root.winfo_width(), 1)
                h = max(self.game_root.winfo_height(), 1)
                s = min(w / self.BASE_W, h / self.BASE_H)
                size = (max(200, int(600 * s)), max(120, int(250 * s)))
            except Exception:
                pass
        if 0 <= self.hangman_index < len(self.hangman_images):
            img = _load_image(self.hangman_images[self.hangman_index], size=size, master=self.game_root)
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
        self._alpha_base = {
            "x0": 150,
            "y0": 370,
            "col_w": 100,
            "row_h": 50,
            "btn_w": 100,
            "btn_h": 50,
            "per_row": 6,
        }

        row_breaks = {6, 12, 18, 24}
        c = 0
        for letter in ALPHABET:
            btn = tk.Button(
                self.game_root,
                text=letter.upper(),
                font=("Pacifico", 16),
                command=lambda l=letter: self._on_letter(l),
            )
            # Initially place at base; will be repositioned on resize
            btn.place(height=self._alpha_base["btn_h"], width=self._alpha_base["btn_w"], x=self._alpha_base["x0"], y=self._alpha_base["y0"]) 
            self.buttons[letter] = btn
            c += 1

        # Perform an initial layout pass
        self._layout_alpha_buttons()

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

    # Responsive layout helpers
    def _scale_factor(self, root: tk.Tk) -> float:
        try:
            w = max(root.winfo_width(), 1)
            h = max(root.winfo_height(), 1)
            return max(0.5, min(w / self.BASE_W, h / self.BASE_H))
        except Exception:
            return 1.0

    def _layout_difficulty_window(self) -> None:
        if not self.difficulty_root:
            return
        s = self._scale_factor(self.difficulty_root)

        # Background fit to window
        if self._diff_bg_label and self._diff_bg_path and self.difficulty_root:
            try:
                w = max(self.difficulty_root.winfo_width(), 1)
                h = max(self.difficulty_root.winfo_height(), 1)
                tkimg = _load_image(self._diff_bg_path, (w, h), master=self.difficulty_root)
                if tkimg:
                    self._diff_bg_label.configure(image=tkimg)
                    self._diff_bg_label.image = tkimg
            except Exception:
                pass

        # Centered vertical stack layout
        w = max(self.difficulty_root.winfo_width(), 1)
        h = max(self.difficulty_root.winfo_height(), 1)

        order = ["beginner", "intermediate", "advanced", "play"]
        gap = max(10, int(70 * s))

        # Compute scaled sizes and total height
        scaled: dict[str, tuple[int, int]] = {}
        total_h = 0
        for key in order:
            size = self._diff_btn_sizes.get(key, (200, 60))
            bw = max(120, int(size[0] * s))
            bh = max(44, int(size[1] * s))
            scaled[key] = (bw, bh)
            total_h += bh
        total_h += gap * (len(order) - 1)

        top_y = max(20, (h - total_h) // 2)

        # Place centered
        y = top_y
        for key in order:
            btn = self._diff_btn_widgets.get(key)
            if not btn:
                continue
            bw, bh = scaled[key]
            x = max(0, (w - bw) // 2)
            # Scale image each time to stay crisp
            path = self._diff_btn_paths.get(key)
            if path and path.exists():
                try:
                    img = _load_image(path, (bw, bh), master=self.difficulty_root)
                    if img:
                        btn.configure(image=img)
                        btn.image = img
                except Exception:
                    pass
            btn.place(x=x, y=y, width=bw, height=bh)
            y += bh + gap

    def _layout_alpha_buttons(self) -> None:
        if not self.game_root:
            return
        s = self._scale_factor(self.game_root)
        x0 = int(self._alpha_base["x0"] * s)
        y0 = int(self._alpha_base["y0"] * s)
        col_w = int(self._alpha_base["col_w"] * s)
        row_h = int(self._alpha_base["row_h"] * s)
        bw = max(50, int(self._alpha_base["btn_w"] * s))
        bh = max(30, int(self._alpha_base["btn_h"] * s))

        # Place in rows of per_row
        per_row = self._alpha_base["per_row"]
        c = 0
        row = 0
        col = 0
        for letter in ALPHABET:
            btn = self.buttons.get(letter)
            if not btn:
                continue
            if c and c % per_row == 0:
                row += 1
                col = 0
            x = x0 + col * col_w
            y = y0 + row * row_h
            btn.place(x=x, y=y, width=bw, height=bh)
            try:
                btn.configure(font=("Pacifico", max(10, int(16 * s))))
            except Exception:
                pass
            col += 1
            c += 1

    def _layout_game_window(self) -> None:
        if not self.game_root:
            return
        s = self._scale_factor(self.game_root)

        # Background resize
        try:
            w = max(self.game_root.winfo_width(), 1)
            h = max(self.game_root.winfo_height(), 1)
            if hasattr(self, "_game_bg_label") and self._game_bg_label is not None:
                tkimg = _load_image(self._game_bg_path, (w, h), master=self.game_root)
                if tkimg:
                    self._game_bg_label.configure(image=tkimg)
                    self._game_bg_label.image = tkimg
        except Exception:
            pass

        # Scale fonts
        try:
            self.hint_label.configure(font=("Verdana", max(8, int(12 * s)), "bold"))
            self.board_label.configure(font=("Verdana", max(16, int(30 * s)), "bold"))
            self.guesses_label.configure(font=("Verdana", max(8, int(10 * s)), "bold"))
            self.lives_label.configure(font=("Verdana", max(8, int(10 * s)), "bold"))
        except Exception:
            pass

        # Reposition meta labels (keep relative to base)
        gx = int(100 * s)
        gy = int(300 * s)
        lx = int(100 * s)
        ly = int(330 * s)
        self.guesses_label.place(x=gx, y=gy)
        self.lives_label.place(x=lx, y=ly)

        # Resize hangman image
        if self.hangman_label:
            img = self._current_hangman_photo()
            self.hangman_label.configure(image=img)
            self.hangman_label.image = img

        # Layout alphabet
        self._layout_alpha_buttons()

    # Debounced configure handlers
    def _on_diff_configure(self, event) -> None:
        if not self.difficulty_root:
            return
        if self._diff_layout_job:
            try:
                self.difficulty_root.after_cancel(self._diff_layout_job)
            except Exception:
                pass
        self._diff_layout_job = self.difficulty_root.after(60, self._layout_difficulty_window)

    def _on_game_configure(self, event) -> None:
        if not self.game_root:
            return
        if self._game_layout_job:
            try:
                self.game_root.after_cancel(self._game_layout_job)
            except Exception:
                pass
        self._game_layout_job = self.game_root.after(60, self._layout_game_window)

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
