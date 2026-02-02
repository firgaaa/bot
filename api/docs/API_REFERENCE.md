# Référence API complète

## Table des matières

1. [Authentification](#authentification)
2. [Endpoints](#endpoints)
   - [POST /insert](#post-insert)
   - [PUT /update](#put-update)
   - [POST /generate](#post-generate)
3. [Codes de statut HTTP](#codes-de-statut-http)
4. [Gestion des erreurs](#gestion-des-erreurs)
5. [Exemples de requêtes](#exemples-de-requêtes)

---

## Authentification

Tous les endpoints de l'API nécessitent une **authentification Basic Auth**.

### Format

```
Authorization: Basic <base64(username:password)>
```

### Exemple

```bash
# Credentials: username=votre_username, password=votre_mot_de_passe
# Token: base64("votre_username:votre_mot_de_passe")
Authorization: Basic Y2xlbXNlcl86Q2xlbXNlcjI5MDMh
```

### Configuration

Les credentials sont définis dans le fichier `.env` :

```env
BASIC_AUTH_USER=votre_username
BASIC_AUTH_PASSWORD=votre_mot_de_passe
```

### Réponses d'authentification

| Code | Description |
|------|-------------|
| `401 Unauthorized` | Credentials manquants ou incorrects |
| `401 Unauthorized` | Variables d'environnement non configurées |

---

## Endpoints

### POST /insert

Insère un nouveau compte KFC dans la base de données.

#### Requête

**URL** : `http://localhost:8080/insert`  
**Méthode** : `POST`  
**Headers** :
```
Authorization: Basic <token>
Content-Type: application/json
```

**Body** (JSON) :
```json
{
  "id": "string" (requis, unique),
  "carte": "string" (requis, 6 caractères, unique),
  "customer_id": "string" (optionnel),
  "email": "string" (optionnel),
  "password": "string" (optionnel),
  "nom": "string" (optionnel),
  "point": integer (requis, >= 0),
  "expired_at": "datetime" (optionnel, format ISO 8601)
}
```

#### Exemple de requête

```json
{
  "id": "kfc_account_001",
  "carte": "123456",
  "customer_id": "customer_123",
  "email": "user@example.com",
  "password": "password123",
  "nom": "John Doe",
  "point": 500,
  "expired_at": null
}
```

#### Réponses

| Code | Description | Body |
|------|-------------|------|
| `204 No Content` | Compte inséré avec succès | (vide) |
| `401 Unauthorized` | Authentification requise/échouée | `"Unauthorized"` |
| `500 Internal Server Error` | Erreur (doublon, contrainte DB, etc.) | `"Failed to insert KFC account"` |

#### Exemple de réponse (204)

```
HTTP/1.1 204 No Content
```

#### Erreurs possibles

- **500** : `id` ou `carte` déjà existant (contrainte unique)
- **500** : `point` négatif (contrainte CHECK)
- **500** : Connexion à la base de données perdue

---

### PUT /update

Met à jour un compte KFC existant. Tous les champs sauf `id` sont optionnels.

#### Requête

**URL** : `http://localhost:8080/update`  
**Méthode** : `PUT`  
**Headers** :
```
Authorization: Basic <token>
Content-Type: application/json
```

**Body** (JSON) :
```json
{
  "id": "string" (requis),
  "carte": "string" (optionnel),
  "customer_id": "string" (optionnel),
  "email": "string" (optionnel),
  "password": "string" (optionnel),
  "nom": "string" (optionnel),
  "point": integer (optionnel, >= 0),
  "expired_at": "datetime" (optionnel, format ISO 8601)
}
```

#### Exemple de requête

```json
{
  "id": "kfc_account_001",
  "point": 750,
  "email": "updated@example.com",
  "nom": "Updated Name"
}
```

#### Réponses

| Code | Description | Body |
|------|-------------|------|
| `204 No Content` | Compte mis à jour avec succès | (vide) |
| `401 Unauthorized` | Authentification requise/échouée | `"Unauthorized"` |
| `404 Not Found` | Compte inexistant | `"KFC account not found"` |
| `500 Internal Server Error` | Erreur base de données | `"Failed to update KFC account"` |

#### Exemple de réponse (204)

```
HTTP/1.1 204 No Content
```

#### Exemple de réponse (404)

```
HTTP/1.1 404 Not Found
Content-Type: text/plain

KFC account not found
```

#### Comportement

- Seuls les champs fournis dans le JSON sont mis à jour
- Les champs non fournis restent inchangés
- Le champ `updated_at` est automatiquement mis à jour par un trigger SQL

---

### POST /generate

Trouve un compte disponible dans une fourchette de points, le vérifie via l'API KFC, et le marque comme vendu.

#### Requête

**URL** : `http://localhost:8080/generate`  
**Méthode** : `POST`  
**Headers** :
```
Authorization: Basic <token>
Content-Type: application/json
```

**Body** (JSON) :
```json
{
  "min_points": integer (requis),
  "max_points": integer (requis)
}
```

**Contraintes** :
- `min_points` doit être <= `max_points`
- `min_points` >= 0
- `max_points` >= 0

#### Exemple de requête

```json
{
  "min_points": 100,
  "max_points": 1000
}
```

#### Réponses

| Code | Description | Body |
|------|-------------|------|
| `200 OK` | Compte trouvé et validé | JSON du compte |
| `400 Bad Request` | `min_points > max_points` | `"min_points cannot be greater than max_points"` |
| `401 Unauthorized` | Authentification requise/échouée | `"Unauthorized"` |
| `404 Not Found` | Aucun compte disponible | `"No KFC account found in the specified point range"` |
| `500 Internal Server Error` | Erreur serveur | `"Failed to generate KFC account"` |

#### Exemple de réponse (200)

```json
{
  "id": "kfc_account_001",
  "customerId": "customer_123",
  "carte": "123456",
  "point": 500,
  "expiredAt": null
}
```

#### Exemple de réponse (404)

```
HTTP/1.1 404 Not Found
Content-Type: text/plain

No KFC account found in the specified point range
```

#### Logique interne

1. **Sélection** : Sélectionne jusqu'à 10 comptes correspondant aux critères :
   - `point` entre `min_points` et `max_points`
   - `status != "expired"`
   - `deja_send = false` ou `NULL`

2. **Réservation** : Marque temporairement ces comptes comme vendus (`deja_send = true`) en transaction

3. **Vérification** : Pour chaque compte réservé :
   - Appelle l'API KFC : `https://www.kfc.fr/api/users/{id}/loyaltyinfo`
   - Si l'appel échoue → remet `deja_send = false` et continue
   - Si `customer_id` a changé → met `status = "expired"` et continue
   - Si les points réels sont hors fourchette → remet `deja_send = false`, met à jour `point`, et continue

4. **Résultat** : Retourne le premier compte valide

5. **Nettoyage** : Remet `deja_send = false` pour les autres comptes réservés

#### Timeout

- Timeout de 5 secondes pour chaque appel à l'API KFC
- Timeout total recommandé : 30 secondes pour la requête complète

---

## Codes de statut HTTP

| Code | Signification | Endpoints concernés |
|------|---------------|---------------------|
| `200 OK` | Succès avec données | `/generate` (compte trouvé) |
| `204 No Content` | Succès sans données | `/insert`, `/update` |
| `400 Bad Request` | Requête invalide | `/generate` (validation) |
| `401 Unauthorized` | Authentification requise/échouée | Tous |
| `404 Not Found` | Ressource introuvable | `/update` (compte inexistant), `/generate` (aucun compte) |
| `500 Internal Server Error` | Erreur serveur | Tous (erreurs DB, API KFC, etc.) |

---

## Gestion des erreurs

### Format des erreurs

Les erreurs sont retournées sous forme de texte brut dans le body de la réponse.

### Types d'erreurs

1. **Erreurs d'authentification** (`401`)
   - Credentials manquants
   - Credentials incorrects
   - Configuration serveur manquante

2. **Erreurs de validation** (`400`)
   - `min_points > max_points` dans `/generate`
   - JSON invalide

3. **Erreurs de ressources** (`404`)
   - Compte inexistant dans `/update`
   - Aucun compte disponible dans `/generate`

4. **Erreurs serveur** (`500`)
   - Erreurs de base de données (contraintes, connexion)
   - Erreurs lors de l'appel à l'API KFC
   - Erreurs internes

### Logs

Toutes les erreurs sont loggées côté serveur avec le niveau approprié :
- `ERROR` : Erreurs critiques
- `WARN` : Avertissements (comptes invalides, etc.)
- `INFO` : Informations générales
- `DEBUG` : Détails de débogage

---

## Exemples de requêtes

### cURL

#### POST /insert

```bash
curl -X POST http://localhost:8080/insert \
  -H "Authorization: Basic Y2xlbXNlcl86Q2xlbXNlcjI5MDMh" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_001",
    "carte": "123456",
    "point": 500,
    "customer_id": "cust_123",
    "email": "test@example.com"
  }'
```

#### PUT /update

```bash
curl -X PUT http://localhost:8080/update \
  -H "Authorization: Basic Y2xlbXNlcl86Q2xlbXNlcjI5MDMh" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_001",
    "point": 750
  }'
```

#### POST /generate

```bash
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Basic Y2xlbXNlcl86Q2xlbXNlcjI5MDMh" \
  -H "Content-Type: application/json" \
  -d '{
    "min_points": 100,
    "max_points": 1000
  }'
```

### Python (requests)

```python
import requests
import base64

BASE_URL = "http://localhost:8080"
USERNAME = "votre_username"
PASSWORD = "votre_mot_de_passe"

# Générer le token Basic Auth
credentials = f"{USERNAME}:{PASSWORD}"
token = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

# POST /insert
response = requests.post(
    f"{BASE_URL}/insert",
    json={
        "id": "test_001",
        "carte": "123456",
        "point": 500
    },
    headers=headers
)
print(f"Status: {response.status_code}")

# PUT /update
response = requests.put(
    f"{BASE_URL}/update",
    json={
        "id": "test_001",
        "point": 750
    },
    headers=headers
)
print(f"Status: {response.status_code}")

# POST /generate
response = requests.post(
    f"{BASE_URL}/generate",
    json={
        "min_points": 100,
        "max_points": 1000
    },
    headers=headers,
    timeout=30
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Compte: {response.json()}")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8080";
const USERNAME = "votre_username";
const PASSWORD = "votre_mot_de_passe";

// Générer le token Basic Auth
const token = btoa(`${USERNAME}:${PASSWORD}`);
const headers = {
  "Authorization": `Basic ${token}`,
  "Content-Type": "application/json"
};

// POST /insert
fetch(`${BASE_URL}/insert`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    id: "test_001",
    carte: "123456",
    point: 500
  })
})
  .then(response => console.log(`Status: ${response.status}`));

// PUT /update
fetch(`${BASE_URL}/update`, {
  method: "PUT",
  headers: headers,
  body: JSON.stringify({
    id: "test_001",
    point: 750
  })
})
  .then(response => console.log(`Status: ${response.status}`));

// POST /generate
fetch(`${BASE_URL}/generate`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    min_points: 100,
    max_points: 1000
  })
})
  .then(response => response.json())
  .then(data => console.log("Compte:", data))
  .catch(error => console.error("Erreur:", error));
```

---

## Notes importantes

1. **Performance** : L'endpoint `/generate` peut prendre jusqu'à 30 secondes car il fait des appels HTTP à l'API KFC
2. **Transactions** : Les opérations de génération utilisent des transactions SQL pour garantir la cohérence
3. **Concurrence** : L'API utilise un `Mutex` pour gérer l'accès concurrent à la base de données
4. **Validation** : Les comptes sont validés en temps réel via l'API KFC avant d'être marqués comme vendus

---

**Pour plus d'exemples, consultez [EXAMPLES.md](./EXAMPLES.md)**
