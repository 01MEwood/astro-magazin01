from pathlib import Path

import pytest

from hop import parse_bytes, parse_file, to_bytes
from hop.analyse import find_samples

SAMPLES = find_samples(Path(__file__).parent.parent / "samples")

# Erfundene Bytefolgen, keine echten HOP-Inhalte: sie prüfen nur, dass die
# verlustfreie Ebene nichts verändert, egal was in der Datei steht.
SYNTHETIC = {
    "leer": b"",
    "crlf": b"eins\r\nzwei\r\n",
    "lf": b"eins\nzwei\n",
    "cr": b"eins\rzwei\r",
    "gemischt": b"eins\r\nzwei\ndrei\rvier",
    "ohne_umbruch_am_ende": b"eins\r\nzwei",
    "leerzeilen": b"\r\n\r\neins\r\n\r\n",
    "leerraum": b"  eins \t\r\n\tzwei  \r\n",
    "cp1252": "Rückwand Größe ø8 €\r\n".encode("cp1252"),
    "utf8": "Rückwand Größe\r\n".encode("utf-8"),
    "utf8_bom": b"\xef\xbb\xbf" + "Rückwand\r\n".encode("utf-8"),
    "nicht_cp1252": b"a\x81b\x8dc\r\n",
    "sonderzeichen": b"a\x0bb\x0cc\x1cd\x85e\r\n",
    "alle_bytes": bytes(range(256)),
}


@pytest.mark.parametrize("data", SYNTHETIC.values(), ids=SYNTHETIC.keys())
def test_roundtrip_synthetisch(data):
    assert to_bytes(parse_bytes(data)) == data


@pytest.mark.parametrize("path", SAMPLES, ids=[str(p) for p in SAMPLES])
def test_roundtrip_samples(path):
    assert to_bytes(parse_file(path)) == path.read_bytes()


def test_zeilen_und_zeilenenden():
    doc = parse_bytes(b"eins\r\nzwei\ndrei")
    assert [(l.text, l.eol) for l in doc.lines] == [("eins", "\r\n"), ("zwei", "\n"), ("drei", "")]


def test_sonderzeichen_trennen_keine_zeile():
    assert len(parse_bytes(b"a\x0bb\x0cc\x1cd\x85e\r\n").lines) == 1


@pytest.mark.parametrize(
    "data, encoding, bom",
    [
        (b"abc\r\n", "ascii", b""),
        ("ü\r\n".encode("utf-8"), "utf-8", b""),
        (b"\xef\xbb\xbfabc", "utf-8", b"\xef\xbb\xbf"),
        ("ü\r\n".encode("cp1252"), "cp1252", b""),
        (b"\x81\r\n", "latin-1", b""),
    ],
)
def test_kodierung(data, encoding, bom):
    doc = parse_bytes(data)
    assert (doc.encoding, doc.bom) == (encoding, bom)
