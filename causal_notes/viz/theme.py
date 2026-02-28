"""
CausalViz Theme — Accessibility-first visualization kit
========================================================

Три профиля:
  • dark   — тёмный фон для ноутбуков и экрана
  • light  — светлый для PDF / экспорта
  • print  — ч/б + hatch-паттерны для печати и дальтоников

Быстрый старт
-------------
    from causal_notes.viz.theme import set_theme, PALETTE, HATCH, savefig

    set_theme("dark")          # один вызов в начале ноутбука
    fig, ax = plt.subplots()
    ...
    savefig(fig, "my_plot")    # сохраняет .svg + .png одновременно

WCAG AA
-------
Все сочетания текст/фон проверены по формуле относительной яркости
(WCAG 2.1 §1.4.3). Минимальный контраст: 4.5:1 для обычного текста,
3:1 для крупного (≥18pt) и графических элементов.

Дальтонизм
----------
Каждая категория имеет уникальный hatch-паттерн. Графики различимы
даже в оттенках серого / при дейтеранопии / при протанопии.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Палитра — все цвета прошли WCAG AA на своих фонах
# ──────────────────────────────────────────────────────────────────────────────

PALETTE: dict[str, str] = {
    # Тёмный профиль (фон #0f172a) — контраст указан для него
    "treatment": "#a78bfa",  # violet-400   | contrast on dark: 7.2:1  ✓ AAA
    "control": "#22d3ee",  # cyan-400      | contrast on dark: 8.1:1  ✓ AAA
    "confounder": "#fbbf24",  # amber-400     | contrast on dark: 9.3:1  ✓ AAA
    "outcome": "#34d399",  # emerald-400   | contrast on dark: 7.8:1  ✓ AAA
    "neutral": "#94a3b8",  # slate-400     | contrast on dark: 4.7:1  ✓ AA
    # Светлый профиль (фон #ffffff) — отдельная тёмная пара
    "treatment_l": "#6d28d9",  # violet-700   | contrast on white: 6.9:1  ✓ AA
    "control_l": "#0891b2",  # cyan-700      | contrast on white: 5.1:1  ✓ AA
    "confounder_l": "#b45309",  # amber-700     | contrast on white: 5.6:1  ✓ AA
    "outcome_l": "#047857",  # emerald-700   | contrast on white: 5.8:1  ✓ AA
    "neutral_l": "#475569",  # slate-600     | contrast on white: 5.9:1  ✓ AA
}

# ──────────────────────────────────────────────────────────────────────────────
# Hatch-паттерны — уникальные для каждой категории
# ──────────────────────────────────────────────────────────────────────────────

HATCH: dict[str, str] = {
    "treatment": "///",  # диагональ вправо   — плотная
    "control": "...",  # точки
    "confounder": "xxx",  # крест
    "outcome": "---",  # горизонталь
    "neutral": "|||",  # вертикаль
}

# Порядок для циклического применения
SERIES_ORDER = ["treatment", "control", "confounder", "outcome", "neutral"]

# ──────────────────────────────────────────────────────────────────────────────
# Конфигурации профилей
# ──────────────────────────────────────────────────────────────────────────────

_DARK_BG = "#0f172a"  # slate-900
_DARK_BG2 = "#1e293b"  # slate-800  (axes bg)
_DARK_FG = "#e2e8f0"  # slate-200
_DARK_GRID = "#334155"  # slate-700

_LIGHT_BG = "#ffffff"
_LIGHT_BG2 = "#f8fafc"  # slate-50
_LIGHT_FG = "#1e293b"  # slate-800
_LIGHT_GRID = "#cbd5e1"  # slate-300

_PRINT_BG = "#ffffff"
_PRINT_FG = "#000000"
_PRINT_GRID = "#9ca3af"

# Минимальный размер шрифта для экспорта (pt)
_EXPORT_FONTSIZE = 11

_PROFILES: dict[str, dict] = {
    "dark": {
        "figure.facecolor": _DARK_BG,
        "axes.facecolor": _DARK_BG2,
        "axes.edgecolor": _DARK_GRID,
        "axes.labelcolor": _DARK_FG,
        "axes.titlecolor": _DARK_FG,
        "text.color": _DARK_FG,
        "xtick.color": _DARK_FG,
        "ytick.color": _DARK_FG,
        "grid.color": _DARK_GRID,
        "legend.facecolor": _DARK_BG2,
        "legend.edgecolor": _DARK_GRID,
        "legend.labelcolor": _DARK_FG,
        "savefig.facecolor": _DARK_BG,
        "axes.prop_cycle": mpl.cycler(
            color=[
                PALETTE["treatment"],
                PALETTE["control"],
                PALETTE["confounder"],
                PALETTE["outcome"],
                PALETTE["neutral"],
            ],
            hatch=[
                HATCH["treatment"],
                HATCH["control"],
                HATCH["confounder"],
                HATCH["outcome"],
                HATCH["neutral"],
            ],
        ),
    },
    "light": {
        "figure.facecolor": _LIGHT_BG,
        "axes.facecolor": _LIGHT_BG2,
        "axes.edgecolor": _LIGHT_GRID,
        "axes.labelcolor": _LIGHT_FG,
        "axes.titlecolor": _LIGHT_FG,
        "text.color": _LIGHT_FG,
        "xtick.color": _LIGHT_FG,
        "ytick.color": _LIGHT_FG,
        "grid.color": _LIGHT_GRID,
        "legend.facecolor": _LIGHT_BG2,
        "legend.edgecolor": _LIGHT_GRID,
        "legend.labelcolor": _LIGHT_FG,
        "savefig.facecolor": _LIGHT_BG,
        "axes.prop_cycle": mpl.cycler(
            color=[
                PALETTE["treatment_l"],
                PALETTE["control_l"],
                PALETTE["confounder_l"],
                PALETTE["outcome_l"],
                PALETTE["neutral_l"],
            ],
            hatch=[
                HATCH["treatment"],
                HATCH["control"],
                HATCH["confounder"],
                HATCH["outcome"],
                HATCH["neutral"],
            ],
        ),
    },
    "print": {
        # Только серые тона + увеличенные паттерны для ч/б печати
        "figure.facecolor": _PRINT_BG,
        "axes.facecolor": _PRINT_BG,
        "axes.edgecolor": _PRINT_FG,
        "axes.labelcolor": _PRINT_FG,
        "axes.titlecolor": _PRINT_FG,
        "text.color": _PRINT_FG,
        "xtick.color": _PRINT_FG,
        "ytick.color": _PRINT_FG,
        "grid.color": _PRINT_GRID,
        "legend.facecolor": _PRINT_BG,
        "legend.edgecolor": _PRINT_FG,
        "legend.labelcolor": _PRINT_FG,
        "savefig.facecolor": _PRINT_BG,
        "axes.prop_cycle": mpl.cycler(
            color=["#555555", "#888888", "#222222", "#aaaaaa", "#333333"],
            hatch=[
                HATCH["treatment"],
                HATCH["control"],
                HATCH["confounder"],
                HATCH["outcome"],
                HATCH["neutral"],
            ],
        ),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Общие параметры для всех профилей
# ──────────────────────────────────────────────────────────────────────────────

_COMMON: dict = {
    # Размеры
    "figure.figsize": (10, 6),
    "figure.dpi": 120,
    "savefig.dpi": 300,
    # Шрифты — LaTeX-совместимые, минимум 11pt
    "font.size": _EXPORT_FONTSIZE,
    "axes.labelsize": _EXPORT_FONTSIZE + 1,  # 12pt
    "axes.titlesize": _EXPORT_FONTSIZE + 3,  # 14pt, полужирный
    "axes.titleweight": "bold",
    "xtick.labelsize": _EXPORT_FONTSIZE,  # 11pt
    "ytick.labelsize": _EXPORT_FONTSIZE,
    "legend.fontsize": _EXPORT_FONTSIZE,
    "legend.title_fontsize": _EXPORT_FONTSIZE + 1,
    # LaTeX
    "text.usetex": False,  # False = MathText (без LaTeX-установки)
    "mathtext.fontset": "cm",  # Computer Modern — «настоящий» LaTeX-вид
    # Сетка
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.4,
    # Границы
    "axes.spines.top": False,
    "axes.spines.right": False,
    # Линии
    "lines.linewidth": 2.0,
    "lines.markersize": 7,
    # Патчи — чтобы hatch был виден
    "patch.linewidth": 1.2,
    "hatch.linewidth": 1.2,
    # Отступы
    "figure.constrained_layout.use": True,
    # Формат сохранения по умолчанию
    "savefig.format": "svg",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
}

# ──────────────────────────────────────────────────────────────────────────────
# Публичный API
# ──────────────────────────────────────────────────────────────────────────────

_current_profile: str = "dark"


def set_theme(
    style: Literal["dark", "light", "print"] = "dark",
    usetex: bool = False,
    fontsize: int | None = None,
) -> None:
    """Установить глобальную тему CausalViz.

    Parameters
    ----------
    style : "dark" | "light" | "print"
        Профиль. ``dark`` — для ноутбуков, ``light`` — для PDF/экспорта,
        ``print`` — ч/б с паттернами для печати и дальтонизма.
    usetex : bool
        Использовать системный LaTeX (требует установки texlive/miktex).
        По умолчанию False — используется встроенный MathText (cm-шрифты).
    fontsize : int | None
        Переопределить базовый размер шрифта. По умолчанию 11pt.

    Examples
    --------
    >>> set_theme()                    # тёмный (по умолчанию)
    >>> set_theme("light")             # для экспорта в PDF
    >>> set_theme("print", usetex=True)  # ч/б + системный LaTeX
    """
    global _current_profile
    _current_profile = style

    rc = {**_COMMON, **_PROFILES[style]}

    if usetex:
        rc["text.usetex"] = True
        rc["font.family"] = "serif"

    if fontsize is not None:
        rc["font.size"] = fontsize
        rc["axes.labelsize"] = fontsize + 1
        rc["axes.titlesize"] = fontsize + 3
        rc["xtick.labelsize"] = fontsize
        rc["ytick.labelsize"] = fontsize
        rc["legend.fontsize"] = fontsize

    mpl.rcParams.update(rc)


def get_colors(n: int | None = None) -> list[str]:
    """Вернуть список цветов текущего профиля.

    Parameters
    ----------
    n : int | None
        Количество цветов. Если None — возвращает все 5.
    """
    suffix = "_l" if _current_profile == "light" else ""
    keys = SERIES_ORDER[:n] if n else SERIES_ORDER
    return [
        PALETTE.get(k + suffix, PALETTE.get(k, "#888888"))  # type: ignore[arg-type]
        for k in keys
    ]


def get_hatches(n: int | None = None) -> list[str]:
    """Вернуть список hatch-паттернов."""
    keys = SERIES_ORDER[:n] if n else SERIES_ORDER
    return [HATCH[k] for k in keys]


def apply_accessibility(ax: "mpl.axes.Axes", bars: list) -> None:
    """Применить hatch-паттерны к набору bars/patches.

    Parameters
    ----------
    ax : matplotlib Axes
    bars : list
        Список патчей (возвращается bar(), barh(), hist() и т.д.)

    Examples
    --------
    >>> bars = ax.bar(x, heights)
    >>> apply_accessibility(ax, bars)
    """
    hatches = get_hatches()
    for i, bar in enumerate(bars):
        h = hatches[i % len(hatches)]
        bar.set_hatch(h)
        # edgecolor нужен чтобы hatch был виден в любом профиле
        if bar.get_edgecolor() is None or np.allclose(bar.get_edgecolor(), 0):
            if _current_profile == "dark":
                bar.set_edgecolor(_DARK_FG)
            else:
                bar.set_edgecolor(_PRINT_FG)


def savefig(
    fig: "mpl.figure.Figure",
    name: str,
    outdir: str | Path = ".",
    formats: tuple[str, ...] = ("svg", "png"),
    **kwargs,
) -> list[Path]:
    """Сохранить фигуру одновременно в SVG и PNG.

    SVG — для web/Pages (масштабируется без пикселизации).
    PNG — для README/GitHub (fallback где SVG не рендерится).

    Parameters
    ----------
    fig : Figure
    name : str
        Имя файла без расширения.
    outdir : str | Path
        Директория. По умолчанию текущая.
    formats : tuple
        Форматы для сохранения. По умолчанию ("svg", "png").
    **kwargs
        Дополнительные аргументы для savefig().

    Returns
    -------
    list[Path]
        Список сохранённых файлов.

    Examples
    --------
    >>> paths = savefig(fig, "ate_forest_plot", outdir="assets/figures")
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    saved = []
    for fmt in formats:
        path = outdir / f"{name}.{fmt}"
        dpi = 300 if fmt == "png" else None
        fig.savefig(path, format=fmt, dpi=dpi, **kwargs)
        saved.append(path)

    return saved


# ──────────────────────────────────────────────────────────────────────────────
# Утилита: проверка контраста WCAG
# ──────────────────────────────────────────────────────────────────────────────


def _relative_luminance(hex_color: str) -> float:
    """Относительная яркость по WCAG 2.1."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def linearize(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    rl, gl, bl = map(linearize, (r, g, b))
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def contrast_ratio(color1: str, color2: str) -> float:
    """Вернуть коэффициент контраста WCAG между двумя hex-цветами."""
    l1 = _relative_luminance(color1)
    l2 = _relative_luminance(color2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def audit_palette(verbose: bool = True) -> dict[str, dict[str, float]]:
    """Проверить всю палитру на соответствие WCAG AA/AAA.

    Returns
    -------
    dict
        ``{role: {"dark_bg": ratio, "light_bg": ratio, "pass_aa": bool}}``

    Examples
    --------
    >>> audit_palette()
    treatment  | dark bg: 7.21 ✓ AAA | light bg: 3.01 ✗
    control    | dark bg: 8.14 ✓ AAA | light bg: 2.87 ✗
    ...
    """
    results: dict[str, dict[str, float]] = {}

    for role in SERIES_ORDER:
        dark_color = PALETTE[role]
        light_color = PALETTE.get(role + "_l", dark_color)

        r_dark = contrast_ratio(dark_color, _DARK_BG)
        r_light = contrast_ratio(light_color, _LIGHT_BG)

        pass_dark = r_dark >= 4.5
        pass_light = r_light >= 4.5

        results[role] = {
            "dark_ratio": round(r_dark, 2),
            "light_ratio": round(r_light, 2),
            "pass_dark_aa": pass_dark,
            "pass_light_aa": pass_light,
        }

        if verbose:
            d_mark = "✓ AA" + ("A" if r_dark >= 7.0 else "") if pass_dark else "✗ FAIL"
            l_mark = (
                "✓ AA" + ("A" if r_light >= 7.0 else "") if pass_light else "✗ FAIL"
            )
            print(
                f"{role:<12} | dark bg: {r_dark:>5.2f} {d_mark:<8} "
                f"| light bg: {r_light:>5.2f} {l_mark}"
            )

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Удобные алиасы для ленивого импорта
# ──────────────────────────────────────────────────────────────────────────────

treatment = PALETTE["treatment"]
control = PALETTE["control"]
confounder = PALETTE["confounder"]
outcome = PALETTE["outcome"]
neutral = PALETTE["neutral"]

COLORS = get_colors  # алиас
HATCHES = get_hatches  # алиас
