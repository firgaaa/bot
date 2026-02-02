# Documentation complète - clemser_kfc_api

## 📚 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation et configuration](./INSTALLATION.md)
3. [Référence API complète](./API_REFERENCE.md)
4. [Base de données](./DATABASE.md)
5. [Architecture du code](./ARCHITECTURE.md)
6. [Sécurité et authentification](./SECURITY.md)
7. [Exemples d'utilisation](./EXAMPLES.md)
8. [Tests](./TESTING.md)

---

## Vue d'ensemble

**clemser_kfc_api** est une API REST écrite en Rust utilisant le framework **Actix-web**. Elle permet de gérer un stock de comptes KFC (cartes fidélité) avec les fonctionnalités suivantes :

- ✅ **Insertion** de comptes KFC dans une base de données PostgreSQL
- ✅ **Mise à jour** de comptes existants
- ✅ **Génération** de comptes disponibles selon des critères (points, statut)
- ✅ **Vérification en temps réel** via l'API officielle KFC France
- ✅ **Authentification** via Basic Auth sur tous les endpoints

### Stack technique

| Composant | Technologie | Version |
|-----------|------------|---------|
| **Langage** | Rust | Edition 2024 |
| **Framework Web** | Actix-web | 4.12.1 |
| **Base de données** | PostgreSQL | - |
| **ORM** | Diesel | 2.3.5 |
| **HTTP Client** | wreq | 5.3.0 |
| **Async Runtime** | Tokio | 1.49.0 |
| **Logging** | env_logger | 0.11.8 |

### Fonctionnalités principales

1. **Gestion de stock** : Stockage et gestion de comptes KFC avec leurs informations (email, password, points, etc.)
2. **Validation automatique** : Vérification de la validité des comptes via l'API KFC avant de les marquer comme "vendus"
3. **Sécurité** : Protection de tous les endpoints par Basic Authentication
4. **Transactions** : Utilisation de transactions SQL pour garantir la cohérence des données

---

## Endpoints disponibles

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|------------------|
| `POST` | `/insert` | Insérer un nouveau compte KFC | ✅ Requis |
| `PUT` | `/update` | Mettre à jour un compte existant | ✅ Requis |
| `POST` | `/generate` | Générer/trouver un compte disponible | ✅ Requis |

> **Note** : Tous les endpoints nécessitent une authentification Basic Auth.

---

## Structure du projet

```
clemser_kfc_api/
├── src/
│   ├── main.rs              # Point d'entrée de l'application
│   ├── api/                 # Modules des endpoints API
│   │   ├── insert.rs        # POST /insert
│   │   ├── update.rs        # PUT /update
│   │   ├── generate.rs      # POST /generate
│   │   ├── middleware.rs    # Middleware Basic Auth
│   │   └── mod.rs           # Module API
│   ├── database/            # Gestion de la base de données
│   │   ├── mod.rs           # Fonctions DB (insert, update, etc.)
│   │   └── model.rs         # Modèles de données
│   ├── errors.rs            # Gestion des erreurs
│   ├── recheck.rs          # Vérification via API KFC
│   └── schema.rs           # Schéma Diesel (généré)
├── migrations/              # Migrations de base de données
├── docs/                   # Documentation (ce dossier)
├── Cargo.toml              # Dépendances Rust
├── diesel.toml             # Configuration Diesel
└── .env                    # Variables d'environnement
```

---

## Démarrage rapide

### 1. Prérequis

- Rust (dernière version stable)
- PostgreSQL 13+
- Diesel CLI

### 2. Installation

```bash
# Cloner le projet (si applicable)
cd clemser_kfc_api

# Installer les dépendances
cargo build

# Installer Diesel CLI
cargo install diesel_cli --no-default-features --features postgres
```

### 3. Configuration

Créer un fichier `.env` à la racine :

```env
RUST_LOG=info
DATABASE_URL=postgres://user:password@localhost:5432/kfc_bot
PORT=8080
BASIC_AUTH_USER=username
BASIC_AUTH_PASSWORD=password
```

### 4. Base de données

```bash
# Créer la base de données
createdb kfc_bot

# Exécuter les migrations
diesel migration run
```

### 5. Lancer l'API

```bash
cargo run
```

L'API sera accessible sur `http://localhost:8080`

---

## Documentation détaillée

Pour plus d'informations, consultez les sections suivantes :

- **[Installation et configuration](./INSTALLATION.md)** : Guide complet d'installation
- **[Référence API](./API_REFERENCE.md)** : Documentation détaillée de tous les endpoints
- **[Base de données](./DATABASE.md)** : Schéma, migrations et modèles
- **[Architecture](./ARCHITECTURE.md)** : Structure du code et flux de données
- **[Sécurité](./SECURITY.md)** : Authentification et bonnes pratiques
- **[Exemples](./EXAMPLES.md)** : Exemples d'utilisation avec différents langages
- **[Tests](./TESTING.md)** : Guide de test et validation

---

## Support

Pour toute question ou problème, consultez la documentation détaillée dans les fichiers correspondants.

---

**Version** : 0.1.0  
**Dernière mise à jour** : 2026-01-26
