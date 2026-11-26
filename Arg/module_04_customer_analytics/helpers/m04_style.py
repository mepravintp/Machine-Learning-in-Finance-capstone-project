"""
Module 4 — shared chart style
=============================

WHAT THIS FILE DOES
    Gives every Module 4 chart the same look, so Task 1–3 charts match in the report.
    It is a helper because more than one task uses it (project decision P-15).

    It provides:
      - colour names (SURFACE, INK, INK_2, GRID, BLUE, ORANGE, AQUA, CHURN, STAY)
      - apply_style(): sets matplotlib's global settings (background, grid, fonts)

    Colours: a light background, dark text, a quiet grid, and three colours that stay
    distinguishable for colour-blind readers (blue, orange, aqua). Churners and stayers always
    get the same colours in every chart.

HOW TO USE
    from m04_style import apply_style, BLUE, ORANGE, AQUA, CHURN, STAY, SURFACE, INK, INK_2, GRID
    apply_style()
"""
import matplotlib.pyplot as plt

# Background, main text, secondary text, grid lines.
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
# Three series colours (checked for colour-blind readers), always used in this order.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
# Churners and stayers always get the same colours in every chart.
CHURN, STAY = "#b8323a", BLUE                   # churners vs stayers, same in every chart


def apply_style() -> None:
    """Set matplotlib's global settings once; every chart drawn afterwards uses them.

    rcParams = matplotlib's settings dictionary. We remove the top/right borders, soften the
    grid and set small, readable font sizes.
    """
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
        "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 11,
        "axes.titleweight": "bold", "axes.labelsize": 9, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
        "figure.dpi": 110, "font.size": 9,
    })


if __name__ == "__main__":
    apply_style()
    print("Chart style applied. Colours:", {"blue": BLUE, "orange": ORANGE, "aqua": AQUA})
