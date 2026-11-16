"""python -m korpus projekt.toml [--csv teile.csv]"""

import argparse
import sys
import tomllib
from pathlib import Path

from .ausgabe import als_csv, als_text
from .generator import erzeuge
from .laden import lade_projekt
from .modell import KorpusFehler


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="korpus")
    parser.add_argument("projekt")
    parser.add_argument("--csv", help="Teileliste zusätzlich als CSV schreiben")
    args = parser.parse_args(argv)
    try:
        ergebnis = erzeuge(lade_projekt(args.projekt))
    except (KorpusFehler, FileNotFoundError, tomllib.TOMLDecodeError) as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        return 1
    print(als_text(ergebnis))
    if args.csv:
        Path(args.csv).write_text(als_csv(ergebnis), encoding="utf-8-sig")
    return 0


if __name__ == "__main__":
    sys.exit(main())
