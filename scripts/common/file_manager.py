from pathlib import Path
from datetime import datetime


def create_backup_folders():

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    history = Path("backup/history") / timestamp

    latest = Path("backup/latest")

    history.mkdir(parents=True, exist_ok=True)

    latest.mkdir(parents=True, exist_ok=True)

    return history, latest, timestamp