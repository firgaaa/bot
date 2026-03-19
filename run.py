"""
Lanceur - database_up, puis API Rust + bot Telegram.

Usage:
    python run.py

1. Charge .env
2. Exécute database_up.py (tables bot + migrations Diesel kfc_storage)
3. Lance cargo run -r (API) et main/bot.py dans 2 fenêtres distinctes

Ctrl+C ici arrête les deux processus.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
IS_WINDOWS = sys.platform == "win32"


def load_env() -> bool:
    """Charge .env depuis la racine du projet."""
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        print(f"Erreur: {env_file} introuvable. Copier .env.example en .env.")
        return False
    from dotenv import load_dotenv
    load_dotenv(env_file)
    return True


def run_database_up() -> bool:
    """Exécute database_up.py (tables bot + Diesel kfc_storage)."""
    print("Mise à jour de la base de données...")
    r = subprocess.run(
        [sys.executable, str(ROOT_DIR / "database_up.py")],
        cwd=ROOT_DIR,
        env=os.environ.copy(),
    )
    if r.returncode != 0:
        print("Erreur: database_up.py a échoué.")
        return False
    print("Base de données à jour.\n")
    return True


def main() -> None:
    os.chdir(ROOT_DIR)

    if not load_env():
        sys.exit(1)

    if not run_database_up():
        sys.exit(1)

    api_dir = ROOT_DIR / "api"
    main_dir = ROOT_DIR / "main"
    CREATE_NEW_CONSOLE = 0x00000010
    processes = []

    def cleanup(_s=None, _f=None):
        print("\nArrêt en cours...")
        for p in processes:
            try:
                if IS_WINDOWS:
                    subprocess.run(
                        ["taskkill", "/PID", str(p.pid), "/T", "/F"],
                        capture_output=True,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
                    )
                else:
                    p.terminate()
                    p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        print("Processus arrêtés.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    print("Lancement de l'API Rust...")
    p_api = subprocess.Popen(
        ["cmd", "/c", "cd", "/d", str(api_dir), "&&", "cargo", "run", "-r"],
        creationflags=CREATE_NEW_CONSOLE,
        env=os.environ.copy(),
    )
    processes.append(p_api)

    print("Lancement du bot Telegram...")
    p_bot = subprocess.Popen(
        ["cmd", "/c", "cd", "/d", str(main_dir), "&&", "python", "bot.py"],
        creationflags=CREATE_NEW_CONSOLE,
        env=os.environ.copy(),
    )
    processes.append(p_bot)

    print("\nAPI et bot lancés. Ctrl+C ici arrête les deux.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
