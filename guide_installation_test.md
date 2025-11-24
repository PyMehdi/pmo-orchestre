# 🐍 GUIDE D'INSTALLATION ET TEST - PYTHON + GOOGLE SHEETS API

## Tester que votre connexion Google Sheets fonctionne

**Durée estimée : 5-10 minutes**

---

## 📋 PRÉREQUIS

Avant de commencer, assurez-vous d'avoir :

- ✅ Python 3.8 ou supérieur installé
- ✅ Le fichier `credentials.json` (depuis la configuration API)
- ✅ Les fichiers `test_connexion.py` et `requirements.txt` (fournis)
- ✅ Votre Google Sheet partagé avec le service account

---

## 🔍 VÉRIFIER L'INSTALLATION DE PYTHON

### Windows

Ouvrir **PowerShell** ou **CMD** et taper :

```bash
python --version
```

ou

```bash
python3 --version
```

**Résultat attendu :**
```
Python 3.8.x  (ou supérieur)
```

### Mac / Linux

Ouvrir le **Terminal** et taper :

```bash
python3 --version
```

**Résultat attendu :**
```
Python 3.8.x  (ou supérieur)
```

### ❌ Si Python n'est pas installé

**Windows :**
1. Télécharger depuis : https://www.python.org/downloads/
2. ✅ Cocher "Add Python to PATH" pendant l'installation
3. Redémarrer l'ordinateur

**Mac :**
```bash
brew install python3
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## 📁 STRUCTURE DES FICHIERS

Créer un dossier pour votre projet, par exemple :

```
C:\Users\VotreNom\Documents\PMO_Orchestre\
```

ou sur Mac/Linux :

```
/Users/votrenom/Documents/PMO_Orchestre/
```

Dans ce dossier, placer les fichiers suivants :

```
PMO_Orchestre/
├── credentials.json          ← Votre fichier de credentials Google
├── test_connexion.py         ← Script de test (fourni)
└── requirements.txt          ← Liste des dépendances (fourni)
```

---

## 🚀 INSTALLATION DES DÉPENDANCES

### Étape 1 : Ouvrir le terminal dans le bon dossier

**Windows :**
1. Ouvrir l'Explorateur de fichiers
2. Naviguer vers le dossier `PMO_Orchestre`
3. Dans la barre d'adresse, taper `cmd` et appuyer sur Entrée
4. Une fenêtre CMD s'ouvre dans le bon dossier

**Mac / Linux :**
1. Ouvrir le Terminal
2. Naviguer vers le dossier :
   ```bash
   cd /Users/votrenom/Documents/PMO_Orchestre
   ```

### Étape 2 : Créer un environnement virtuel (RECOMMANDÉ)

**Pourquoi ?** Pour isoler les dépendances de ce projet.

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Résultat attendu :**
Vous devriez voir `(venv)` au début de votre ligne de commande :
```
(venv) C:\Users\VotreNom\Documents\PMO_Orchestre>
```

### Étape 3 : Installer les dépendances

**Avec l'environnement virtuel activé :**

```bash
pip install -r requirements.txt
```

**Temps d'installation :** 2-3 minutes

**Résultat attendu :**
```
Successfully installed gspread-5.12.0 oauth2client-4.1.3 streamlit-1.29.0 ...
```

✅ **Dépendances installées !**

---

## 🧪 EXÉCUTER LE TEST DE CONNEXION

### Commande pour lancer le test

**S'assurer que l'environnement virtuel est activé** (vous devez voir `(venv)`)

Puis exécuter :

```bash
python test_connexion.py
```

---

## ✅ RÉSULTATS ATTENDUS

### Si tout fonctionne correctement :

```
============================================================
   TEST DE CONNEXION - GOOGLE SHEETS API
   Projet PFE - ENCG Settat
   09/11/2024 14:30:15
============================================================

🔐 TEST DE CONNEXION GOOGLE SHEETS API

============================================================

📋 Étape 1/5 : Vérification du fichier credentials...
✅ Fichier credentials.json trouvé
   Service Account : pmo-orchestre-service@pmo-orchestre-xxxxx.iam.gserviceaccount.com

============================================================

🔑 Étape 2/5 : Configuration de l'authentification...
✅ Authentification configurée

============================================================

🌐 Étape 3/5 : Connexion au client Google Sheets...
✅ Client Google Sheets connecté

============================================================

📊 Étape 4/5 : Ouverture du Google Sheet...
✅ Google Sheet ouvert avec succès
   Titre : PMO_Affectation_Projets_IT
   URL : https://docs.google.com/spreadsheets/d/1TFC.../edit

============================================================

📖 Étape 5/5 : Test de lecture des onglets...
✅ 3 onglet(s) trouvé(s) :
   • Projets (100 lignes × 18 colonnes)
   • Chefs_Projet (100 lignes × 17 colonnes)
   • Ponderations (20 lignes × 4 colonnes)

   Vérification des onglets attendus :
   ✅ 'Projets' : Présent
   ✅ 'Chefs_Projet' : Présent
   ✅ 'Ponderations' : Présent

============================================================

🔍 TEST BONUS : Lecture des données Ponderations...
✅ Données lues avec succès
   Nombre de lignes : 17

   Aperçu des 5 premières lignes :
   1. Paramètre               Poids
   2. Budget                  15
   3. Charge JH               20
   4. Complexité Tech         18
   5. Niveau Risque           15

============================================================

✅ TEST DE CONNEXION RÉUSSI !

🎉 Votre connexion Google Sheets API est fonctionnelle !

Vous pouvez maintenant :
  1. Lire les données de votre Google Sheet
  2. Écrire dans votre Google Sheet
  3. Passer au développement de l'application Streamlit

============================================================

✅ Tous les tests sont passés avec succès !

📧 Prochaine étape : Informez votre encadrant que la connexion
   est fonctionnelle pour démarrer le développement de l'application.
```

---

## ❌ ERREURS COURANTES ET SOLUTIONS

### Erreur 1 : "credentials.json introuvable"

```
❌ ERREUR : Fichier 'credentials.json' introuvable
```

**Solution :**
1. Vérifier que le fichier `credentials.json` est bien dans le même dossier
2. Vérifier l'orthographe exacte du nom
3. Le fichier doit être au même niveau que `test_connexion.py`

---

### Erreur 2 : "SpreadsheetNotFound"

```
❌ ERREUR : Google Sheet introuvable
   Le Sheet avec l'ID ... n'existe pas ou
   n'est pas partagé avec le service account
```

**Solution :**
1. Ouvrir le fichier `credentials.json`
2. Copier l'email du `"client_email"`
3. Ouvrir votre Google Sheet
4. Cliquer sur **Partager**
5. Ajouter l'email du service account
6. Définir le rôle : **Éditeur**
7. Relancer le test

---

### Erreur 3 : "ModuleNotFoundError: No module named 'gspread'"

```
ModuleNotFoundError: No module named 'gspread'
```

**Solution :**
1. Vérifier que l'environnement virtuel est activé (voir `(venv)`)
2. Réinstaller les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

---

### Erreur 4 : "API has not been used in project"

```
Google Sheets API has not been used in project xxxxx before or it is disabled
```

**Solution :**
1. Retourner sur Google Cloud Console
2. Vérifier que **Google Sheets API** est activée
3. Vérifier que **Google Drive API** est activée
4. Attendre 2-3 minutes pour la propagation
5. Relancer le test

---

### Erreur 5 : Onglets manquants

```
⚠️  'Projets' : MANQUANT
```

**Solution :**
1. Ouvrir votre Google Sheet
2. Vérifier l'orthographe exacte des onglets :
   - `Projets` (pas "Projet" ou "projets")
   - `Chefs_Projet` (pas "Chefs_de_Projet" ou "chefs_projet")
   - `Ponderations` (pas "Pondérations" avec accent)
3. Renommer si nécessaire
4. Relancer le test

---

## 📸 CAPTURES D'ÉCRAN À FOURNIR

Si le test réussit, faire **2 captures d'écran** :

1. **Terminal avec le résultat complet du test**
   - Montrant tous les ✅ verts
   - Montrant la confirmation finale

2. **Google Sheet ouvert dans le navigateur**
   - Montrant les 3 onglets : Projets, Chefs_Projet, Ponderations
   - Avec quelques données visibles

**Envoyer ces captures d'écran pour confirmation.**

---

## 🎉 SI LE TEST RÉUSSIT

**Félicitations ! 🎊**

Votre connexion Google Sheets API est maintenant fonctionnelle.

### Prochaines étapes :

1. ✅ **Garder** l'environnement virtuel activé
2. ✅ **Ne pas supprimer** le fichier `credentials.json`
3. ✅ **Confirmer** à votre encadrant que tout fonctionne
4. ✅ **Attendre** les fichiers de l'application Streamlit

**Le développement de l'application peut maintenant commencer ! 🚀**

---

## 🔧 COMMANDES UTILES

### Activer l'environnement virtuel

**Windows :**
```bash
venv\Scripts\activate
```

**Mac / Linux :**
```bash
source venv/bin/activate
```

### Désactiver l'environnement virtuel

```bash
deactivate
```

### Relancer le test

```bash
python test_connexion.py
```

### Vérifier les packages installés

```bash
pip list
```

---

## 📞 BESOIN D'AIDE ?

Si vous rencontrez un problème :

1. **Copier le message d'erreur complet** du terminal
2. **Faire une capture d'écran** de l'erreur
3. **Noter à quelle étape** le problème survient
4. **Contacter votre encadrant** avec ces informations

---

**Bon test ! Vous êtes presque prêt pour le développement ! 💪**
