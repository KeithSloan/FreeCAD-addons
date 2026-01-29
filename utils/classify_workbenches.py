#!/usr/bin/env python3
"""
Robust workbench classifier for FreeCAD-addons.

Detects:
- old-style (Init.py + InitGui.py)
- new-style (__init__.py + init_gui.py anywhere under a freecad/ directory)
- mixed
- unknown

Outputs CSV + summary.
"""

import csv
from pathlib import Path


def find_new_style(path: Path):
    """
    Detect new-style workbench layout:

    freecad/
        <anysubmodule>/
            __init__.py
            init_gui.py (or InitGui.py)
    """
    for freecad_dir in path.rglob("freecad"):
        if freecad_dir.is_dir():
            # Look inside freecad/ for any subpackage
            for sub in freecad_dir.iterdir():
                if not sub.is_dir():
                    continue
                init_file = sub / "__init__.py"
                gui1 = sub / "init_gui.py"
                gui2 = sub / "InitGui.py"

                if init_file.exists() and (gui1.exists() or gui2.exists()):
                    return True
    return False


def find_old_style(path: Path):
    """Detect old-style Init.py + InitGui.py at the addon root."""
    old_init = (path / "Init.py").exists() or (path / "init.py").exists()
    old_gui = (path / "InitGui.py").exists() or (path / "initgui.py").exists()
    return old_init and old_gui


def classify_workbench(path: Path):
    """Classify addon folder by structure."""
    name = path.name
    old_style = find_old_style(path)
    new_style = find_new_style(path)

    if old_style and not new_style:
        style = "old"
    elif new_style and not old_style:
        style = "new"
    elif old_style and new_style:
        style = "mixed"
    else:
        style = "unknown"

    return {
        "name": name,
        "style": style,
        "path": str(path),
        "old_style": old_style,
        "new_style": new_style,
    }


def scan_addons(root: Path):
    """Scan FreeCAD-addons root directory."""
    results = []
    for child in root.iterdir():
        if child.is_dir() and child.name != "utils":
            results.append(classify_workbench(child))
    return results


def write_csv(results, csv_path):
    """Write CSV report."""
    fieldnames = ["name", "style", "path", "old_style", "new_style"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def print_summary(results):
    totals = {
        "old": sum(r["style"] == "old" for r in results),
        "new": sum(r["style"] == "new" for r in results),
        "mixed": sum(r["style"] == "mixed" for r in results),
        "unknown": sum(r["style"] == "unknown" for r in results),
    }

    print("\nSummary")
    print("----------------------------")
    print(f"Total addons scanned : {len(results)}")
    print(f"Old-style            : {totals['old']}")
    print(f"New-style            : {totals['new']}")
    print(f"Mixed                : {totals['mixed']}")
    print(f"Unknown              : {totals['unknown']}")
    print("----------------------------")


def main():
    script_path = Path(__file__).resolve()
    addons_root = script_path.parents[1]

    print(f"Scanning: {addons_root}")

    results = scan_addons(addons_root)

    csv_path = script_path.parent / "workbench_report.csv"
    write_csv(results, csv_path)

    print(f"CSV written to: {csv_path}")
    print_summary(results)


if __name__ == "__main__":
    main()

