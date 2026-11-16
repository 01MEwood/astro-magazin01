import sys

from .auswertung import EingabeFehler, auswerten


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Aufruf: python -m auswertung <Ordner mit auftraege.csv und verluste.csv>", file=sys.stderr)
        return 2
    try:
        print(auswerten(args[0]))
    except (EingabeFehler, FileNotFoundError) as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
