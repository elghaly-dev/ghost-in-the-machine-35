from ghost35.cli import main


def test_demo_exits_zero(capsys):
    code = main(["demo"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Ghost35 demo" in out
    assert "git status" in out
