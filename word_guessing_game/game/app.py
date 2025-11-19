from __future__ import annotations

from .gui import GameGUI


def run() -> None:
    app = GameGUI()
    app.start()


if __name__ == "__main__":
    run()
