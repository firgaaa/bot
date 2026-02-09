"""
Script d'insertion de comptes KFC via l'API /insert.

Récupère les fichiers .txt du dossier, affiche la liste (numéro | nom | nb lignes),
l'utilisateur choisit un fichier, puis chaque ligne (JSON) est traitée une par une.

Mappe les champs: cartiId -> customer_id, mail -> email, idd -> id
Champs ignorés: url, jour, mois, annee

Usage:
    python insert_api.py
"""
import base64
import json
import os
import sys
import time
from typing import List, Tuple

import requests
from dotenv import load_dotenv

# Charger .env depuis le dossier insert
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
load_dotenv(os.path.join(SCRIPT_DIR, "..", "staff.env"))

# Champs à ignorer (inutiles pour l'API)
IGNORED_KEYS = {"url", "jour", "mois", "annee"}

# Mapping des noms de champs source -> API
FIELD_MAP = {
    "cartiId": "customer_id",
    "mail": "email",
    "idd": "id",
    "date": "expired_at",
}

# Champs requis par l'API
REQUIRED = {"customer_id", "carte", "point"}

AVANCEMENT_PATH = os.path.join(SCRIPT_DIR, "avancement.json")
ERREUR_LOG_PATH = os.path.join(SCRIPT_DIR, "erreur_log.txt")


def reset_erreur_log() -> None:
    """Réinitialise le fichier erreur_log.txt à chaque lancement."""
    with open(ERREUR_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("")


def log_erreur_insert(source_file: str, line_content: str, error_type: str, details: str) -> None:
    """Enregistre les détails d'une erreur d'insert dans erreur_log.txt."""
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
    """Charge le fichier avancement.json. Crée vide si inexistant."""
    if os.path.exists(AVANCEMENT_PATH):
        try:
            with open(AVANCEMENT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_avancement(data: dict) -> None:
    """Sauvegarde avancement.json."""
    with open(AVANCEMENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ensure_file_in_avancement(filename: str) -> None:
    """Ajoute le fichier dans avancement avec 0 si absent."""
    data = load_avancement()
    if filename not in data:
        data[filename] = 0
        save_avancement(data)


def increment_avancement(filename: str) -> None:
    """Incrémente de 1 l'avancement du fichier."""
    data = load_avancement()
    data[filename] = data.get(filename, 0) + 1
    save_avancement(data)


def build_payload(raw: dict) -> dict:
    """Construit le payload pour /insert à partir des données brutes."""
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

    # Convertir point en int
    if "point" in payload and payload["point"] is not None:
        try:
            payload["point"] = int(payload["point"])
        except (ValueError, TypeError):
            raise ValueError(f"point doit être un entier (reçu: {payload['point']!r})")

    # Traiter expired_at: ignorer "0001-01-01" et retirer .000Z/Z
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


def insert_one(payload: dict) -> Tuple[str, str]:
    """
    Appelle POST /insert.
    Retourne ("valid"|"duplicate"|"error", message).
    """
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
        resp = requests.post(
            f"{base_url}/insert",
            json=payload,
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 204:
            return "valid", "OK"
        if resp.status_code == 409:
            return "duplicate", resp.text.strip() or "La carte existe déjà"
        if resp.status_code == 401:
            return "error", "Authentification échouée (401)"
        return "error", f"HTTP {resp.status_code}: {resp.text.strip()}"
    except requests.exceptions.RequestException as e:
        return "error", str(e)


def list_txt_files() -> List[Tuple[str, int]]:
    """Liste les fichiers .txt du dossier insert (lignes non vides)."""
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


def process_file(
    filepath: str,
    filename: str,
    max_insertions: int,
) -> Tuple[int, int, int]:
    """Traite un fichier ligne par ligne. Retourne (valid, duplicate, error)."""
    valid, duplicate, error = 0, 0, 0
    ensure_file_in_avancement(filename)
    start_at = load_avancement().get(filename, 0)
    done_count = 0
    skip_count = 0  # lignes déjà traitées (non vides) à sauter

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
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as e:
                error += 1
                log_erreur_insert(filename, line, "JSON invalide", str(e))
                increment_avancement(filename)
                done_count += 1
                continue
            try:
                payload = build_payload(raw)
            except ValueError as e:
                error += 1
                log_erreur_insert(filename, line, "Validation", str(e))
                increment_avancement(filename)
                done_count += 1
                continue
            for req in REQUIRED:
                if req not in payload or payload[req] is None:
                    error += 1
                    log_erreur_insert(
                        filename, line, "Champs requis manquants",
                        f"Champ requis manquant: {req}"
                    )
                    increment_avancement(filename)
                    done_count += 1
                    break
            else:
                status, msg = insert_one(payload)
                increment_avancement(filename)
                done_count += 1
                if status == "valid":
                    valid += 1
                elif status == "duplicate":
                    duplicate += 1
                else:
                    error += 1
                    log_erreur_insert(filename, line, "API", msg)

    return valid, duplicate, error


def print_summary(valid: int, duplicate: int, error: int, total: int):
    """Affiche la page de résumé."""
    valid_pct = f"({100 * valid / total:.1f}%)" if total else "(0%)"
    error_pct = f"({100 * error / total:.1f}%)" if total else "(0%)"
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("         POSTGRES - insert bycl3mser")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"          Valid    : {valid:>6}  {valid_pct}")
    print(f"          Duplicate: {duplicate:>6}")
    print(f"          Errors   : {error:>6}  {error_pct}")
    print(f"          Total    : {total:>6}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def main():
    # Réinitialiser erreur_log.txt à chaque lancement
    reset_erreur_log()

    # Créer avancement.json au premier démarrage s'il n'existe pas
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

    # Demander le nombre max d'insertions
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

    print(f"\nTraitement de {filename} (max {max_insertions} insertions)...\n")

    valid, duplicate, error = process_file(filepath, filename, max_insertions)
    total = valid + duplicate + error

    print_summary(valid, duplicate, error, total)


if __name__ == "__main__":
    main()
