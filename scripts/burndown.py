"""Generate docs/agile/burndown.svg from burndown.csv (stdlib only, no matplotlib)."""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CSV = BASE / "docs" / "agile" / "burndown.csv"
SVG = BASE / "docs" / "agile" / "burndown.svg"


def load_points(path=CSV):
    """Return list of (label, remaining) from the CSV."""
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append((f"{row['sprint']} d{row['day']}", int(row["remaining"])))
    return rows


def to_svg(points, path=SVG, width=720, height=320):
    """Write a simple polyline burndown chart."""
    max_y = max([p[1] for p in points] + [1])
    pad = 40
    n = max(len(points) - 1, 1)
    coords = []
    for i, (_, remaining) in enumerate(points):
        x = pad + (width - 2 * pad) * i / n
        y = pad + (height - 2 * pad) * (1 - remaining / max_y)
        coords.append((x, y))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    dots = "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#38bdf8"/>'
        for x, y in coords
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="#0f172a"/>
<text x="{width // 2}" y="22" fill="#e2e8f0" text-anchor="middle" font-size="16">Burndown — remaining story points</text>
<polyline points="{line}" fill="none" stroke="#38bdf8" stroke-width="2"/>
{dots}
<text x="{pad}" y="{height - 8}" fill="#94a3b8" font-size="11">{points[0][0]}: {points[0][1]}</text>
<text x="{width - pad}" y="{height - 8}" fill="#94a3b8" font-size="11" text-anchor="end">{points[-1][0]}: {points[-1][1]}</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")
    return path


if __name__ == "__main__":
    pts = load_points()
    out = to_svg(pts)
    print(f"Wrote {out} ({len(pts)} points)")
