from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List

# Base directories
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PACKAGE_ROOT / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
BUTTONS_DIR = ASSETS_DIR / "buttons"
# Support legacy folder name 'mouse_images' while preferring 'hangman_images'
_PREF_HANGMAN = ASSETS_DIR / "hangman_images"
_LEGACY_MOUSE = ASSETS_DIR / "mouse_images"
HANGMAN_DIR = _PREF_HANGMAN if _PREF_HANGMAN.exists() else _LEGACY_MOUSE
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Constants
ALPHABET: List[str] = [chr(c) for c in range(ord('a'), ord('z') + 1)]
MAX_WRONG_GUESSES: int = 5

# Hangman image sequence (52 frames, img0.png ... img51.png)
HANGMAN_IMAGE_FILENAMES: List[str] = [f"img{i}.png" for i in range(52)]

# Initial index mapping for first shown frame by word length
_INITIAL_INDEX_BY_WORD_LEN = {
    3: 3,
    4: 7,
    5: 12,
    6: 18,
    7: 25,
    8: 33,
    9: 43,
}


def initial_hangman_index(word_len: int) -> int:
    return _INITIAL_INDEX_BY_WORD_LEN.get(word_len, 0)


# Word lists by difficulty/category
WORD_LISTS: Dict[str, Dict[str, List[str]]] = {
    'Beginner': {
        'animals': ['tiger', 'zebra', 'koala', 'snake', 'goose', 'otter', 'raven', 'gazelle', 'skunk', 'whale', 'horse', 'sloth', 'crane', 'lemur', 'shark', 'frogs', 'sheep', 'zebra'],
        'fruits': ['mango', 'melon', 'grape', 'lemon', 'peach', 'grape', 'melon', 'grape', 'lemon'],
        'flowers': ['tulip', 'daisy', 'lupin', 'aster', 'lotus', 'violet', 'tulip', 'clove', 'daisy', 'rose', 'clove', 'daisy', 'tulip']
    },
    'Intermediate': {
        'animals': ['zebra', 'whale', 'panda', 'shark', 'tiger', 'horse', 'lemur', 'koala', 'otter', 'raven', 'skunk', 'frogs'],
        'fruits': ['peach', 'melon', 'mango', 'grape', 'lemon', 'apple', 'berry', 'grape', 'melon'],
        'flowers': ['tulip', 'rose', 'daisy', 'poppy', 'violet', 'tulip', 'daisy', 'poppy', 'violet']
    },
    'Advanced': {
        'animals': ['hippo', 'rhino', 'crocs', 'chimp', 'lemur', 'hyena', 'dingo', 'whale', 'shark'],
        'fruits': ['pomeg', 'persi', 'grape', 'mango', 'quinc', 'guava', 'dates', 'plant', 'lemon', 'lyche', 'apric', 'papay', 'mulbe', 'berry', 'prune', 'mango', 'grape'],
        'flowers': ['chrys', 'hydrn', 'anemo', 'camel', 'clemi', 'tulip', 'daisy', 'poppy', 'daffo', 'vibur', 'mimic', 'dahli']
    }
}


def pick_word(difficulty: str) -> tuple[str, str]:
    """Return (category, word) given a difficulty."""
    categories = list(WORD_LISTS[difficulty].keys())
    category = random.choice(categories)
    word = random.choice(WORD_LISTS[difficulty][category])
    return category, word
