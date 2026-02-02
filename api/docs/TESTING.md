# Guide de Test

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Script de test Python](#script-de-test-python)
3. [Tests manuels](#tests-manuels)
4. [Tests d'intégration](#tests-dintégration)
5. [Validation des résultats](#validation-des-résultats)

---

## Vue d'ensemble

L'API dispose d'un script de test complet (`teste_api.py`) qui teste tous les endpoints avec tous les types d'erreurs possibles.

### Objectifs des tests

- ✅ Vérifier que tous les endpoints fonctionnent correctement
- ✅ Tester tous les cas d'erreur (401, 404, 400, 500)
- ✅ Valider l'authentification
- ✅ Détecter les anomalies de comportement

---

## Script de test Python

### Installation

```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :
```
requests>=2.31.0
```

### Configuration

Modifier les credentials dans `teste_api.py` :

```python
BASE_URL = "http://localhost:8080"
USERNAME = "votre_username"  # Ton BASIC_AUTH_USER
PASSWORD = "votre_mot_de_passe"  # Ton BASIC_AUTH_PASSWORD
```

### Exécution

```bash
python teste_api.py
```

### Résultats attendus

```
======================================================================
  TESTS DE L'API clemser_kfc_api
======================================================================
URL de base: http://localhost:8080
Username: votre_username
Date: 2026-01-26 22:08:45

======================================================================
  TESTS POST /insert
======================================================================
[OK] POST /insert - Succès
   Attendu: 204, Reçu: 204
[OK] POST /insert - Duplicate (500 attendu)
   Attendu: 500, Reçu: 500
[OK] POST /insert - Sans auth (401)
   Attendu: 401, Reçu: 401
[OK] POST /insert - Mauvais credentials (401)
   Attendu: 401, Reçu: 401

======================================================================
  TESTS PUT /update
======================================================================
[OK] PUT /update - Succès
   Attendu: 204, Reçu: 204
[OK] PUT /update - Not Found (404)
   Attendu: 404, Reçu: 404
[OK] PUT /update - Sans auth (401)
   Attendu: 401, Reçu: 401

======================================================================
  TESTS POST /generate
======================================================================
[OK] POST /generate - Not Found (404) - Aucun compte disponible
   (Comportement normal si la base est vide)
[OK] POST /generate - Bad Request (400)
   Attendu: 400, Reçu: 400
[OK] POST /generate - Sans auth (401)
   Attendu: 401, Reçu: 401
[OK] POST /generate - JSON invalide (400/422/500)
   Attendu: 400, Reçu: 400

======================================================================
  RAPPORT FINAL
======================================================================
Total de tests: 11
[OK] Tests reussis: 11
[FAIL] Tests echoues: 0
[INFO] Taux de reussite: 100.0%

[OK] AUCUNE ANOMALIE DETECTEE - Tous les tests sont passes!
```

### Tests effectués

#### POST /insert (4 tests)

1. **Succès (204)** : Insertion d'un compte valide
2. **Duplicate (500)** : Tentative d'insertion d'un doublon
3. **Sans auth (401)** : Requête sans authentification
4. **Mauvais credentials (401)** : Requête avec mauvais credentials

#### PUT /update (3 tests)

1. **Succès (204)** : Mise à jour d'un compte existant
2. **Not Found (404)** : Mise à jour d'un compte inexistant
3. **Sans auth (401)** : Requête sans authentification

#### POST /generate (4 tests)

1. **Succès/Not Found (200/404)** : Génération selon disponibilité
2. **Bad Request (400)** : `min_points > max_points`
3. **Sans auth (401)** : Requête sans authentification
4. **JSON invalide (400)** : Requête avec JSON malformé

---

## Tests manuels

### 1. Test de connexion

```bash
# Vérifier que l'API répond
curl http://localhost:8080/generate
# Doit retourner 401 (pas d'auth)
```

### 2. Test d'authentification

```bash
# Générer le token
TOKEN=$(echo -n "votre_username:votre_mot_de_passe" | base64)

# Tester avec authentification
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 100, "max_points": 1000}'
```

### 3. Test POST /insert

```bash
curl -X POST http://localhost:8080/insert \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_manual",
    "carte": "999999",
    "point": 500
  }'
# Doit retourner 204
```

### 4. Test PUT /update

```bash
# Mettre à jour
curl -X PUT http://localhost:8080/update \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_manual",
    "point": 750
  }'
# Doit retourner 204

# Tester avec compte inexistant
curl -X PUT http://localhost:8080/update \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "nonexistent",
    "point": 999
  }'
# Doit retourner 404
```

### 5. Test POST /generate

```bash
# Test avec fourchette valide
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 0, "max_points": 10000}'
# Doit retourner 200 ou 404

# Test avec fourchette invalide
curl -X POST http://localhost:8080/generate \
  -H "Authorization: Basic $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 1000, "max_points": 100}'
# Doit retourner 400
```

---

## Tests d'intégration

### Scénario complet

```python
import requests
import base64
import time

BASE_URL = "http://localhost:8080"
USERNAME = "votre_username"
PASSWORD = "votre_mot_de_passe"

token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

# 1. Préparer des données de test
test_id = f"integration_test_{int(time.time())}"

# 2. Insérer un compte
print("1. Insertion...")
response = requests.post(
    f"{BASE_URL}/insert",
    json={
        "id": test_id,
        "carte": "888888",
        "point": 500,
        "email": "test@example.com"
    },
    headers=headers
)
assert response.status_code == 204, f"Insert échoué: {response.status_code}"
print("   ✅ Insertion réussie")

# 3. Mettre à jour le compte
print("2. Mise à jour...")
response = requests.put(
    f"{BASE_URL}/update",
    json={
        "id": test_id,
        "point": 750
    },
    headers=headers
)
assert response.status_code == 204, f"Update échoué: {response.status_code}"
print("   ✅ Mise à jour réussie")

# 4. Générer un compte (peut ne pas trouver celui qu'on vient d'insérer car deja_send)
print("3. Génération...")
response = requests.post(
    f"{BASE_URL}/generate",
    json={"min_points": 0, "max_points": 10000},
    headers=headers,
    timeout=30
)
assert response.status_code in [200, 404], f"Generate échoué: {response.status_code}"
if response.status_code == 200:
    account = response.json()
    print(f"   ✅ Compte généré: {account['id']}")
else:
    print("   ℹ️  Aucun compte disponible")

# 5. Nettoyage (optionnel)
# Supprimer le compte de test depuis la base de données

print("\n✅ Tous les tests d'intégration sont passés!")
```

---

## Validation des résultats

### Codes de statut attendus

| Endpoint | Cas | Code attendu |
|----------|-----|--------------|
| POST /insert | Succès | 204 |
| POST /insert | Doublon | 500 |
| POST /insert | Sans auth | 401 |
| PUT /update | Succès | 204 |
| PUT /update | Compte inexistant | 404 |
| PUT /update | Sans auth | 401 |
| POST /generate | Compte trouvé | 200 |
| POST /generate | Aucun compte | 404 |
| POST /generate | min > max | 400 |
| POST /generate | Sans auth | 401 |

### Validation des données

#### POST /insert

- ✅ Le compte doit être inséré dans la base
- ✅ `created_at` et `updated_at` doivent être définis
- ✅ `deja_send` doit être `false` par défaut
- ✅ `status` doit être `'alive'` par défaut

#### PUT /update

- ✅ Seuls les champs fournis doivent être mis à jour
- ✅ `updated_at` doit être mis à jour automatiquement
- ✅ Les autres champs doivent rester inchangés

#### POST /generate

- ✅ Le compte retourné doit avoir des points dans la fourchette
- ✅ Le compte doit être marqué comme `deja_send = true`
- ✅ Le compte doit être valide (vérifié via API KFC)

---

## Dépannage des tests

### Erreur : "Impossible de se connecter à l'API"

**Cause** : L'API n'est pas démarrée

**Solution** :
```bash
# Vérifier que l'API tourne
cargo run

# Dans un autre terminal, relancer les tests
python teste_api.py
```

### Erreur : "401 Unauthorized" sur tous les tests

**Cause** : Mauvais credentials dans le script

**Solution** :
1. Vérifier les credentials dans `.env` de l'API
2. Mettre à jour `USERNAME` et `PASSWORD` dans `teste_api.py`

### Erreur : "404 Not Found" sur PUT /update

**Cause** : Le test précédent n'a pas créé de compte

**Solution** : Vérifier que le test `POST /insert - Succès` a réussi

### Erreur : Timeout sur POST /generate

**Cause** : L'API KFC met trop de temps à répondre

**Solution** : Augmenter le timeout dans le script (actuellement 30s)

---

## Tests de charge (optionnel)

### Script simple

```python
import requests
import base64
import concurrent.futures
import time

BASE_URL = "http://localhost:8080"
USERNAME = "votre_username"
PASSWORD = "votre_mot_de_passe"

token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

def test_generate():
    response = requests.post(
        f"{BASE_URL}/generate",
        json={"min_points": 0, "max_points": 10000},
        headers=headers,
        timeout=30
    )
    return response.status_code

# Tester avec 10 requêtes simultanées
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_generate) for _ in range(10)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

end = time.time()
print(f"10 requêtes en {end - start:.2f} secondes")
print(f"Résultats: {results}")
```

---

## Conclusion

Le script `teste_api.py` fournit une couverture complète des tests pour l'API. Il est recommandé de l'exécuter :

- ✅ Avant chaque déploiement
- ✅ Après chaque modification du code
- ✅ Régulièrement pour vérifier que l'API fonctionne correctement

---

**Pour plus d'informations, consultez [API_REFERENCE.md](./API_REFERENCE.md)**
