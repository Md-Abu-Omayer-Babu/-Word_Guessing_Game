# Word Guessing Game (Tkinter + Pygame)

A modular, maintainable refactor of a Hangman-style word guessing game using Tkinter for UI and Pygame for sounds.

## Project Structure

```
word_guessing_game/
│
├── assets/
│   ├── backgrounds/
│   ├── buttons/
│   ├── hangman_images/   # preferred
│   ├── mouse_images/     # legacy folder also supported
│   └── sounds/
│
├── game/
│   ├── __init__.py
│   ├── app.py              # Entry point
│   ├── gui.py              # Tkinter GUI logic
│   ├── game_logic.py       # Word guessing mechanics
│   ├── sounds.py           # Sound effects management
│   └── data.py             # Word lists, categories, constants
│
├── requirements.txt
└── README.md
```

## Features

- Difficulty selection (Beginner, Intermediate, Advanced)
- Category hint and first-letter hint
- 26 letter buttons with per-click disable
- Hangman image progression for correct guesses
- Sound effects for correct, wrong, win, and game over
- Replay prompt on win/lose
- Graceful fallbacks if assets or audio are missing

## Assets

Place your files here (filenames expected by default):

- Backgrounds: `assets/backgrounds/background_image.png`
- Buttons: `assets/buttons/beginner_image.png`, `intermediate_image.png`, `advanced_image.png`, `play_image.png`
- Hangman frames: preferred `assets/hangman_images/img0.png` ... `img51.png` (falls back to `assets/mouse_images/` if missing)
- Sounds: `assets/sounds/correct_guess.wav`, `wrong_guess.wav`, `win_sound.mp3`, `game_over.wav`

If an asset is missing, the game will still run using placeholders and muted sounds.

## Setup

Install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r ..\requirements.txt
```

## Run

From the repo root:

```powershell
python -m word_guessing_game
```

Or run the module directly:

```powershell
python word_guessing_game\game\app.py
```

## Extending

- Add words to `word_guessing_game/game/data.py` under `WORD_LISTS`.
- Change max wrong guesses via `MAX_WRONG_GUESSES` in `data.py`.
- Replace images and sounds by updating files in `assets/`.

## Notes

- UI matches the legacy look: list-style labels and button fonts/placements.
- Tkinter ships with Python. Pygame is required only for sounds; if it fails to initialize, the game runs without audio.
- Letter buttons use the `Pacifico` font; if it's not installed, Tk will use a fallback.
