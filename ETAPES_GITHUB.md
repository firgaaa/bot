# Ajouter les dossiers api et main au dépôt GitHub "bot"

## Étape 1 : Créer le dépôt "bot" sur GitHub

1. Va sur **https://github.com/new**
2. **Repository name** : `bot`
3. Laisse **Public** (ou choisis Privé si tu préfères)
4. **Ne coche pas** "Add a README file" (on veut un dépôt vide)
5. Clique sur **Create repository**

---

## Étape 2 : Lier ce dossier au nouveau dépôt et pousser

Ouvre un terminal dans le dossier `BOT` et exécute (remplace **VOTRE_USERNAME** par ton pseudo GitHub) :

```powershell
cd "c:\Users\clemser_\Desktop\Gestion_KFC\BOT"

# Remplacer l'ancien dépôt (bot-main) par le nouveau "bot"
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/bot.git

# Ajouter les 2 dossiers api et main + le .gitignore
git add .
git status
git commit -m "Initial: ajout des dossiers api et main"

# Envoyer sur GitHub
git push -u origin main
```

Le fichier `main/staff.env` ne sera **pas** envoyé (il est dans le `.gitignore`).

Quand tu as créé le dépôt "bot" et ton pseudo GitHub, dis-moi et on pourra lancer les commandes ensemble.
