"""Kommandozeile: python -m hop check|stats <Pfad>"""

from __future__ import annotations

import argparse
import sys

from .analyse import find_samples, roundtrip_ok, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hop")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("check", "Round-Trip jeder .hop-Datei prüfen"),
        ("stats", "Kodierung, Zeilenenden und Zeilenanfänge mit Belegstellen auflisten"),
    ):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("path", nargs="?", default="samples")
    args = parser.parse_args(argv)

    paths = find_samples(args.path)
    if not paths:
        print(f"Keine .hop-Dateien unter {args.path} gefunden.", file=sys.stderr)
        return 2

    if args.command == "stats":
        print(stats(paths))
        return 0

    failed = [p for p in paths if not roundtrip_ok(p)]
    for path in paths:
        print(f"{'FEHLER' if path in failed else 'ok    '}  {path}")
    print(f"\n{len(paths) - len(failed)} von {len(paths)} Dateien bytegenau.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
