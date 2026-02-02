# Sécurité et Authentification

## Table des matières

1. [Authentification Basic Auth](#authentification-basic-auth)
2. [Sécurité des données](#sécurité-des-données)
3. [Bonnes pratiques](#bonnes-pratiques)
4. [Recommandations](#recommandations)
5. [Audit de sécurité](#audit-de-sécurité)

---

## Authentification Basic Auth

### Principe

Tous les endpoints de l'API sont protégés par **Basic Authentication**.

### Fonctionnement

1. **Client** : Envoie les credentials encodés en base64 dans le header `Authorization`
2. **Serveur** : Décode et compare avec les credentials stockés dans les variables d'environnement
3. **Résultat** : Autorise ou rejette la requête

### Format du header

```
Authorization: Basic <base64(username:password)>
```

### Exemple

```bash
# Credentials: votre_username / votre_mot_de_passe
# Encodage: base64("votre_username:votre_mot_de_passe")
Authorization: Basic Y2xlbXNlcl86Q2xlbXNlcjI5MDMh
```

### Configuration

Les credentials sont définis dans `.env` :

```env
BASIC_AUTH_USER=votre_username
BASIC_AUTH_PASSWORD=votre_mot_de_passe
```

### ⚠️ Limitations

1. **Transmission en clair** : Les credentials sont encodés en base64 (pas chiffrés)
   - **Solution** : Utiliser HTTPS en production

2. **Pas de rotation automatique** : Les credentials sont statiques
   - **Solution** : Changer régulièrement les mots de passe

3. **Pas de gestion de session** : Chaque requête nécessite les credentials
   - **Note** : C'est normal pour Basic Auth

---

## Sécurité des données

### Données stockées

L'API stocke des informations sensibles :
- **Email** : Stocké en clair
- **Password** : Stocké en clair
- **Customer ID** : Identifiant KFC
- **Points** : Informations de fidélité

### ⚠️ Points d'attention

1. **Mots de passe en clair**
   - Les mots de passe des comptes KFC sont stockés sans hashage
   - **Risque** : Accès non autorisé en cas de compromission de la DB

2. **Pas de chiffrement au repos**
   - Les données sensibles ne sont pas chiffrées dans la base
   - **Risque** : Lecture des données si la DB est compromise

3. **Pas de chiffrement en transit (HTTP)**
   - Les données transitent en HTTP (non chiffré)
   - **Risque** : Interception des données par un attaquant

### Recommandations

1. **Utiliser HTTPS** en production
2. **Chiffrer les données sensibles** dans la base (optionnel)
3. **Hasher les mots de passe** si nécessaire (bcrypt, argon2)

---

## Bonnes pratiques

### 1. Configuration sécurisée

#### Fichier .env

```env
# ✅ Bonne pratique : Variables d'environnement
BASIC_AUTH_USER=username
BASIC_AUTH_PASSWORD=password_complexe_et_long

# ❌ À éviter : Credentials faibles
BASIC_AUTH_PASSWORD=1234
```

#### .gitignore

Assurez-vous que `.env` est dans `.gitignore` :

```gitignore
.env
*.env
.env.local
```

### 2. Mots de passe forts

**Critères recommandés** :
- Minimum 12 caractères
- Mélange de majuscules, minuscules, chiffres, symboles
- Pas de mots du dictionnaire
- Unique pour chaque service

**Exemple** :
```
✅ VotreMotDePasse123!@#Secure
❌ password123
❌ admin
```

### 3. Accès à la base de données

#### Utilisateur dédié

Créer un utilisateur PostgreSQL avec des permissions minimales :

```sql
-- Créer un utilisateur dédié
CREATE USER kfc_api_user WITH PASSWORD 'mot_de_passe_fort';

-- Donner uniquement les permissions nécessaires
GRANT CONNECT ON DATABASE kfc_bot TO kfc_api_user;
GRANT USAGE ON SCHEMA public TO kfc_api_user;
GRANT SELECT, INSERT, UPDATE ON kfc_storage TO kfc_api_user;

-- Ne PAS donner DELETE ou DROP
```

#### Connexion sécurisée

```env
# ✅ Utiliser un utilisateur dédié
DATABASE_URL=postgres://kfc_api_user:password@localhost:5432/kfc_bot

# ❌ Éviter d'utiliser postgres (superuser)
DATABASE_URL=postgres://postgres:password@localhost:5432/kfc_bot
```

### 4. Logs et monitoring

#### Niveaux de log

```env
# Production : info ou warn
RUST_LOG=info

# Développement : debug
RUST_LOG=debug
```

#### ⚠️ Ne pas logger les credentials

```rust
// ❌ À éviter
log::info!("Password: {}", password);

// ✅ Bonne pratique
log::info!("User authenticated: {}", username);
```

### 5. Rate limiting (à implémenter)

Pour éviter les abus, implémenter un rate limiting :

```rust
// Exemple avec actix-web-httpauth + actix-limitation
.use(actix_limitation::Limiter::default())
```

---

## Recommandations

### Production

1. **HTTPS obligatoire**
   - Utiliser un reverse proxy (nginx, Caddy) avec certificat SSL
   - Rediriger tout le trafic HTTP vers HTTPS

2. **Firewall**
   - Limiter l'accès au port de l'API
   - Autoriser uniquement les IPs autorisées si possible

3. **Monitoring**
   - Surveiller les tentatives d'authentification échouées
   - Alerter en cas de comportement suspect

4. **Backup régulier**
   - Sauvegarder la base de données régulièrement
   - Tester la restauration des backups

5. **Mises à jour**
   - Maintenir les dépendances à jour
   - Appliquer les correctifs de sécurité

### Développement

1. **Variables d'environnement**
   - Ne jamais commiter `.env`
   - Utiliser des credentials différents en dev/prod

2. **Tests de sécurité**
   - Tester l'authentification
   - Tester les validations d'entrée
   - Tester les erreurs

3. **Code review**
   - Vérifier qu'aucun credential n'est hardcodé
   - Vérifier la gestion des erreurs

---

## Audit de sécurité

### Points vérifiés

✅ **Authentification** : Tous les endpoints sont protégés  
✅ **Pas de code malveillant** : Aucun stealer, malware, ou backdoor détecté  
✅ **Gestion des erreurs** : Pas de fuite d'informations sensibles  
✅ **Validation des entrées** : Validation basique présente  

### Points à améliorer

⚠️ **Mots de passe en clair** : Les mots de passe sont stockés sans hashage  
⚠️ **HTTP non chiffré** : Utiliser HTTPS en production  
⚠️ **Pas de rate limiting** : Risque de brute force  
⚠️ **Pas de chiffrement au repos** : Données sensibles en clair dans la DB  

### Checklist de sécurité

- [x] Authentification sur tous les endpoints
- [x] Pas de credentials hardcodés
- [x] Variables d'environnement pour la config
- [x] Gestion des erreurs sans fuite d'infos
- [ ] HTTPS en production
- [ ] Rate limiting
- [ ] Chiffrement des données sensibles
- [ ] Hashage des mots de passe
- [ ] Audit logs
- [ ] Monitoring des tentatives d'intrusion

---

## Exemples d'attaques et protections

### 1. Brute force

**Attaque** : Tester de nombreux mots de passe pour deviner les credentials

**Protection** :
- Rate limiting
- Mots de passe forts
- Monitoring des tentatives échouées

### 2. Man-in-the-middle

**Attaque** : Intercepter le trafic HTTP pour voler les credentials

**Protection** :
- HTTPS obligatoire
- Certificats SSL valides

### 3. Injection SQL

**Attaque** : Injecter du code SQL malveillant

**Protection** :
- ✅ Utilisation de Diesel ORM (protection automatique)
- ✅ Paramètres préparés

### 4. XSS (Cross-Site Scripting)

**Attaque** : Injecter du code JavaScript malveillant

**Protection** :
- ✅ API REST (pas de rendu HTML)
- ✅ Validation des entrées JSON

---

## Conclusion

L'API utilise Basic Auth pour protéger les endpoints, ce qui est suffisant pour un usage interne. Pour la production, il est recommandé d'ajouter :

1. HTTPS
2. Rate limiting
3. Monitoring
4. Chiffrement des données sensibles (optionnel)

---

**Pour plus d'informations sur l'utilisation, consultez [API_REFERENCE.md](./API_REFERENCE.md)**
