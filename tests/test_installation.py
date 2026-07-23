import subprocess
from pathlib import Path


def test_install():
    path = Path(__file__).parent.parent.resolve()
    subprocess.check_call([
        "pip", "install", "-e", str(path)
    ])
    subprocess.check_call([
        "pip", "uninstall", "telegram-bot-api", "-y"
    ])
