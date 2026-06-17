import subprocess
import sys


def test_cli_prints_hello_and_fulcrum_ascii_art():
    result = subprocess.run(
        [sys.executable, "-m", "sandcastle"],
        check=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout
    assert output.startswith("Hello\n")
    art_lines = output.splitlines()[1:]
    assert len(art_lines) == 6
    assert art_lines[0].startswith("███████╗")
    assert "██████╔╝" in art_lines[2]
