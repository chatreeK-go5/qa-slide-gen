#!/usr/bin/env python3
"""
Render Jira metrics dashboards as static PNG charts.

Architecture note (per PRD):
  - n8n owns Jira access and writes JSON to data/YYYY-MM-DD/
  - This script ONLY reads pre-aggregated JSON — no Jira API calls.

Usage:
    python scripts/render_charts.py [--date YYYY-MM-DD]

If --date is omitted the most recent date folder under data/ is used.
Outputs PNG files to artifacts/YYYY-MM-DD/.
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
THEME = {
    "bg_color":        "#F5F0E8",   # warm paper-like background
    "grid_color":      "#D8CEBA",
    "title_fontsize":  18,
    "label_fontsize":  11,
    "value_fontsize":  10,
    "bar_alpha":       0.85,
    # Ordered palette for status bars
    "bar_colors": ["#4A7FA5", "#6E9FBF", "#92BECE", "#B4D4E2", "#D2E8F2"],
    # Priority colours shared across charts
    "priority_colors": {
        "Highest": "#C0392B",
        "High":    "#E67E22",
        "Medium":  "#27AE60",
        "Low":     "#2980B9",
        "Lowest":  "#95A5A6",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_bg(fig, *axes):
    """Paint background colour on figure and all supplied axes."""
    fig.patch.set_facecolor(THEME["bg_color"])
    for ax in axes:
        ax.set_facecolor(THEME["bg_color"])


def _title(ax, text, subtitle=""):
    """Set a bold, uppercase title (and optional subtitle) on an axes."""
    ax.set_title(
        text.upper(),
        fontsize=THEME["title_fontsize"],
        fontweight="bold",
        pad=14,
        loc="left",
    )
    if subtitle:
        ax.annotate(
            subtitle,
            xy=(0, 1.02),
            xycoords="axes fraction",
            fontsize=THEME["label_fontsize"],
            color="#555555",
        )


def _total_badge(ax, total, label="TOTAL"):
    """Draw a prominent total number in the top-right corner of an axes."""
    ax.text(
        0.98, 0.98, f"{label}\n{total}",
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=22, fontweight="bold",
        color="#2C3E50",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", alpha=0.7,
                  edgecolor="#AAAAAA"),
    )


def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓  saved → {path}")


def _make_autopct(counts):
    """Return an autopct callable that displays the raw count on each slice."""
    counter = [0]

    def autopct(_pct):
        val = counts[counter[0]]
        counter[0] += 1
        return str(val)

    return autopct


# ---------------------------------------------------------------------------
# Chart 1 – Production Issues
# ---------------------------------------------------------------------------

def render_production_issues(data: dict, output_path: Path):
    """Horizontal bar chart grouped by status, sorted descending."""
    statuses = sorted(data["statuses"], key=lambda x: x["count"], reverse=True)
    labels  = [s["label"] for s in statuses]
    counts  = [s["count"] for s in statuses]
    total   = data.get("total", sum(counts))

    colors = (THEME["bar_colors"] * ((len(labels) // len(THEME["bar_colors"])) + 1))[: len(labels)]

    fig, ax = plt.subplots(figsize=(12, 6))
    _apply_bg(fig, ax)

    bars = ax.barh(labels, counts, color=colors, alpha=THEME["bar_alpha"], height=0.55)

    # Value labels on bars
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + max(counts) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center", ha="left",
            fontsize=THEME["value_fontsize"], fontweight="bold",
        )

    ax.set_xlabel("Issue Count", fontsize=THEME["label_fontsize"])
    ax.set_xlim(0, max(counts) * 1.20)
    ax.tick_params(axis="y", labelsize=THEME["label_fontsize"])
    ax.tick_params(axis="x", labelsize=THEME["value_fontsize"])
    ax.grid(axis="x", color=THEME["grid_color"], linestyle="--", linewidth=0.7)
    ax.invert_yaxis()

    _title(ax, data.get("title", "PRODUCTION ISSUES"),
           subtitle=f"Date: {data.get('date', '')}")
    _total_badge(ax, total)

    fig.tight_layout()
    _save(fig, output_path)


# ---------------------------------------------------------------------------
# Chart 2 – Beauty in Sprint
# ---------------------------------------------------------------------------

def render_beauty_in_sprint(data: dict, output_path: Path):
    """Horizontal bar chart for sprint items, with highlighted total badge."""
    items   = data.get("items", [])
    labels  = [i["label"] for i in items]
    counts  = [i["count"] for i in items]
    total   = data.get("total", sum(counts))
    sprint  = data.get("sprint_name", "")

    colors = (THEME["bar_colors"] * ((len(labels) // len(THEME["bar_colors"])) + 1))[: len(labels)]

    fig, ax = plt.subplots(figsize=(12, 5))
    _apply_bg(fig, ax)

    bars = ax.barh(labels, counts, color=colors, alpha=THEME["bar_alpha"], height=0.50)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + max(counts) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center", ha="left",
            fontsize=THEME["value_fontsize"], fontweight="bold",
        )

    ax.set_xlabel("Issue Count", fontsize=THEME["label_fontsize"])
    ax.set_xlim(0, max(counts) * 1.20)
    ax.tick_params(axis="y", labelsize=THEME["label_fontsize"])
    ax.tick_params(axis="x", labelsize=THEME["value_fontsize"])
    ax.grid(axis="x", color=THEME["grid_color"], linestyle="--", linewidth=0.7)
    ax.invert_yaxis()

    title_text = data.get("title", "BEAUTY IN SPRINT")
    if sprint:
        title_text += f" – {sprint}"
    _title(ax, title_text)
    _total_badge(ax, total)

    fig.tight_layout()
    _save(fig, output_path)


# ---------------------------------------------------------------------------
# Chart 3 – Over 14 Days (stacked bars by priority)
# ---------------------------------------------------------------------------

def render_over_14_days(data: dict, output_path: Path):
    """Stacked horizontal bar chart: PI vs Beauty, stacked by priority."""
    priority_keys = ["highest", "high", "medium"]
    priority_labels = ["Highest", "High", "Medium"]
    groups = []
    for key in ("pi", "beauty"):
        entry = data.get(key, {})
        groups.append({
            "label": entry.get("label", key.upper()),
            "values": [entry.get(p, 0) for p in priority_keys],
        })

    group_labels = [g["label"] for g in groups]
    n_groups = len(groups)
    bar_height = 0.45

    fig, ax = plt.subplots(figsize=(12, 4))
    _apply_bg(fig, ax)

    lefts = np.zeros(n_groups)
    for idx, (pkey, plabel) in enumerate(zip(priority_keys, priority_labels)):
        values = np.array([g["values"][idx] for g in groups], dtype=float)
        color  = THEME["priority_colors"].get(plabel, "#888888")
        bars   = ax.barh(
            group_labels, values, left=lefts,
            color=color, alpha=THEME["bar_alpha"],
            height=bar_height, label=plabel,
        )
        # Annotate segment if wide enough
        for i, (bar, val) in enumerate(zip(bars, values)):
            if val > 0:
                ax.text(
                    lefts[i] + val / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(int(val)),
                    ha="center", va="center",
                    fontsize=THEME["value_fontsize"], fontweight="bold",
                    color="white",
                )
        lefts += values

    ax.set_xlabel("Issue Count", fontsize=THEME["label_fontsize"])
    ax.tick_params(axis="y", labelsize=THEME["label_fontsize"])
    ax.tick_params(axis="x", labelsize=THEME["value_fontsize"])
    ax.grid(axis="x", color=THEME["grid_color"], linestyle="--", linewidth=0.7)
    ax.legend(loc="lower right", fontsize=THEME["value_fontsize"])

    _title(ax, data.get("title", "OVER – 14 DAYS"))

    fig.tight_layout()
    _save(fig, output_path)


# ---------------------------------------------------------------------------
# Chart 4 – Summary by Priority (two pie charts)
# ---------------------------------------------------------------------------

def render_summary_by_priority(data: dict, output_path: Path):
    """Two pie charts side-by-side: Beauty and PI."""
    sections = [data.get("beauty", {}), data.get("pi", {})]

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    _apply_bg(fig, *axes)

    for ax, section in zip(axes, sections):
        prios  = section.get("priorities", [])
        labels = [p["label"] for p in prios]
        counts = [p["count"]  for p in prios]
        total  = section.get("total", sum(counts))
        title  = section.get("label", "")

        colors = [THEME["priority_colors"].get(lbl, "#AAAAAA") for lbl in labels]

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=None,
            colors=colors,
            autopct=_make_autopct(counts),
            startangle=140,
            pctdistance=0.72,
            wedgeprops=dict(width=0.65, edgecolor="white", linewidth=1.5),
        )
        for at in autotexts:
            at.set_fontsize(THEME["value_fontsize"])
            at.set_fontweight("bold")
            at.set_color("white")

        # Centre total label
        ax.text(0, 0, str(total), ha="center", va="center",
                fontsize=24, fontweight="bold", color="#2C3E50")

        ax.set_title(title, fontsize=THEME["title_fontsize"],
                     fontweight="bold", pad=10)

        # Legend
        legend_patches = [
            mpatches.Patch(color=THEME["priority_colors"].get(lbl, "#AAAAAA"),
                           label=f"{lbl}: {cnt}")
            for lbl, cnt in zip(labels, counts)
        ]
        ax.legend(handles=legend_patches, loc="lower center",
                  bbox_to_anchor=(0.5, -0.18), ncol=2,
                  fontsize=THEME["value_fontsize"] - 1, framealpha=0.5)

    fig.suptitle(data.get("title", "SUMMARY BY PRIORITY").upper(),
                 fontsize=THEME["title_fontsize"], fontweight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, output_path)


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

RENDERERS = {
    "production_issues":   render_production_issues,
    "beauty_in_sprint":    render_beauty_in_sprint,
    "over_14_days":        render_over_14_days,
    "summary_by_priority": render_summary_by_priority,
}


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def resolve_date(requested: str | None, data_root: Path) -> str:
    """Return a valid date string (YYYY-MM-DD) under data_root."""
    if requested:
        target = data_root / requested
        if not target.is_dir():
            print(f"ERROR: data directory not found: {target}", file=sys.stderr)
            sys.exit(1)
        return requested

    # Pick the most recent date folder
    date_dirs = sorted(
        [p.name for p in data_root.iterdir() if p.is_dir()],
        reverse=True,
    )
    if not date_dirs:
        print(f"ERROR: no date folders found under {data_root}", file=sys.stderr)
        sys.exit(1)
    return date_dirs[0]


def main():
    repo_root = Path(__file__).resolve().parent.parent
    data_root = repo_root / "data"
    artifacts_root = repo_root / "artifacts"

    parser = argparse.ArgumentParser(description="Render Jira metrics charts.")
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Date folder to render (default: most recent in data/).",
    )
    args = parser.parse_args()

    date_str   = resolve_date(args.date, data_root)
    data_dir   = data_root / date_str
    output_dir = artifacts_root / date_str

    print(f"Rendering charts for: {date_str}")
    print(f"  Input  : {data_dir}")
    print(f"  Output : {output_dir}")

    errors = []
    for name, renderer in RENDERERS.items():
        json_path = data_dir / f"{name}.json"
        png_path  = output_dir / f"{name}.png"

        if not json_path.exists():
            print(f"  ⚠  skipping {name} — {json_path} not found")
            continue

        try:
            with open(json_path, encoding="utf-8") as fh:
                data = json.load(fh)
            renderer(data, png_path)
        except Exception as exc:
            traceback.print_exc()
            print(f"  ✗  {name}: {exc}", file=sys.stderr)
            errors.append(name)

    if errors:
        print(f"\nFailed charts: {errors}", file=sys.stderr)
        sys.exit(1)

    print("\nAll charts rendered successfully.")


if __name__ == "__main__":
    main()
