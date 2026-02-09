"""
Script d'insertion asynchrone de comptes KFC via l'API /insert.

Version asyncio + aiohttp avec workers, queue et affichage temps réel throttlé.
Comportement identique à insert_api.py (avancement.json, erreur_log.txt, mapping).
"""
import asyncio
import base64
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple

import aiohttp
from dotenv import load_dotenv

# Charger .env depuis le dossier insert
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
load_dotenv(os.path.join(SCRIPT_DIR, "..", "staff.env"))

IGNORED_KEYS = {"url", "jour", "mois", "annee"}
FIELD_MAP = {
    "cartiId": "customer_id",
    "mail": "email",
    "idd": "id",
    "date": "expired_at",
}
REQUIRED = {"customer_id", "carte", "point"}

AVANCEMENT_PATH = os.path.join(SCRIPT_DIR, "avancement.json")
ERREUR_LOG_PATH = os.path.join(SCRIPT_DIR, "erreur_log.txt")

# Config async
CONNECTOR_LIMIT = 100
CONNECTOR_LIMIT_PER_HOST = 30
TIMEOUT = 15
DISPLAY_THROTTLE = 0.3

# Compteurs partagés
valid_count = 0
duplicate_count = 0
error_count = 0
stats_lock = asyncio.Lock()
avancement_lock = asyncio.Lock()
last_display_time = 0.0


def reset_erreur_log() -> None:
    with open(ERREUR_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("")


def log_erreur_insert(source_file: str, line_content: str, error_type: str, details: str) -> None:
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ERREUR_LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"[{ts}] [{error_type}] source={source_file}\n")
            f.write(f"  ligne: {line_content[:500]}{'...' if len(line_content) > 500 else ''}\n")
            f.write(f"  détails: {details}\n")
            f.write("-" * 60 + "\n")
    except Exception:
        pass


def load_avancement() -> dict:
    if os.path.exists(AVANCEMENT_PATH):
        try:
            with open(AVANCEMENT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_avancement(data: dict) -> None:
    with open(AVANCEMENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def ensure_file_in_avancement(filename: str) -> None:
    async with avancement_lock:
        data = load_avancement()
        if filename not in data:
            data[filename] = 0
            save_avancement(data)


async def increment_avancement(filename: str) -> None:
    async with avancement_lock:
        data = load_avancement()
        data[filename] = data.get(filename, 0) + 1
        save_avancement(data)


def build_payload(raw: dict) -> dict:
    payload = {}
    for key, value in raw.items():
        if key in IGNORED_KEYS:
            continue
        api_key = FIELD_MAP.get(key, key)
        if value is None or value == "":
            if api_key in ("id", "email", "password", "nom", "prenom", "numero", "ddb", "expired_at"):
                payload[api_key] = None
            continue
        payload[api_key] = value

    if "point" in payload and payload["point"] is not None:
        try:
            payload["point"] = int(payload["point"])
        except (ValueError, TypeError):
            raise ValueError(f"point doit être un entier (reçu: {payload['point']!r})")

    if "expired_at" in payload and payload["expired_at"]:
        val = str(payload["expired_at"])
        if "0001-01-01" in val:
            payload["expired_at"] = None
        else:
            val = val.replace(".000Z", "").replace(".000z", "").rstrip("Zz")
            payload["expired_at"] = val
    if "expired_at" not in payload:
        payload["expired_at"] = None

    return payload


async def insert_one_async(session: aiohttp.ClientSession, payload: dict) -> Tuple[str, str]:
    base_url = os.getenv("KFC_API_URL", "http://localhost:8080")
    user = os.getenv("KFC_API_USERNAME") or os.getenv("BASIC_AUTH_USER")
    password = os.getenv("KFC_API_PASSWORD") or os.getenv("BASIC_AUTH_PASSWORD")

    if not user or not password:
        return "error", "Credentials API manquants dans .env"

    credentials = f"{user}:{password}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }

    try:
        async with session.post(
            f"{base_url}/insert",
            json=payload,
            headers=headers,
        ) as resp:
            if resp.status == 204:
                return "valid", "OK"
            if resp.status == 409:
                text = (await resp.text()).strip() or "La carte existe déjà"
                return "duplicate", text
            if resp.status == 401:
                return "error", "Authentification échouée (401)"
            text = (await resp.text()).strip()
            return "error", f"HTTP {resp.status}: {text}"
    except asyncio.TimeoutError:
        return "error", "Timeout"
    except aiohttp.ClientError as e:
        return "error", str(e)


def display_status_throttled(
    valid: int,
    duplicate: int,
    errors: int,
    total: int,
    cpm: float,
    workers: int,
    start_script: float,
) -> None:
    global last_display_time
    current = time.time()
    if current - last_display_time < DISPLAY_THROTTLE:
        return
    last_display_time = current
    display_status(valid, duplicate, errors, total, cpm, workers, start_script)


def display_status(
    valid: int,
    duplicate: int,
    errors: int,
    total: int,
    cpm: float,
    workers: int,
    start_script: float,
) -> None:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    elapsed = time.time() - start_script
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    valid_pct = f"({100 * valid / total:.1f}%)" if total else "(0%)"
    dup_pct = f"({100 * duplicate / total:.1f}%)" if total else "(0%)"
    error_pct = f"({100 * errors / total:.1f}%)" if total else "(0%)"

    content = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         POSTGRES - insert bycl3mser
         {CYAN}{workers} Workers | {cpm:.0f} CPM{RESET}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          Valid    : {GREEN}{valid:>6}{RESET}  {valid_pct}
          Duplicate: {YELLOW}{duplicate:>6}{RESET}  {dup_pct}
          Errors   : {RED}{errors:>6}{RESET}  {error_pct}
          Total    : {CYAN}{total:>6}{RESET}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     - Speed     : {CYAN}{cpm:.0f}{RESET} inserts/min
     - Runtime   : {hours:02}:{minutes:02}:{seconds:02}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    os.system("cls" if os.name == "nt" else "clear")
    print(content)


def list_txt_files() -> List[Tuple[str, int]]:
    files = []
    exclude = {os.path.basename(ERREUR_LOG_PATH)}
    for name in sorted(os.listdir(SCRIPT_DIR)):
        if name in exclude or not name.endswith(".txt"):
            continue
        path = os.path.join(SCRIPT_DIR, name)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for ln in f if ln.strip())
            except Exception:
                lines = 0
            files.append((name, lines))
    return files


@dataclass
class LineTask:
    filename: str
    line: str
    line_num: int


async def worker(
    queue: asyncio.Queue,
    session: aiohttp.ClientSession,
    start_script: float,
    max_workers: int,
) -> None:
    global valid_count, duplicate_count, error_count

    while True:
        try:
            task = await asyncio.wait_for(queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue

        if task is None:
            queue.task_done()
            break

        filename, line, _ = task.filename, task.line, task.line_num

        try:
            raw = json.loads(line)
        except json.JSONDecodeError as e:
            log_erreur_insert(filename, line, "JSON invalide", str(e))
            async with stats_lock:
                error_count += 1
                total = valid_count + duplicate_count + error_count
                elapsed = time.time() - start_script
                cpm = total / (elapsed / 60) if elapsed > 0 else 0
                display_status_throttled(
                    valid_count, duplicate_count, error_count, total, cpm, max_workers, start_script
                )
            await increment_avancement(filename)
            queue.task_done()
            continue

        try:
            payload = build_payload(raw)
        except ValueError as e:
            log_erreur_insert(filename, line, "Validation", str(e))
            async with stats_lock:
                error_count += 1
                total = valid_count + duplicate_count + error_count
                elapsed = time.time() - start_script
                cpm = total / (elapsed / 60) if elapsed > 0 else 0
                display_status_throttled(
                    valid_count, duplicate_count, error_count, total, cpm, max_workers, start_script
                )
            await increment_avancement(filename)
            queue.task_done()
            continue

        for req in REQUIRED:
            if req not in payload or payload[req] is None:
                log_erreur_insert(filename, line, "Champs requis manquants", f"Champ manquant: {req}")
                async with stats_lock:
                    error_count += 1
                    total = valid_count + duplicate_count + error_count
                    elapsed = time.time() - start_script
                    cpm = total / (elapsed / 60) if elapsed > 0 else 0
                    display_status_throttled(
                        valid_count, duplicate_count, error_count, total, cpm, max_workers, start_script
                    )
                await increment_avancement(filename)
                queue.task_done()
                break
        else:
            status, msg = await insert_one_async(session, payload)
            async with stats_lock:
                if status == "valid":
                    valid_count += 1
                elif status == "duplicate":
                    duplicate_count += 1
                else:
                    error_count += 1
                    log_erreur_insert(filename, line, "API", msg)
                total = valid_count + duplicate_count + error_count
                elapsed = time.time() - start_script
                cpm = total / (elapsed / 60) if elapsed > 0 else 0
                display_status_throttled(
                    valid_count, duplicate_count, error_count, total, cpm, max_workers, start_script
                )
            await increment_avancement(filename)

        queue.task_done()


async def producer(queue: asyncio.Queue, filepath: str, filename: str, max_insertions: int) -> int:
    await ensure_file_in_avancement(filename)
    avancement = load_avancement()
    start_at = avancement.get(filename, 0)
    skip_count = 0
    done_count = 0

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if done_count >= max_insertions:
                break
            line = line.strip()
            if not line:
                continue
            if skip_count < start_at:
                skip_count += 1
                continue
            await queue.put(LineTask(filename=filename, line=line, line_num=done_count))
            done_count += 1

    return done_count


def print_summary(valid: int, duplicate: int, error: int, total: int) -> None:
    valid_pct = f"({100 * valid / total:.1f}%)" if total else "(0%)"
    dup_pct = f"({100 * duplicate / total:.1f}%)" if total else "(0%)"
    error_pct = f"({100 * error / total:.1f}%)" if total else "(0%)"
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("         POSTGRES - insert bycl3mser")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"          Valid    : {valid:>6}  {valid_pct}")
    print(f"          Duplicate: {duplicate:>6}  {dup_pct}")
    print(f"          Errors   : {error:>6}  {error_pct}")
    print(f"          Total    : {total:>6}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


async def run_insert(
    filepath: str,
    filename: str,
    max_insertions: int,
    max_workers: int,
) -> Tuple[int, int, int]:
    global valid_count, duplicate_count, error_count, last_display_time
    valid_count = duplicate_count = error_count = 0
    last_display_time = 0.0

    connector = aiohttp.TCPConnector(
        limit=CONNECTOR_LIMIT,
        limit_per_host=CONNECTOR_LIMIT_PER_HOST,
    )
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    start_script = time.time()

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        queue = asyncio.Queue(maxsize=max_workers * 2)
        workers = [
            asyncio.create_task(worker(queue, session, start_script, max_workers))
            for _ in range(max_workers)
        ]
        producer_task = asyncio.create_task(producer(queue, filepath, filename, max_insertions))
        total_put = await producer_task
        await queue.join()

        for _ in range(max_workers):
            await queue.put(None)
        await asyncio.gather(*workers)

    return valid_count, duplicate_count, error_count


def main():
    reset_erreur_log()
    if not os.path.exists(AVANCEMENT_PATH):
        save_avancement({})

    txt_files = list_txt_files()
    if not txt_files:
        print("Aucun fichier .txt trouvé dans le dossier insert.")
        sys.exit(1)

    print("Fichiers .txt disponibles:\n")
    for i, (name, lines) in enumerate(txt_files, 1):
        print(f"  {i} | {name} | {lines} lignes")
    print()

    while True:
        try:
            choice = input("Entrez le numéro du fichier à traiter: ").strip()
            idx = int(choice)
            if 1 <= idx <= len(txt_files):
                break
            print("Numéro invalide.")
        except ValueError:
            print("Entrez un nombre valide.")

    filename = txt_files[idx - 1][0]
    filepath = os.path.join(SCRIPT_DIR, filename)
    total_lines = txt_files[idx - 1][1]
    avancement = load_avancement()
    start_at = avancement.get(filename, 0)
    restantes = max(0, total_lines - start_at)

    print(f"\nFichier: {filename}")
    print(f"Lignes déjà traitées: {start_at}")
    print(f"Lignes restantes: {restantes}")

    while True:
        try:
            max_input = input("\nNombre max d'insertions à effectuer: ").strip()
            max_insertions = int(max_input)
            if max_insertions > 0:
                break
            print("Entrez un nombre > 0.")
        except ValueError:
            print("Entrez un nombre valide.")

    while True:
        try:
            workers_input = input("Nombre de workers (1-100): ").strip()
            max_workers = int(workers_input)
            if 1 <= max_workers <= 100:
                break
            print("Entrez un nombre entre 1 et 100.")
        except ValueError:
            print("Entrez un nombre valide.")

    print(f"\nTraitement de {filename} (max {max_insertions} insertions, {max_workers} workers)...\n")

    valid, duplicate, error = asyncio.run(
        run_insert(filepath, filename, max_insertions, max_workers)
    )
    total = valid + duplicate + error

    print_summary(valid, duplicate, error, total)


if __name__ == "__main__":
    main()
