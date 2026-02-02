# Documentation Base de Données

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Schéma de la base de données](#schéma-de-la-base-de-données)
3. [Table kfc_storage](#table-kfc_storage)
4. [Migrations](#migrations)
5. [Triggers et fonctions](#triggers-et-fonctions)
6. [Contraintes](#contraintes)
7. [Index](#index)
8. [Modèles Rust](#modèles-rust)

---

## Vue d'ensemble

L'API utilise **PostgreSQL** comme base de données relationnelle. La gestion des schémas et migrations est assurée par **Diesel ORM**.

### Informations de connexion

- **Format URL** : `postgres://username:password@host:port/database`
- **Base par défaut** : `kfc_bot`
- **Port par défaut** : `5432`

---

## Schéma de la base de données

### Diagramme

```
┌─────────────────────────────────────┐
│         kfc_storage                 │
├─────────────────────────────────────┤
│ PK  id              VARCHAR(255)    │
│     created_at      TIMESTAMP      │
│     updated_at      TIMESTAMP      │
│     carte           VARCHAR(6)      │ (UNIQUE)
│     deja_send       BOOLEAN        │
│     status          VARCHAR(50)    │
│     customer_id     VARCHAR(255)   │
│     email           VARCHAR(255)   │
│     password        VARCHAR(255)   │
│     nom             VARCHAR(255)   │
│     point           INT            │
│     expired_at      TIMESTAMP      │
└─────────────────────────────────────┘
```

---

## Table kfc_storage

### Description

Table principale stockant tous les comptes KFC avec leurs informations.

### Colonnes

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `VARCHAR(255)` | **PRIMARY KEY**, NOT NULL | Identifiant unique du compte |
| `created_at` | `TIMESTAMP` | NULLABLE, DEFAULT CURRENT_TIMESTAMP | Date de création |
| `updated_at` | `TIMESTAMP` | NULLABLE, DEFAULT CURRENT_TIMESTAMP | Date de dernière mise à jour |
| `carte` | `VARCHAR(6)` | **UNIQUE**, NOT NULL | Numéro de carte (6 caractères) |
| `deja_send` | `BOOLEAN` | NULLABLE, DEFAULT FALSE | Indique si le compte a été "vendu" |
| `status` | `VARCHAR(50)` | NULLABLE, DEFAULT 'alive' | Statut du compte ('alive' ou 'expired') |
| `customer_id` | `VARCHAR(255)` | NULLABLE | ID client KFC |
| `email` | `VARCHAR(255)` | NULLABLE | Email du compte |
| `password` | `VARCHAR(255)` | NULLABLE | Mot de passe du compte |
| `nom` | `VARCHAR(255)` | NULLABLE | Nom du propriétaire |
| `point` | `INT` | NULLABLE, DEFAULT 0, CHECK >= 0 | Points fidélité |
| `expired_at` | `TIMESTAMP` | NULLABLE | Date d'expiration |

### Contraintes

1. **PRIMARY KEY** : `id`
2. **UNIQUE** : `carte`
3. **CHECK** : `point >= 0`
4. **CHECK** : `status IN ('alive', 'expired')`

---

## Migrations

Les migrations sont gérées par Diesel et se trouvent dans le dossier `migrations/`.

### Liste des migrations

1. **2026-01-12-171845-0000_create_table**
   - Crée la table `kfc_storage` avec la colonne `id` (PRIMARY KEY)

2. **2026-01-12-172404-0000_alter_table**
   - Ajoute toutes les colonnes supplémentaires
   - Définit les contraintes (UNIQUE, CHECK)
   - Définit les valeurs par défaut

3. **2026-01-12-173640-0000_update_trigger**
   - Crée la fonction `set_updated_at()`
   - Crée le trigger `trg_updated_at` pour mettre à jour automatiquement `updated_at`

4. **2026-01-16-140716-0000_insert_1K6_kfc**
   - Migration de données (actuellement vide)

### Commandes de migration

```bash
# Appliquer toutes les migrations
diesel migration run

# Annuler la dernière migration
diesel migration revert

# Créer une nouvelle migration
diesel migration generate nom_de_la_migration

# Réinitialiser la base (⚠️ Supprime toutes les données)
diesel database reset
```

---

## Triggers et fonctions

### Fonction set_updated_at()

Fonction PL/pgSQL qui met à jour automatiquement le champ `updated_at`.

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger trg_updated_at

Trigger qui appelle `set_updated_at()` avant chaque UPDATE sur `kfc_storage`.

```sql
CREATE TRIGGER trg_updated_at
BEFORE UPDATE ON kfc_storage
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
```

**Comportement** : À chaque mise à jour d'une ligne, le champ `updated_at` est automatiquement mis à jour avec la date/heure actuelle.

---

## Contraintes

### Contraintes de domaine

1. **point >= 0**
   - Les points ne peuvent pas être négatifs

2. **status IN ('alive', 'expired')**
   - Le statut doit être soit 'alive' soit 'expired'

### Contraintes d'unicité

1. **PRIMARY KEY sur id**
   - Chaque compte doit avoir un `id` unique

2. **UNIQUE sur carte**
   - Chaque numéro de carte doit être unique

### Contraintes de référence

Aucune contrainte de clé étrangère pour le moment.

---

## Index

### Index automatiques

PostgreSQL crée automatiquement des index pour :
- **PRIMARY KEY** : `id` (index unique)
- **UNIQUE** : `carte` (index unique)

### Index recommandés (futurs)

Pour améliorer les performances des requêtes de `/generate`, on pourrait ajouter :

```sql
CREATE INDEX idx_kfc_storage_point ON kfc_storage(point);
CREATE INDEX idx_kfc_storage_status ON kfc_storage(status);
CREATE INDEX idx_kfc_storage_deja_send ON kfc_storage(deja_send);
CREATE INDEX idx_kfc_storage_composite ON kfc_storage(point, status, deja_send);
```

---

## Modèles Rust

### AddKfcStorage

Structure pour l'insertion d'un compte.

```rust
pub struct AddKfcStorage {
    id: String,
    carte: String,
    customer_id: Option<String>,
    email: Option<String>,
    password: Option<String>,
    nom: Option<String>,
    point: i32,
    expired_at: Option<chrono::NaiveDateTime>,
}
```

**Utilisation** : Endpoint `POST /insert`

### UpdateKfcStorage

Structure pour la mise à jour d'un compte (tous les champs sauf `id` sont optionnels).

```rust
pub struct UpdateKfcStorage {
    pub id: String,
    pub carte: Option<String>,
    pub customer_id: Option<String>,
    pub email: Option<String>,
    pub password: Option<String>,
    pub nom: Option<String>,
    pub point: Option<i32>,
    pub expired_at: Option<chrono::NaiveDateTime>,
}
```

**Utilisation** : Endpoint `PUT /update`

### Kfc

Structure pour la lecture d'un compte (utilisée dans `/generate`).

```rust
pub struct Kfc {
    id: String,
    customer_id: Option<String>,
    carte: String,
    point: Option<i32>,
    expired_at: Option<chrono::NaiveDateTime>,
}
```

**Utilisation** : Endpoint `POST /generate` (réponse)

---

## Requêtes SQL utiles

### Vérifier la structure de la table

```sql
\d kfc_storage
```

### Compter les comptes par statut

```sql
SELECT status, COUNT(*) 
FROM kfc_storage 
GROUP BY status;
```

### Compter les comptes disponibles

```sql
SELECT COUNT(*) 
FROM kfc_storage 
WHERE status != 'expired' 
  AND (deja_send IS NULL OR deja_send = false);
```

### Trouver les comptes dans une fourchette de points

```sql
SELECT * 
FROM kfc_storage 
WHERE point BETWEEN 100 AND 1000
  AND status != 'expired'
  AND (deja_send IS NULL OR deja_send = false)
LIMIT 10;
```

### Vérifier les comptes expirés

```sql
SELECT id, carte, point, expired_at 
FROM kfc_storage 
WHERE status = 'expired' 
  OR expired_at < NOW();
```

### Nettoyer les comptes de test

```sql
DELETE FROM kfc_storage 
WHERE id LIKE 'test_%';
```

---

## Maintenance

### Sauvegarde

```bash
# Sauvegarder la base
pg_dump -U postgres kfc_bot > backup.sql

# Restaurer la base
psql -U postgres kfc_bot < backup.sql
```

### Analyse des performances

```sql
-- Analyser la table
ANALYZE kfc_storage;

-- Vérifier les statistiques
SELECT * FROM pg_stats WHERE tablename = 'kfc_storage';
```

### Nettoyage

```sql
-- Supprimer les comptes expirés depuis plus de 30 jours
DELETE FROM kfc_storage 
WHERE status = 'expired' 
  AND updated_at < NOW() - INTERVAL '30 days';
```

---

## Sécurité

### ⚠️ Points d'attention

1. **Mots de passe en clair** : Les mots de passe sont stockés en clair dans la base
   - **Recommandation** : Utiliser un hash (bcrypt, argon2) si nécessaire

2. **Données sensibles** : Email, password, customer_id sont stockés en clair
   - **Recommandation** : Chiffrer les données sensibles si nécessaire

3. **Accès à la base** : Limiter l'accès à la base de données
   - **Recommandation** : Utiliser un utilisateur dédié avec des permissions minimales

---

## Schéma Diesel

Le schéma Diesel est généré automatiquement dans `src/schema.rs` :

```rust
diesel::table! {
    kfc_storage (id) {
        id -> Varchar,
        created_at -> Nullable<Timestamp>,
        updated_at -> Nullable<Timestamp>,
        carte -> Varchar,
        deja_send -> Nullable<Bool>,
        status -> Nullable<Varchar>,
        customer_id -> Nullable<Varchar>,
        email -> Nullable<Varchar>,
        password -> Nullable<Varchar>,
        nom -> Nullable<Varchar>,
        point -> Nullable<Int4>,
        expired_at -> Nullable<Timestamp>,
    }
}
```

**Note** : Ce fichier est généré automatiquement par Diesel. Ne pas modifier manuellement.

---

**Pour plus d'informations sur l'architecture, consultez [ARCHITECTURE.md](./ARCHITECTURE.md)**
