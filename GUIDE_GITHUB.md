# Guide GitHub – Projet BOT

Ce fichier explique à 100 % :
- **Partie 1** : créer le dépôt, y ajouter le projet et le mettre à jour (sur ton PC principal).
- **Partie 2** : sur un autre PC, créer l’espace de travail, récupérer le projet et faire les mises à jour.

---

# Partie 1 – Créer, ajouter et mettre à jour le projet sur GitHub

## 1.1 Créer le dépôt sur GitHub

1. Va sur **https://github.com/new** (connecte-toi si besoin).
2. **Repository name** : par exemple `bot` (ou le nom de ton projet).
3. **Description** (optionnel) : courte description du projet.
4. Choisis **Public** ou **Private**.
5. **Ne coche pas** « Add a README file », « Add .gitignore » ni « Choose a license » si ton projet existe déjà en local (dépôt vide).
6. Clique sur **Create repository**.

Tu obtiens une URL du type : `https://github.com/TON_PSEUDO/bot.git`.

---

## 1.2 Installer Git sur ton PC (si ce n’est pas déjà fait)

- Téléchargement : **https://git-scm.com/download/win**
- Après installation, ouvre un nouveau terminal (PowerShell ou CMD).

Vérifier que Git est installé :

```powershell
git --version
```

---

## 1.3 Lier ton dossier projet au dépôt GitHub (première fois)

Ouvre un terminal dans le dossier de ton projet (ex. `BOT`) :

```powershell
cd "C:\Users\clemser_\Desktop\Gestion_KFC\BOT"
```

- **Si le dossier n’a jamais été suivi par Git** (pas encore de dépôt Git local) :

```powershell
git init
git branch -M main
git remote add origin https://github.com/TON_PSEUDO/bot.git
```

- **Si un autre dépôt était déjà configuré** (changer l’origine) :

```powershell
git remote remove origin
git remote add origin https://github.com/TON_PSEUDO/bot.git
```

Remplace **TON_PSEUDO** par ton identifiant GitHub et **bot** par le nom de ton dépôt.

---

## 1.4 Ajouter les fichiers au dépôt (premier envoi)

1. Voir ce qui sera ajouté :
   ```powershell
   git status
   ```

2. Tout ajouter (les fichiers listés dans `.gitignore` ne seront pas inclus, ex. `value.env`, `*.env`) :
   ```powershell
   git add .
   ```

3. Créer un commit avec un message clair :
   ```powershell
   git commit -m "Description courte : ex. Premier envoi du projet bot"
   ```

4. Envoyer sur GitHub (la première fois, avec suivi de la branche) :
   ```powershell
   git push -u origin main
   ```

Si ta branche s’appelle `master` au lieu de `main` :

```powershell
git push -u origin master
```

À partir de là, le projet est sur GitHub.

---

## 1.5 Mettre à jour le projet sur GitHub (au quotidien)

Dès que tu modifies des fichiers et que tu veux enregistrer ces changements sur GitHub :

1. Voir les fichiers modifiés :
   ```powershell
   git status
   ```

2. Ajouter les fichiers à inclure dans le prochain commit :
   - tout : `git add .`
   - un seul fichier : `git add chemin/vers/fichier.py`

3. Créer un commit :
   ```powershell
   git commit -m "Description des changements : ex. Ajout du guide GitHub"
   ```

4. Envoyer les commits sur GitHub :
   ```powershell
   git push
   ```

Si tu as oublié de commit avant de faire `git push`, Git affiche **« Everything up-to-date »** : il n’y a rien de nouveau à envoyer. Dans ce cas, fais d’abord `git add` puis `git commit`, puis `git push`.

---

## 1.6 Fichiers ignorés (ne sont jamais envoyés sur GitHub)

Le fichier **`.gitignore`** à la racine du projet indique ce qui ne doit pas être versionné, par exemple :

- `value.env`, `staff.env`, `api/.env` (mots de passe, tokens)
- dossiers `__pycache__/`, `.venv/`, `venv/`
- fichiers `*.log`

Ces fichiers restent uniquement sur ton PC ; sur un autre PC, il faudra les recréer (voir Partie 2).

---

# Partie 2 – Sur un autre PC : créer l’espace, récupérer le projet et faire les mises à jour

## 2.1 Prérequis sur l’autre PC

- **Git** installé : https://git-scm.com/download/win  
- Connexion Internet.  
- (Optionnel) Compte GitHub si le dépôt est privé ; pour un dépôt public, le clone peut se faire sans compte.

---

## 2.2 Créer l’espace de travail et récupérer le projet (clone)

1. Ouvre un terminal et va dans le dossier où tu veux placer le projet (ex. Bureau, `Documents`, etc.) :

   ```powershell
   cd C:\Users\AutreUtilisateur\Desktop
   ```

2. Cloner le dépôt (récupère tout le code en une fois) :

   ```powershell
   git clone https://github.com/TON_PSEUDO/bot.git
   ```

   Un dossier **`bot`** est créé avec tout le contenu du dépôt.

3. Entrer dans le projet :

   ```powershell
   cd bot
   ```

Tu as maintenant une copie complète du projet à jour au moment du clone.

**Dépôt privé** : Git te demandera de t’identifier (compte GitHub + mot de passe ou token). Sur Windows, les identifiants peuvent être mémorisés par le Gestionnaire d’identifiants.

---

## 2.3 Fichiers à recréer sur l’autre PC (non versionnés)

Les fichiers suivants ne sont pas sur GitHub (à cause du `.gitignore`) ; il faut les recréer sur ce PC :

| Fichier        | Action |
|----------------|--------|
| **value.env**  | Copier `value.env.example` en `value.env`, puis remplir les vraies valeurs (tokens, base de données, etc.). |
| **staff.env**  | Recréer avec le même contenu que sur ton PC principal (données sensibles). |
| **api/.env**   | Recréer avec les variables nécessaires à l’API (DB, etc.). |

Exemple (PowerShell, dans le dossier `bot`) :

```powershell
copy value.env.example value.env
# Puis éditer value.env, staff.env et api\.env avec un éditeur de texte.
```

---

## 2.4 Récupérer les mises à jour (pull)

Quand le projet est déjà cloné sur cet autre PC et que tu veux récupérer les derniers changements envoyés sur GitHub :

1. Ouvre un terminal dans le dossier du projet :
   ```powershell
   cd C:\Users\AutreUtilisateur\Desktop\bot
   ```

2. Récupérer et appliquer les mises à jour :
   ```powershell
   git pull origin main
   ```

   Si la branche par défaut est déjà `main` et qu’elle suit `origin/main` :
   ```powershell
   git pull
   ```

3. (Optionnel) Voir l’état avant de tirer les mises à jour :
   ```powershell
   git fetch origin
   git status
   git pull
   ```

À chaque `git pull`, les nouveaux commits (fichiers modifiés, ajoutés, supprimés) sont téléchargés et appliqués dans ton dossier local.

---

## 2.5 Résumé des commandes selon la situation

| Situation | Commande |
|-----------|----------|
| **Première fois sur ce PC** – récupérer tout le projet | `git clone https://github.com/TON_PSEUDO/bot.git` puis `cd bot` |
| **Projet déjà cloné** – récupérer les dernières modifs | `cd bot` puis `git pull` (ou `git pull origin main`) |
| **Sur le PC principal** – envoyer tes modifs sur GitHub | `git add .` → `git commit -m "message"` → `git push` |

---

## Récapitulatif

- **Partie 1** : créer le dépôt sur GitHub → lier le dossier (`git init` / `git remote add origin ...`) → `git add .` → `git commit -m "..."` → `git push -u origin main`. Ensuite, pour toute mise à jour : `git add` → `git commit` → `git push`.
- **Partie 2** : sur l’autre PC, **récupérer le projet** = `git clone https://github.com/TON_PSEUDO/bot.git` ; **récupérer les mises à jour** = `cd bot` puis `git pull`. Penser à recréer `value.env`, `staff.env` et `api/.env` après le clone.
