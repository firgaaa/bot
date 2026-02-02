# Exemples d'utilisation

## Table des matières

1. [cURL](#curl)
2. [Python](#python)
3. [JavaScript/Node.js](#javascriptnodejs)
4. [Rust](#rust)
5. [PowerShell](#powershell)
6. [Scénarios complets](#scénarios-complets)

---

## cURL

### Configuration

```bash
# Définir les variables
BASE_URL="http://localhost:8080"
USERNAME="votre_username"
PASSWORD="votre_mot_de_passe"

# Générer le token Basic Auth
AUTH_TOKEN=$(echo -n "${USERNAME}:${PASSWORD}" | base64)
```

### POST /insert

```bash
curl -X POST "${BASE_URL}/insert" \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "kfc_001",
    "carte": "123456",
    "customer_id": "customer_123",
    "email": "user@example.com",
    "password": "password123",
    "nom": "John Doe",
    "point": 500,
    "expired_at": null
  }'
```

### PUT /update

```bash
curl -X PUT "${BASE_URL}/update" \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "kfc_001",
    "point": 750,
    "email": "updated@example.com"
  }'
```

### POST /generate

```bash
curl -X POST "${BASE_URL}/generate" \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "min_points": 100,
    "max_points": 1000
  }' \
  --max-time 30
```

### Gestion des erreurs

```bash
# Tester sans authentification (doit retourner 401)
curl -X POST "${BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 100, "max_points": 1000}'

# Vérifier le code de statut
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "${BASE_URL}/generate" \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"min_points": 100, "max_points": 1000}')

echo "Code HTTP: ${HTTP_CODE}"
```

---

## Python

### Installation

```bash
pip install requests
```

### Classe API complète

```python
import requests
import base64
from typing import Optional, Dict, Any

class KfcAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self._auth_token = self._generate_auth_token()
        self._headers = {
            "Authorization": f"Basic {self._auth_token}",
            "Content-Type": "application/json"
        }
    
    def _generate_auth_token(self) -> str:
        credentials = f"{self.username}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()
    
    def insert_account(self, account_data: Dict[str, Any]) -> requests.Response:
        """Insère un nouveau compte KFC"""
        return requests.post(
            f"{self.base_url}/insert",
            json=account_data,
            headers=self._headers,
            timeout=10
        )
    
    def update_account(self, account_id: str, updates: Dict[str, Any]) -> requests.Response:
        """Met à jour un compte existant"""
        payload = {"id": account_id, **updates}
        return requests.put(
            f"{self.base_url}/update",
            json=payload,
            headers=self._headers,
            timeout=10
        )
    
    def generate_account(self, min_points: int, max_points: int) -> Optional[Dict[str, Any]]:
        """Génère/trouve un compte disponible"""
        response = requests.post(
            f"{self.base_url}/generate",
            json={"min_points": min_points, "max_points": max_points},
            headers=self._headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()

# Utilisation
api = KfcAPI(
    base_url="http://localhost:8080",
    username="votre_username",
    password="votre_mot_de_passe"
)

# Insérer un compte
response = api.insert_account({
    "id": "kfc_001",
    "carte": "123456",
    "point": 500,
    "email": "user@example.com"
})
print(f"Insert: {response.status_code}")

# Mettre à jour
response = api.update_account("kfc_001", {"point": 750})
print(f"Update: {response.status_code}")

# Générer un compte
account = api.generate_account(100, 1000)
if account:
    print(f"Compte trouvé: {account}")
else:
    print("Aucun compte disponible")
```

### Exemple simple

```python
import requests
import base64

BASE_URL = "http://localhost:8080"
USERNAME = "votre_username"
PASSWORD = "votre_mot_de_passe"

# Générer le token
token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
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
    json={"min_points": 100, "max_points": 1000},
    headers=headers,
    timeout=30
)
if response.status_code == 200:
    print(f"Compte: {response.json()}")
```

---

## JavaScript/Node.js

### Installation

```bash
npm install axios
# ou
npm install node-fetch
```

### Avec axios

```javascript
const axios = require('axios');
const base64 = require('base-64');

const BASE_URL = 'http://localhost:8080';
const USERNAME = 'votre_username';
const PASSWORD = 'votre_mot_de_passe';

// Générer le token
const token = base64.encode(`${USERNAME}:${PASSWORD}`);
const headers = {
  'Authorization': `Basic ${token}`,
  'Content-Type': 'application/json'
};

// POST /insert
axios.post(`${BASE_URL}/insert`, {
  id: 'kfc_001',
  carte: '123456',
  point: 500,
  email: 'user@example.com'
}, { headers })
  .then(response => console.log('Insert:', response.status))
  .catch(error => console.error('Erreur:', error.response?.status));

// PUT /update
axios.put(`${BASE_URL}/update`, {
  id: 'kfc_001',
  point: 750
}, { headers })
  .then(response => console.log('Update:', response.status))
  .catch(error => console.error('Erreur:', error.response?.status));

// POST /generate
axios.post(`${BASE_URL}/generate`, {
  min_points: 100,
  max_points: 1000
}, { headers, timeout: 30000 })
  .then(response => {
    if (response.status === 200) {
      console.log('Compte:', response.data);
    }
  })
  .catch(error => {
    if (error.response?.status === 404) {
      console.log('Aucun compte disponible');
    } else {
      console.error('Erreur:', error.message);
    }
  });
```

### Avec fetch (Node.js 18+)

```javascript
const BASE_URL = 'http://localhost:8080';
const USERNAME = 'votre_username';
const PASSWORD = 'votre_mot_de_passe';

// Générer le token
const token = Buffer.from(`${USERNAME}:${PASSWORD}`).toString('base64');
const headers = {
  'Authorization': `Basic ${token}`,
  'Content-Type': 'application/json'
};

// POST /insert
fetch(`${BASE_URL}/insert`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    id: 'kfc_001',
    carte: '123456',
    point: 500
  })
})
  .then(response => console.log('Status:', response.status));

// POST /generate
fetch(`${BASE_URL}/generate`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    min_points: 100,
    max_points: 1000
  })
})
  .then(async response => {
    if (response.status === 200) {
      const data = await response.json();
      console.log('Compte:', data);
    } else if (response.status === 404) {
      console.log('Aucun compte disponible');
    }
  });
```

---

## Rust

### Exemple avec reqwest

```toml
# Cargo.toml
[dependencies]
reqwest = { version = "0.11", features = ["json"] }
tokio = { version = "1", features = ["full"] }
base64 = "0.22"
```

```rust
use reqwest::Client;
use base64::{Engine as _, engine::general_purpose};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let base_url = "http://localhost:8080";
    let username = "votre_username";
    let password = "votre_mot_de_passe";
    
    // Générer le token
    let credentials = format!("{}:{}", username, password);
    let token = general_purpose::STANDARD.encode(credentials);
    let auth_header = format!("Basic {}", token);
    
    let client = Client::new();
    
    // POST /insert
    let response = client
        .post(&format!("{}/insert", base_url))
        .header("Authorization", &auth_header)
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({
            "id": "kfc_001",
            "carte": "123456",
            "point": 500
        }))
        .send()
        .await?;
    
    println!("Insert status: {}", response.status());
    
    // PUT /update
    let response = client
        .put(&format!("{}/update", base_url))
        .header("Authorization", &auth_header)
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({
            "id": "kfc_001",
            "point": 750
        }))
        .send()
        .await?;
    
    println!("Update status: {}", response.status());
    
    // POST /generate
    let response = client
        .post(&format!("{}/generate", base_url))
        .header("Authorization", &auth_header)
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({
            "min_points": 100,
            "max_points": 1000
        }))
        .timeout(std::time::Duration::from_secs(30))
        .send()
        .await?;
    
    if response.status() == 200 {
        let account: serde_json::Value = response.json().await?;
        println!("Compte trouvé: {}", account);
    } else if response.status() == 404 {
        println!("Aucun compte disponible");
    }
    
    Ok(())
}
```

---

## PowerShell

### Script complet

```powershell
# Configuration
$baseUrl = "http://localhost:8080"
$username = "votre_username"
$password = "votre_mot_de_passe"

# Générer le token Basic Auth
$credentials = "${username}:${password}"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($credentials)
$base64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $base64"
    "Content-Type" = "application/json"
}

# POST /insert
$body = @{
    id = "kfc_001"
    carte = "123456"
    point = 500
    email = "user@example.com"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/insert" `
        -Method POST `
        -Headers $headers `
        -Body $body
    Write-Host "Insert: Succès"
} catch {
    Write-Host "Insert: Erreur - $($_.Exception.Message)"
}

# PUT /update
$body = @{
    id = "kfc_001"
    point = 750
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/update" `
        -Method PUT `
        -Headers $headers `
        -Body $body
    Write-Host "Update: Succès"
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "Update: Compte non trouvé"
    } else {
        Write-Host "Update: Erreur - $($_.Exception.Message)"
    }
}

# POST /generate
$body = @{
    min_points = 100
    max_points = 1000
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/generate" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 30
    Write-Host "Compte trouvé:"
    $response | ConvertTo-Json
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "Aucun compte disponible"
    } else {
        Write-Host "Erreur: $($_.Exception.Message)"
    }
}
```

---

## Scénarios complets

### Scénario 1 : Workflow complet

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

# 1. Insérer plusieurs comptes
accounts = [
    {"id": "kfc_001", "carte": "111111", "point": 500},
    {"id": "kfc_002", "carte": "222222", "point": 750},
    {"id": "kfc_003", "carte": "333333", "point": 1000},
]

for account in accounts:
    response = requests.post(f"{BASE_URL}/insert", json=account, headers=headers)
    print(f"Inserted {account['id']}: {response.status_code}")

# 2. Mettre à jour un compte
response = requests.put(
    f"{BASE_URL}/update",
    json={"id": "kfc_001", "point": 600},
    headers=headers
)
print(f"Updated kfc_001: {response.status_code}")

# 3. Générer un compte dans une fourchette
response = requests.post(
    f"{BASE_URL}/generate",
    json={"min_points": 400, "max_points": 800},
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    account = response.json()
    print(f"Compte généré: {account['id']} avec {account['point']} points")
elif response.status_code == 404:
    print("Aucun compte disponible dans cette fourchette")
```

### Scénario 2 : Gestion d'erreurs robuste

```python
import requests
import base64
from typing import Optional, Dict, Any

class KfcAPIError(Exception):
    pass

def call_api(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    BASE_URL = "http://localhost:8080"
    USERNAME = "votre_username"
    PASSWORD = "votre_mot_de_passe"
    
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Méthode non supportée: {method}")
        
        if response.status_code == 204:
            return {"success": True}
        elif response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 404:
            return {"success": False, "error": "Not found"}
        elif response.status_code == 401:
            raise KfcAPIError("Authentification échouée")
        elif response.status_code == 400:
            raise KfcAPIError(f"Requête invalide: {response.text}")
        else:
            raise KfcAPIError(f"Erreur serveur: {response.status_code}")
            
    except requests.exceptions.Timeout:
        raise KfcAPIError("Timeout - La requête a pris trop de temps")
    except requests.exceptions.ConnectionError:
        raise KfcAPIError("Impossible de se connecter à l'API")
    except Exception as e:
        raise KfcAPIError(f"Erreur inattendue: {str(e)}")

# Utilisation
try:
    # Insérer
    result = call_api("POST", "/insert", {
        "id": "test_001",
        "carte": "123456",
        "point": 500
    })
    print("Insert:", result)
    
    # Générer
    result = call_api("POST", "/generate", {
        "min_points": 100,
        "max_points": 1000
    })
    if result.get("success") and "data" in result:
        print("Compte:", result["data"])
    else:
        print("Aucun compte disponible")
        
except KfcAPIError as e:
    print(f"Erreur API: {e}")
```

---

**Pour plus d'informations, consultez [API_REFERENCE.md](./API_REFERENCE.md)**
