from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from backend.utils.rich_readchar.readchar_support import read_key, is_back, is_enter, is_left, is_quit, is_right, is_space
from backend.config.registry import REGISTRY, DATAFLOW_REGISTRY


@dataclass(frozen=True)
class _MenuItem:
    label: str
    value: str
    enabled: bool = True


def _move_index(items: List[_MenuItem], idx: int, delta: int) -> int:
    if not items:
        return 0
    n = len(items)
    for _ in range(n):
        idx = (idx + delta) % n
        if items[idx].enabled:
            return idx
    return idx


def _render_hmenu(items: List[_MenuItem], idx: int, *, selected_values: Optional[Set[str]] = None, show_checks: bool = False) -> RenderableType:
    selected_values = selected_values or set()
    t = Text()
    for i, it in enumerate(items):
        is_cursor = i == idx
        is_enabled = it.enabled
        is_checked = it.value in selected_values

        prefix = ""
        if show_checks:
            prefix = "[x] " if is_checked else "[ ] "

        label = prefix + it.label
        if not is_enabled:
            style = "grey50"
            if is_cursor:
                style = "black on grey50"
        else:
            style = "white"
            if is_cursor:
                style = "black on #f266e0"

        t.append(label, style=style)
        if i < len(items) - 1:
            t.append(" | ", style="grey62")
    return Align.center(t)


def _panel(title: str, body: RenderableType, help_text: str) -> Panel:
    help_line = Align.center(Text(help_text, style="grey70"))
    return Panel(Group(body, Text(""), help_line), title=title, border_style="grey37")


def _enabled_values(items: List[_MenuItem]) -> Set[str]:
    return {it.value for it in items if it.enabled}


def _enabled_non_all_values(items: List[_MenuItem]) -> Set[str]:
    return {it.value for it in items if it.enabled and it.value != "all"}


def _apply_all_semantics(selected: Set[str], items: List[_MenuItem]) -> Set[str]:
    sel = set(selected)
    non_all = _enabled_non_all_values(items)

    if "all" in sel:
        sel |= non_all
    else:
        if non_all and non_all.issubset(sel):
            sel.add("all")
        else:
            sel.discard("all")

    sel &= _enabled_values(items)
    return sel


def _plan_header(plan: List[Tuple[str, str, Optional[List[type]]]]) -> Panel:
    lines = Text()
    lines.append("Selected:\n", style="bold")

    if not plan:
        lines.append("(none)", style="white")
        return Panel(lines, title="Run Plan", border_style="grey37")

    for kind, key, classes_override in plan:
        if classes_override is None:
            lines.append(f"- {kind} → {key}: ALL\n", style="white")
        else:
            if not classes_override:
                lines.append(f"- {kind} → {key}: (none)\n", style="white")
            else:
                names = ", ".join(cls.__name__ for cls in classes_override)
                lines.append(f"- {kind} → {key}: {names}\n", style="white")

    return Panel(lines, title="Run Plan", border_style="grey37")


def _select_mode_and_groups(console: Console) -> Tuple[str, Set[str]]:
    top = [_MenuItem("All", "all"), _MenuItem("Scrape", "scrape"), _MenuItem("Dataflow", "dataflow")]
    groups_all_or_scrape = [_MenuItem("All", "all"), _MenuItem("Soons", "Soons"), _MenuItem("Theques", "Theques"), _MenuItem("Showtimes", "Showtimes")]
    groups_dataflow = [_MenuItem("All", "all"), _MenuItem("Soons", "Soons"), _MenuItem("Theques", "Theques", enabled=False), _MenuItem("Showtimes", "Showtimes")]

    stage: str = "top"
    idx: int = 0
    mode: str = "all"
    selected_groups: Set[str] = set()

    def default_select_all(items: List[_MenuItem]) -> Set[str]:
        return _apply_all_semantics({"all"}, items)

    def current_items() -> List[_MenuItem]:
        if stage == "groups_dataflow":
            return groups_dataflow
        return groups_all_or_scrape

    def render() -> Panel:
        if stage == "top":
            body = Group(Text("Run:", style="bold"), _render_hmenu(top, idx))
            return _panel("Select Mode", body, "←/→ move   Enter select   Backspace/Esc back   q quit")

        items = current_items()
        title = "All" if mode == "all" else ("Scrape" if mode == "scrape" else "Dataflow")
        body = Group(Text(f"[{title}]", style="bold"), _render_hmenu(items, idx, selected_values=selected_groups, show_checks=True))
        return _panel("Select Groups", body, "←/→ move   Space toggle   Enter done   Backspace/Esc back   q quit")

    with Live(render(), console=console, refresh_per_second=30) as live:
        while True:
            live.update(render())
            k = read_key()

            if is_quit(k):
                raise KeyboardInterrupt

            if is_back(k):
                if stage != "top":
                    stage = "top"
                    idx = 0
                continue

            if stage == "top":
                if is_left(k):
                    idx = _move_index(top, idx, -1)
                elif is_right(k):
                    idx = _move_index(top, idx, +1)
                elif is_enter(k):
                    mode = top[idx].value
                    idx = 0
                    if mode == "dataflow":
                        stage = "groups_dataflow"
                        selected_groups = default_select_all(groups_dataflow)
                    else:
                        stage = "groups_all"
                        selected_groups = default_select_all(groups_all_or_scrape)
                continue

            items = current_items()
            if is_left(k):
                idx = _move_index(items, idx, -1)
                continue
            if is_right(k):
                idx = _move_index(items, idx, +1)
                continue

            if is_space(k):
                it = items[idx]
                if not it.enabled:
                    continue

                sel = set(selected_groups)
                if it.value == "all":
                    if "all" in sel:
                        sel.discard("all")
                    else:
                        sel.add("all")
                    selected_groups = _apply_all_semantics(sel, items)
                else:
                    if it.value in sel:
                        sel.remove(it.value)
                    else:
                        sel.add(it.value)
                    selected_groups = _apply_all_semantics(sel, items)
                continue

            if is_enter(k):
                out = set(selected_groups)
                out.discard("all")
                return mode, out


def _select_registry_items(console: Console, title: str, classes: List[type]) -> Tuple[Optional[List[type]], bool]:
    menu_items: List[_MenuItem] = [_MenuItem("All", "all")]
    by_value: Dict[str, type] = {}
    for cls in classes:
        v = cls.__name__
        by_value[v] = cls
        menu_items.append(_MenuItem(v, v))

    idx = 0
    selected: Set[str] = set()  # DEFAULT EMPTY

    def render() -> Panel:
        body = Group(
            Text(title, style="bold"),
            _render_hmenu(menu_items, idx, selected_values=selected, show_checks=True),
        )
        return _panel("Select Items", body, "←/→ move   Space toggle   Enter done   Backspace/Esc back   q quit")

    with Live(render(), console=console, refresh_per_second=30) as live:
        while True:
            live.update(render())
            k = read_key()

            if is_quit(k):
                raise KeyboardInterrupt

            if is_back(k):
                return None, True

            if is_left(k):
                idx = _move_index(menu_items, idx, -1)
                continue
            if is_right(k):
                idx = _move_index(menu_items, idx, +1)
                continue

            if is_space(k):
                it = menu_items[idx]
                sel = set(selected)

                if it.value == "all":
                    if "all" in sel:
                        sel.discard("all")
                    else:
                        sel.add("all")
                    selected = _apply_all_semantics(sel, menu_items)
                else:
                    if it.value in sel:
                        sel.remove(it.value)
                    else:
                        sel.add(it.value)
                    selected = _apply_all_semantics(sel, menu_items)
                continue

            if is_enter(k):
                sel = set(selected)
                if "all" in sel:
                    return list(classes), False
                sel.discard("all")
                picked = [by_value[it.value] for it in menu_items if it.value in sel and it.value in by_value]
                return picked, False


def choose_run_plan() -> Tuple[List[Tuple], Panel]:
    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))

    SCRAPE_KEY_BY_GROUP = {"Soons": "testingSoons", "Theques": "testingTheques", "Showtimes": "testingShowtimes"}
    DATAFLOW_KEY_BY_GROUP = {"Soons": "comingSoonsData", "Showtimes": "nowPlayingData"}

    ORDER = ["Soons", "Showtimes", "Theques"]

    while True:
        mode, groups = _select_mode_and_groups(console)

        if not groups:
            plan: List[Tuple[str, str, Optional[List[type]]]] = []
            return plan, _plan_header(plan)

        if len(groups) == 1:
            group = next(iter(groups))
            plan: List[Tuple[str, str, Optional[List[type]]]] = []

            if mode in ("all", "scrape"):
                scrape_key = SCRAPE_KEY_BY_GROUP.get(group)
                if scrape_key:
                    scrape_classes = list(REGISTRY.get(scrape_key, []))
                    picked, backed = _select_registry_items(console, f"Scrape → {group}", scrape_classes)
                    if backed:
                        continue
                    if picked:
                        plan.append(("cinema", scrape_key, picked))

            if mode in ("all", "dataflow"):
                df_key = DATAFLOW_KEY_BY_GROUP.get(group)
                if df_key:
                    df_classes = list(DATAFLOW_REGISTRY.get(df_key, []))
                    picked, backed = _select_registry_items(console, f"Dataflow → {group}", df_classes)
                    if backed:
                        continue
                    if picked:
                        plan.append(("dataflow", df_key, picked))

            return plan, _plan_header(plan)

        plan2: List[Tuple[str, str, Optional[List[type]]]] = []

        scrape_groups = set(groups) if mode in ("all", "scrape") else set()
        dataflow_groups = (set(groups) & {"Soons", "Showtimes"}) if mode in ("all", "dataflow") else set()

        for g in ORDER:
            if g in scrape_groups:
                plan2.append(("cinema", SCRAPE_KEY_BY_GROUP[g], None))
            if g in dataflow_groups:
                plan2.append(("dataflow", DATAFLOW_KEY_BY_GROUP[g], None))

        return plan2, _plan_header(plan2)
