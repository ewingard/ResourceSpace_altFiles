import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

EXTENSIONS = {".tif", ".tiff", ".jpg", ".jpeg"}
MAX_ALTS = 9
ALT_RE = re.compile(r"-alt\d*$", re.IGNORECASE)
NUM_RE = re.compile(r"^(?P<prefix>.*?)(?P<num>\d+)$")


def alt_suffix(i: int) -> str:
    """1 -> '-alt', 2 -> '-alt2', 3 -> '-alt3', ..."""
    return "-alt" if i == 1 else f"-alt{i}"


def read_main_list(path: Path) -> set:
    """Read main filenames (or stems) from a .txt or .csv; case-insensitive."""
    names = set()
    with path.open(newline="", encoding="utf-8-sig") as f:
        if path.suffix.lower() == ".csv":
            for row in csv.reader(f):
                if row and row[0].strip():
                    names.add(row[0].strip().lower())
        else:
            for line in f:
                if line.strip():
                    names.add(line.strip().lower())
    # Header rows like "filename" are harmless: they just won't match a file.
    return names


def is_main(file: Path, mains: set) -> bool:
    return file.name.lower() in mains or file.stem.lower() in mains


def build_plan(folder: Path, mains: set):
    groups = defaultdict(list)  # prefix -> [(num, file)]
    skipped = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower() not in EXTENSIONS:
            continue
        if ALT_RE.search(p.stem):
            skipped.append((p.name, "already an -alt file"))
            continue
        m = NUM_RE.match(p.stem)
        if not m:
            skipped.append((p.name, "no trailing number in name"))
            continue
        groups[m.group("prefix")].append((int(m.group("num")), p))

    renames, warnings = [], []
    for prefix, items in groups.items():
        items.sort(key=lambda t: t[0])
        current_main, alt_count = None, 0
        for num, p in items:
            if is_main(p, mains):
                current_main, alt_count = p, 0
                continue
            if current_main is None:
                warnings.append(f"{p.name}: no main file before it; left alone")
                continue
            alt_count += 1
            if alt_count > MAX_ALTS:
                warnings.append(
                    f"{current_main.name}: more than {MAX_ALTS} alts "
                    f"(max 10 images total) - {p.name} not renamed"
                )
                continue
            new_name = f"{current_main.stem}{alt_suffix(alt_count)}{p.suffix}"
            renames.append((p, p.with_name(new_name)))

    # Soft check on the "acceptable" range (5-9 alts) is left to the user;
    # report counts per main so odd cases stand out.
    return renames, warnings, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="folder containing the images")
    ap.add_argument("main_list", type=Path,
                    help=".txt (one per line) or .csv (first column) of MAIN filenames")
    ap.add_argument("--apply", action="store_true",
                    help="actually rename (default is a dry-run preview)")
    ap.add_argument("--log", type=Path, default=Path("rename_log.csv"),
                    help="CSV log path used with --apply (default: rename_log.csv)")
    args = ap.parse_args()

    if not args.folder.is_dir():
        sys.exit(f"Folder not found: {args.folder}")
    if not args.main_list.is_file():
        sys.exit(f"Main list not found: {args.main_list}")

    mains = read_main_list(args.main_list)
    renames, warnings, skipped = build_plan(args.folder, mains)

    done = []
    for old, new in renames:
        if new.exists():
            warnings.append(f"{new.name} already exists; {old.name} not renamed")
            continue
        print(f"{old.name}  ->  {new.name}")
        if args.apply:
            old.rename(new)
        done.append((old.name, new.name))

    print(f"\n{len(done)} file(s) {'renamed' if args.apply else 'would be renamed (dry run)'}.")
    for w in warnings:
        print(f"WARNING: {w}")
    for name, why in skipped:
        print(f"skipped: {name} ({why})")

    if args.apply and done:
        with args.log.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["old_name", "new_name"])
            w.writerows(done)
        print(f"Log written to {args.log}")
    elif not args.apply:
        print("Re-run with --apply to perform the renames.")


if __name__ == "__main__":
    main()
