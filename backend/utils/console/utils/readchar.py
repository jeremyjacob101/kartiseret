from __future__ import annotations

from dataclasses import dataclass

from readchar import key as rkey
import readchar


@dataclass(frozen=True)
class Keys:
    LEFT: str = rkey.LEFT
    RIGHT: str = rkey.RIGHT
    UP: str = rkey.UP
    DOWN: str = rkey.DOWN
    ENTER: str = rkey.ENTER
    SPACE: str = rkey.SPACE
    BACKSPACE: str = getattr(rkey, "BACKSPACE", "\x7f")
    ESC: str = getattr(rkey, "ESC", "\x1b")
    CTRL_C: str = rkey.CTRL_C


def read_key() -> str:
    return readchar.readkey()


def is_left(k: str) -> bool:
    return k == Keys.LEFT


def is_right(k: str) -> bool:
    return k == Keys.RIGHT


def is_enter(k: str) -> bool:
    return k == Keys.ENTER or k == "\r" or k == "\n"


def is_space(k: str) -> bool:
    return k == Keys.SPACE or k == " "


def is_back(k: str) -> bool:
    return k in (Keys.BACKSPACE, Keys.ESC)


def is_quit(k: str) -> bool:
    return k in (Keys.CTRL_C, "q", "Q")
