import subprocess
import sys


def test_fish_command_prints_ascii_fish() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "sandcastle", "fish"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == "><(((('>\n"
    assert result.stderr == ""
