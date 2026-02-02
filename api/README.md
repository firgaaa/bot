# clemser_kfc_api

API REST en **Rust** (Actix-web) pour gérer un stock de comptes KFC (cartes fidélité), avec authentification Basic Auth et vérification via l’API KFC France.

## Fonctionnalités

- **Insertion** de comptes KFC (PostgreSQL)
- **Mise à jour** de comptes existants
- **Génération** de comptes disponibles (filtres points/statut)
- **Vérification** en temps réel via l’API officielle KFC France
- **Authentification** Basic Auth sur tous les endpoints

## Prérequis

- Rust (stable)
- PostgreSQL 13+
- [Diesel CLI](https://diesel.rs/guides/getting-started) pour les migrations

## Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_USER/clemser_kfc_api.git
cd clemser_kfc_api

# Build
cargo build

# Copier le fichier d'exemple et configurer
cp exemple.env .env
# Éditer .env avec DATABASE_URL, BASIC_AUTH_USER, BASIC_AUTH_PASSWORD, etc.

# Créer la base et lancer les migrations
createdb kfc_bot
diesel migration run

# Lancer l'API
cargo run
```

L’API écoute par défaut sur le port **8080**.

## Configuration

Variables d’environnement (fichier `.env`) :

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | URL PostgreSQL (`postgres://user:pass@host:port/db`) |
| `PORT` | Port HTTP (défaut : 8080) |
| `BASIC_AUTH_USER` | Utilisateur Basic Auth |
| `BASIC_AUTH_PASSWORD` | Mot de passe Basic Auth |
| `RUST_LOG` | Niveau de log (ex. `info`, `debug`) |

Ne **jamais** commiter le fichier `.env` (il est dans `.gitignore`).

## Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/insert` | Insérer un compte KFC |
| `PUT` | `/update` | Mettre à jour un compte |
| `POST` | `/generate` | Obtenir un compte disponible (critères points/statut) |
| `GET` | `/get_old` | Récupérer un compte « ancien » |

Tous les endpoints exigent une authentification **Basic Auth**.

## Documentation

La documentation détaillée est dans le dossier [`docs/`](docs/) :

- [Vue d’ensemble et structure](docs/README.md)
- [Installation et configuration](docs/INSTALLATION.md)
- [Référence API](docs/API_REFERENCE.md)
- [Base de données](docs/DATABASE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Sécurité](docs/SECURITY.md)
- [Exemples](docs/EXAMPLES.md)
- [Tests](docs/TESTING.md)

## Mise en ligne sur GitHub

1. Créer un dépôt sur [GitHub](https://github.com/new) (sans initialiser avec un README si le projet existe déjà).
2. Vérifier que `.env` n’est **pas** suivi par Git : `git status` ne doit pas lister `.env`.
3. Pousser le code :

   ```bash
   git remote add origin https://github.com/VOTRE_USER/clemser_kfc_api.git
   git branch -M main
   git push -u origin main
   ```

4. Optionnel : ajouter un fichier `LICENSE` (MIT, Apache 2.0, etc.) à la racine.

## Licence

Voir le fichier [LICENSE](LICENSE) si vous en ajoutez un.

---

**Version** : 0.1.0
