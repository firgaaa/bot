# Architecture du Code

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Structure du projet](#structure-du-projet)
3. [Flux de données](#flux-de-données)
4. [Modules principaux](#modules-principaux)
5. [Gestion de la concurrence](#gestion-de-la-concurrence)
6. [Gestion des erreurs](#gestion-des-erreurs)
7. [Patterns utilisés](#patterns-utilisés)

---

## Vue d'ensemble

L'API est construite avec une architecture modulaire en Rust, utilisant :
- **Actix-web** : Framework web asynchrone
- **Diesel** : ORM pour PostgreSQL
- **Tokio** : Runtime asynchrone
- **Arc + Mutex** : Gestion de la concurrence

---

## Structure du projet

```
src/
├── main.rs                 # Point d'entrée, configuration serveur
├── api/                    # Couche API (endpoints)
│   ├── mod.rs             # Module API
│   ├── insert.rs          # POST /insert
│   ├── update.rs          # PUT /update
│   ├── generate.rs         # POST /generate
│   └── middleware.rs      # Middleware Basic Auth
├── database/               # Couche base de données
│   ├── mod.rs             # Fonctions DB (CRUD)
│   └── model.rs           # Modèles de données
├── errors.rs              # Types d'erreurs personnalisés
├── recheck.rs            # Vérification via API KFC
└── schema.rs             # Schéma Diesel (généré)
```

---

## Flux de données

### 1. Requête HTTP entrante

```
Client HTTP
    ↓
Actix-web Server
    ↓
BasicAuth Middleware (vérification credentials)
    ↓
Route Handler (insert/update/generate)
    ↓
Database Layer (Diesel)
    ↓
PostgreSQL
```

### 2. Flux POST /insert

```
1. Requête HTTP POST /insert
   ↓
2. Middleware BasicAuth vérifie les credentials
   ↓
3. Handler insert_kfc_account() parse le JSON
   ↓
4. database::insert_kfc_account() insère en DB
   ↓
5. Réponse 204 No Content
```

### 3. Flux PUT /update

```
1. Requête HTTP PUT /update
   ↓
2. Middleware BasicAuth vérifie les credentials
   ↓
3. Handler update_kfc_account() parse le JSON
   ↓
4. database::update_kfc_account() met à jour en DB
   ↓
5. Vérifie rows_affected (0 = 404, >0 = 204)
   ↓
6. Réponse 204 ou 404
```

### 4. Flux POST /generate (complexe)

```
1. Requête HTTP POST /generate
   ↓
2. Middleware BasicAuth vérifie les credentials
   ↓
3. Handler generate_kfc() valide min_points <= max_points
   ↓
4. database::model::generate_kfc_storage()
   ↓
   a. Transaction SQL :
      - Sélectionne jusqu'à 10 comptes candidats
      - Marque tous comme deja_send = true
   ↓
   b. Pour chaque compte :
      - Appelle recheck::recheck_kfc_accounts()
      - Vérifie customer_id et points
      - Si valide → retourne le compte
      - Si invalide → remet deja_send = false
   ↓
5. Réponse 200 (compte) ou 404 (aucun compte)
```

---

## Modules principaux

### main.rs

**Responsabilités** :
- Initialisation de l'application
- Configuration du serveur HTTP
- Connexion à la base de données
- Enregistrement des routes

**Points clés** :
```rust
// Connexion DB partagée avec Arc<Mutex<...>>
let db_pool = Arc::new(Mutex::new(db_pool));

// Middleware Basic Auth sur toutes les routes
.wrap(api::middleware::BasicAuth)

// Enregistrement des services
.service(api::insert::insert_kfc_account)
.service(api::update::update_kfc_account)
.service(api::generate::generate_kfc)
```

### api/middleware.rs

**Responsabilités** :
- Vérification Basic Auth
- Extraction des credentials depuis les headers
- Rejet des requêtes non authentifiées

**Fonctionnement** :
1. Lit `BASIC_AUTH_USER` et `BASIC_AUTH_PASSWORD` depuis les variables d'environnement
2. Décode le header `Authorization: Basic <token>`
3. Compare avec les credentials attendus
4. Autorise ou rejette la requête

### api/insert.rs

**Responsabilités** :
- Validation du JSON d'entrée
- Appel à la fonction DB d'insertion
- Gestion des erreurs

**Code clé** :
```rust
let new_account = new_account.into_inner();
match crate::database::insert_kfc_account(&mut conn, new_account).await {
    Ok(_) => HttpResponse::NoContent(),
    Err(e) => HttpResponse::InternalServerError(),
}
```

### api/update.rs

**Responsabilités** :
- Validation du JSON d'entrée
- Appel à la fonction DB de mise à jour
- Gestion des erreurs (404 si compte inexistant)

**Code clé** :
```rust
match crate::database::update_kfc_account(&mut conn, updated_account).await {
    Ok(_) => HttpResponse::NoContent(),
    Err(e) if e == diesel::result::Error::NotFound => {
        HttpResponse::NotFound()
    },
    Err(e) => HttpResponse::InternalServerError(),
}
```

### api/generate.rs

**Responsabilités** :
- Validation de `min_points <= max_points`
- Appel à la fonction de génération
- Gestion des réponses (200, 404, 500)

### database/mod.rs

**Responsabilités** :
- Connexion à PostgreSQL
- Fonctions CRUD de base
- Gestion des transactions

**Fonctions principales** :
- `establish_connection()` : Connexion à la DB
- `insert_kfc_account()` : Insertion
- `update_kfc_account()` : Mise à jour (avec vérification rows_affected)
- `get_old_kfc_accounts()` : Récupération (non utilisée actuellement)

### database/model.rs

**Responsabilités** :
- Définition des structures de données
- Logique métier complexe (generate_kfc_storage)

**Fonction principale** :
- `generate_kfc_storage()` : Logique de génération avec vérification KFC

### recheck.rs

**Responsabilités** :
- Appel HTTP à l'API KFC
- Validation des comptes en temps réel
- Gestion des timeouts

**Fonctionnement** :
```rust
pub async fn recheck_kfc_accounts(id: &str) -> Result<KfcResponse, AppError> {
    let client = wreq::Client::builder()
        .timeout(Duration::from_secs(5))
        .emulation(wreq_util::Emulation::random())
        .build()?;
    
    let url = format!("https://www.kfc.fr/api/users/{}/loyaltyinfo", id);
    let resp = client.get(&url).send().await?;
    // ...
}
```

### errors.rs

**Responsabilités** :
- Définition des types d'erreurs personnalisés
- Conversion automatique des erreurs

**Types d'erreurs** :
```rust
pub enum AppError {
    DatabaseError(diesel::result::Error),
    NotFound,
    HttpRequestError(wreq::Error),
    InvalidAccount,
    RecheckError(String),
    BadPoints,
    Unknown,
}
```

---

## Gestion de la concurrence

### Problème

Plusieurs requêtes HTTP peuvent arriver simultanément et accéder à la base de données.

### Solution

Utilisation de `Arc<Mutex<PgConnection>>` :

```rust
let db_pool = Arc::new(Mutex::new(db_pool));
```

**Arc** (Atomically Reference Counted) :
- Permet le partage de la connexion entre plusieurs threads
- Comptage de références automatique

**Mutex** (Mutual Exclusion) :
- Garantit qu'une seule requête accède à la DB à la fois
- Évite les conflits de données

**Limitation** : Cette approche limite le débit car toutes les requêtes sont sérialisées.

**Amélioration future** : Utiliser un pool de connexions (ex: `bb8` + `diesel-async`).

---

## Gestion des erreurs

### Stratégie

Utilisation de `Result<T, E>` et du type `AppError` personnalisé.

### Propagation

```rust
// Dans database/mod.rs
pub async fn update_kfc_account(...) -> Result<(), diesel::result::Error> {
    // ...
    if rows_affected == 0 {
        return Err(diesel::result::Error::NotFound);
    }
    Ok(())
}

// Dans api/update.rs
match crate::database::update_kfc_account(...).await {
    Ok(_) => HttpResponse::NoContent(),
    Err(e) if e == diesel::result::Error::NotFound => {
        HttpResponse::NotFound()
    },
    Err(e) => HttpResponse::InternalServerError(),
}
```

### Logging

Toutes les erreurs sont loggées :
- `log::error!()` : Erreurs critiques
- `log::warn!()` : Avertissements
- `log::info!()` : Informations
- `log::debug!()` : Détails de débogage

---

## Patterns utilisés

### 1. Repository Pattern

Les fonctions dans `database/mod.rs` encapsulent l'accès à la base de données.

### 2. Middleware Pattern

Le middleware Basic Auth intercepte toutes les requêtes avant les handlers.

### 3. Error Handling Pattern

Utilisation de `Result<T, E>` et `?` pour la propagation d'erreurs.

### 4. Builder Pattern

Utilisé par Actix-web pour construire l'application :
```rust
actix_web::App::new()
    .wrap(api::middleware::BasicAuth)
    .app_data(web::Data::new(db_pool.clone()))
    .service(api::insert::insert_kfc_account)
```

### 5. Dependency Injection

La connexion DB est injectée via `web::Data` dans les handlers.

---

## Améliorations possibles

### 1. Pool de connexions

Remplacer `Arc<Mutex<PgConnection>>` par un pool :
```rust
// Utiliser diesel-async avec bb8
let pool = Pool::new(...);
```

### 2. Validation des entrées

Ajouter une validation plus stricte des données JSON (ex: avec `validator`).

### 3. Rate limiting

Ajouter un middleware de rate limiting pour éviter les abus.

### 4. Caching

Mettre en cache les résultats de vérification KFC pour éviter les appels répétés.

### 5. Logging structuré

Utiliser un logging structuré (ex: `tracing`) pour une meilleure observabilité.

---

**Pour plus d'informations, consultez les autres sections de la documentation.**
