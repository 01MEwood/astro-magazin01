from hop.__main__ import main


def test_check_und_stats(tmp_path, capsys):
    (tmp_path / "a.hop").write_bytes(b"eins\r\nzwei\r\n")
    (tmp_path / "B.HOP").write_bytes(b"eins\n")
    assert main(["check", str(tmp_path)]) == 0
    assert "2 von 2" in capsys.readouterr().out
    assert main(["stats", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "CRLF" in out and "LF" in out
    assert "a.hop:1" in out or "B.HOP:1" in out


def test_ohne_dateien(tmp_path):
    assert main(["check", str(tmp_path)]) == 2
