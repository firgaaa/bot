# Installation et Configuration

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation de Rust](#installation-de-rust)
3. [Installation de PostgreSQL](#installation-de-postgresql)
4. [Installation des dépendances](#installation-des-dépendances)
5. [Configuration de la base de données](#configuration-de-la-base-de-données)
6. [Configuration de l'API](#configuration-de-lapi)
7. [Lancement de l'API](#lancement-de-lapi)
8. [Vérification](#vérification)

---

## Prérequis

### Système d'exploitation

- **Windows** : Windows 10 ou supérieur
- **Linux** : Distribution moderne (Ubuntu 20.04+, Debian 11+, etc.)
- **macOS** : macOS 10.15 ou supérieur

### Logiciels requis

- **Rust** : Version 1.70+ (stable)
- **PostgreSQL** : Version 13 ou supérieure
- **Git** : Pour cloner le projet (optionnel)
- **Cargo** : Inclus avec Rust

---

## Installation de Rust

### Windows

1. Télécharger Rust depuis [rustup.rs](https://rustup.rs/)
2. Exécuter `rustup-init.exe`
3. Suivre les instructions d'installation
4. Redémarrer le terminal

### Linux / macOS

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Vérification

```bash
rustc --version
cargo --version
```

---

## Installation de PostgreSQL

### Windows

1. Télécharger PostgreSQL depuis [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Installer avec l'installateur officiel
3. Noter le mot de passe du superutilisateur `postgres`
4. Vérifier que le service PostgreSQL est démarré

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS

```bash
brew install postgresql
brew services start postgresql
```

### Vérification

```bash
psql --version
```

---

## Installation des dépendances

### 1. Cloner ou naviguer vers le projet

```bash
cd clemser_kfc_api
```

### 2. Installer les dépendances Rust

```bash
cargo build
```

Cette commande télécharge et compile toutes les dépendances nécessaires.

### 3. Installer Diesel CLI

Diesel CLI est nécessaire pour gérer les migrations de base de données :

```bash
cargo install diesel_cli --no-default-features --features postgres
```

**Note** : Cette installation peut prendre plusieurs minutes.

### Vérification

```bash
diesel --version
```

---

## Configuration de la base de données

### 1. Créer la base de données

#### Méthode 1 : Via psql

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE kfc_bot;

# (Optionnel) Créer un utilisateur dédié
CREATE USER kfc_user WITH PASSWORD 'ton_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE kfc_bot TO kfc_user;

# Se connecter à la nouvelle base
\c kfc_bot
GRANT ALL ON SCHEMA public TO kfc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kfc_user;

# Quitter
\q
```

#### Méthode 2 : Via ligne de commande

```bash
createdb -U postgres kfc_bot
```

### 2. Exécuter les migrations

```bash
cd clemser_kfc_api
diesel migration run
```

Cette commande va :
- Créer la table `kfc_storage`
- Ajouter toutes les colonnes nécessaires
- Créer les triggers et fonctions SQL

### 3. Vérifier la structure

```bash
psql -U postgres -d kfc_bot -c "\d kfc_storage"
```

Vous devriez voir la structure complète de la table.

---

## Configuration de l'API

### 1. Créer le fichier `.env`

Créer un fichier `.env` à la racine du projet :

```env
# Niveau de log (debug, info, warn, error)
RUST_LOG=info

# URL de connexion PostgreSQL
# Format: postgres://username:password@host:port/database
DATABASE_URL=postgres://postgres:ton_mot_de_passe@localhost:5432/kfc_bot

# Port d'écoute de l'API (par défaut: 8080)
PORT=8080

# Credentials Basic Auth
BASIC_AUTH_USER=username
BASIC_AUTH_PASSWORD=password
```

### 2. Exemple de configuration

```env
RUST_LOG=info
DATABASE_URL=postgres://postgres:root@localhost:5432/kfc_bot
PORT=8080
BASIC_AUTH_USER=votre_username
BASIC_AUTH_PASSWORD=votre_mot_de_passe
```

### 3. Sécurité du fichier `.env`

⚠️ **Important** : Le fichier `.env` contient des informations sensibles. Assurez-vous qu'il est dans `.gitignore` :

```gitignore
.env
*.env
```

---

## Lancement de l'API

### Mode développement

```bash
cargo run
```

### Mode production (optimisé)

```bash
cargo build --release
./target/release/clemser_kfc_api
```

### Vérification du démarrage

Vous devriez voir dans les logs :

```
[INFO] Starting clemser_kfc_api...
[INFO] Loading database configuration...
[INFO] Database connected successfully.
[INFO] Starting server on port 8080
[INFO] starting 4 workers
[INFO] Actix runtime found; starting in Actix runtime
[INFO] starting service: "actix-web-service-0.0.0.0:8080"
```

---

## Vérification

### 1. Test de connexion

L'API devrait être accessible sur `http://localhost:8080`

### 2. Test avec curl

```bash
# Test sans authentification (doit retourner 401)
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"min_points": 100, "max_points": 1000}'
```

Réponse attendue : `401 Unauthorized`

### 3. Test avec authentification

```bash
# Générer le token Basic Auth
# Format: base64(username:password)
echo -n "username:password" | base64

# Test avec authentification
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Basic <token_base64>" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 100, "max_points": 1000}'
```

### 4. Utiliser le script de test Python

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Lancer les tests
python teste_api.py
```

---

## Dépannage

### Erreur : "Failed to connect to the database"

**Causes possibles** :
- PostgreSQL n'est pas démarré
- `DATABASE_URL` incorrect dans `.env`
- La base de données n'existe pas
- Mauvais mot de passe

**Solutions** :
```bash
# Vérifier que PostgreSQL tourne
# Windows: Services > PostgreSQL
# Linux: sudo systemctl status postgresql

# Tester la connexion
psql -U postgres -d kfc_bot

# Vérifier DATABASE_URL dans .env
```

### Erreur : "PORT must be a valid u16 number"

**Solution** : Vérifier que `PORT` dans `.env` est un nombre entre 1 et 65535.

### Erreur : "Server configuration error: Missing auth credentials"

**Solution** : Vérifier que `BASIC_AUTH_USER` et `BASIC_AUTH_PASSWORD` sont définis dans `.env`.

### Erreur lors des migrations

**Solution** :
```bash
# Vérifier la connexion
diesel database reset

# Réessayer les migrations
diesel migration run
```

---

## Prochaines étapes

Une fois l'installation terminée :

1. ✅ Consulter la [Référence API](./API_REFERENCE.md) pour utiliser les endpoints
2. ✅ Lire les [Exemples d'utilisation](./EXAMPLES.md)
3. ✅ Consulter la [Documentation de la base de données](./DATABASE.md)

---

**Note** : En cas de problème, vérifiez les logs avec `RUST_LOG=debug` pour plus de détails.
