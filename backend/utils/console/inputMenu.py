from typing import Dict, List, Optional, Set, Tuple
from __future__ import annotations
from dataclasses import dataclass

from rich.console import Console, Group, RenderableType
from rich.align import Align
from rich.panel import Panel
from rich.theme import Theme
from rich.live import Live
from rich.text import Text

from backend.utils.console.utils.readchar import read_key, is_back, is_enter, is_left, is_quit, is_right, is_space
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
    all_selected = show_checks and _is_all_selected(selected_values, items)

    t = Text()
    for i, it in enumerate(items):
        is_cursor = i == idx
        is_enabled = it.enabled
        is_checked = (it.value in selected_values) if it.value != "all" else all_selected

        # No checkbox for All
        prefix = ""
        if show_checks and it.value != "all":
            prefix = "[x] " if is_checked else "[ ] "

        label = prefix + it.label

        # Base style
        if not is_enabled:
            style = "grey50"
        else:
            style = "white"

        # If All is active, make it obvious (no checkbox)
        if show_checks and it.value == "all" and is_checked and is_enabled:
            style = "bold green"

        # Cursor override
        if is_cursor:
            style = "bold black on grey50" if not is_enabled else "bold black on #8040e6"

        t.append(label, style=style)
        if i < len(items) - 1:
            t.append(" | ", style="grey62")

    return Align.center(t)


def _panel(title: str, body: RenderableType) -> Panel:
    return Panel(Group(Text(""), body, Text("")), title=title, title_align="center", border_style="grey37")


def _enabled_non_all(items: List[_MenuItem]) -> List[_MenuItem]:
    return [it for it in items if it.enabled and it.value != "all"]


def _enabled_non_all_values(items: List[_MenuItem]) -> Set[str]:
    return {it.value for it in _enabled_non_all(items)}


def _is_all_selected(selected: Set[str], items: List[_MenuItem]) -> bool:
    non_all = _enabled_non_all_values(items)
    return bool(non_all) and non_all.issubset(selected)


def _toggle_all(selected: Set[str], items: List[_MenuItem]) -> Set[str]:
    # Toggle between select-all and clear-all
    if _is_all_selected(selected, items):
        return set()
    return set(_enabled_non_all_values(items))


def _normalize_selected(selected: Set[str], items: List[_MenuItem]) -> Set[str]:
    # Keep only enabled non-all values (never keep "all" in the set)
    allowed = _enabled_non_all_values(items)
    return set(selected) & allowed


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
    top = [_MenuItem("Everything", "everything"), _MenuItem("All", "all"), _MenuItem("Scrape", "scrape"), _MenuItem("Dataflow", "dataflow")]
    groups_all_or_scrape = [_MenuItem("All", "all"), _MenuItem("Soons", "Soons"), _MenuItem("Theques", "Theques"), _MenuItem("Showtimes", "Showtimes")]
    groups_dataflow = [_MenuItem("All", "all"), _MenuItem("Soons", "Soons"), _MenuItem("Theques", "Theques", enabled=False), _MenuItem("Showtimes", "Showtimes")]

    stage: str = "top"
    idx: int = 0
    mode: str = "all"
    selected_groups = set()  # DEFAULT EMPTY

    def current_items() -> List[_MenuItem]:
        if stage == "groups_dataflow":
            return groups_dataflow
        return groups_all_or_scrape

    def render() -> Panel:
        if stage == "top":
            body = _render_hmenu(top, idx)
            return _panel("Select Mode", body)

        items = current_items()
        title = "All" if mode == "all" else ("Scrape" if mode == "scrape" else "Dataflow")
        body = _render_hmenu(items, idx, selected_values=selected_groups, show_checks=True)
        return _panel(title, body)

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
                    if mode == "everything":
                        return "everything", set()

                    idx, selected_groups = 0, set()
                    if mode == "dataflow":
                        stage = "groups_dataflow"
                    else:
                        stage = "groups_all"
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
                    selected_groups = _toggle_all(sel, items)
                else:
                    if it.value in sel:
                        sel.remove(it.value)
                    else:
                        sel.add(it.value)
                    selected_groups = _normalize_selected(sel, items)

                continue

            if is_enter(k):
                hovered = items[idx]
                if hovered.value == "all":
                    return mode, set(_enabled_non_all_values(items))
                return mode, set(selected_groups)


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
        body = _render_hmenu(menu_items, idx, selected_values=selected, show_checks=True)
        return _panel(title, body)

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
                if not it.enabled:
                    continue

                sel = set(selected)

                if it.value == "all":
                    selected = _toggle_all(sel, menu_items)
                else:
                    if it.value in sel:
                        sel.remove(it.value)
                    else:
                        sel.add(it.value)
                    selected = _normalize_selected(sel, menu_items)

                continue

            if is_enter(k):
                hovered = menu_items[idx]
                if hovered.value == "all":
                    return list(classes), False

                if _is_all_selected(selected, menu_items):
                    return list(classes), False

                picked = [by_value[it.value] for it in menu_items if it.value in selected and it.value in by_value]
                return picked, False


def choose_run_plan() -> Tuple[List[Tuple], Panel]:
    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))

    SCRAPE_KEY_BY_GROUP = {"Soons": "testingSoons", "Theques": "testingTheques", "Showtimes": "testingShowtimes"}
    DATAFLOW_KEY_BY_GROUP = {"Soons": "comingSoonsData", "Showtimes": "nowPlayingData"}
    ORDER = ["Soons", "Showtimes", "Theques"]

    while True:
        mode, groups = _select_mode_and_groups(console)

        if mode == "everything":
            plan: List[Tuple[str, str, Optional[List[type]]]] = []

            for group in ["Soons", "Showtimes", "Theques"]:
                scrape_key = SCRAPE_KEY_BY_GROUP.get(group)
                if scrape_key:
                    plan.append(("cinema", scrape_key, list(REGISTRY.get(scrape_key, []))))

            for group in ["Soons", "Showtimes"]:
                df_key = DATAFLOW_KEY_BY_GROUP.get(group)
                if df_key:
                    plan.append(("dataflow", df_key, list(DATAFLOW_REGISTRY.get(df_key, []))))

            return plan, _plan_header(plan)

        if not groups:
            plan: List[Tuple[str, str, Optional[List[type]]]] = []
            return plan, _plan_header(plan)

        plan: List[Tuple[str, str, Optional[List[type]]]] = []

        def pick_for_group(kind: str, group: str, key_by_group: Dict[str, str], registry: Dict[str, List[type]], title_prefix: str) -> bool:
            key = key_by_group.get(group)
            if not key:
                return True

            classes = list(registry.get(key, []))
            picked, backed = _select_registry_items(console, f"{title_prefix} → {group}", classes)

            if backed:
                return False

            if picked:
                plan.append((kind, key, picked))

            return True

        for group in ORDER:
            if group not in groups:
                continue

            if mode in ("all", "scrape"):
                if not pick_for_group("cinema", group, SCRAPE_KEY_BY_GROUP, REGISTRY, "Scrape"):
                    plan = []
                    break

            if mode in ("all", "dataflow"):
                if not pick_for_group("dataflow", group, DATAFLOW_KEY_BY_GROUP, DATAFLOW_REGISTRY, "Dataflow"):
                    plan = []
                    break

        if not plan:
            if plan == []:
                continue

        return plan, _plan_header(plan)
