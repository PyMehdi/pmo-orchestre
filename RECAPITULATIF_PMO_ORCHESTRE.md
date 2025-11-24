# 📋 RÉCAPITULATIF - CONFIGURATION API GOOGLE SHEETS

## Projet : PMO Orchestre

---

## 🎯 NOMS À UTILISER DANS GOOGLE CLOUD

### Projet Google Cloud
```
Nom : PMO-Orchestre
```

### Service Account
```
Nom : pmo-orchestre-service
Email (exemple) : pmo-orchestre-service@pmo-orchestre-xxxxx.iam.gserviceaccount.com
```

### Fichier téléchargé
```
Nom d'origine : pmo-orchestre-xxxxxxxxxxxxx.json
À renommer en : credentials.json
```

---

## 📁 STRUCTURE DES DOSSIERS

### Dossier du projet

**Windows :**
```
C:\Users\VotreNom\Documents\PMO_Orchestre\
```

**Mac / Linux :**
```
/Users/votrenom/Documents/PMO_Orchestre/
```

### Fichiers à placer dans ce dossier

```
PMO_Orchestre/
├── credentials.json          ← Fichier téléchargé depuis Google Cloud
├── test_connexion.py         ← Script de test (fourni)
└── requirements.txt          ← Dépendances Python (fourni)
```

---

## ✅ CHECKLIST DE CONFIGURATION

### Étape 1 : Google Cloud Console

- [ ] Aller sur https://console.cloud.google.com/
- [ ] Créer un nouveau projet : **PMO-Orchestre**
- [ ] Activer **Google Sheets API**
- [ ] Activer **Google Drive API**

### Étape 2 : Service Account

- [ ] Créer un compte de service : **pmo-orchestre-service**
- [ ] Rôle : **Éditeur**
- [ ] Créer une clé **JSON**
- [ ] Télécharger le fichier et le renommer : **credentials.json**

### Étape 3 : Permissions Google Sheet

- [ ] Ouvrir credentials.json
- [ ] Copier l'email : `pmo-orchestre-service@pmo-orchestre-xxxxx...`
- [ ] Ouvrir le Google Sheet
- [ ] Cliquer sur **Partager**
- [ ] Ajouter l'email du service account
- [ ] Rôle : **Éditeur**
- [ ] Décocher "Avertir les utilisateurs"
- [ ] Cliquer sur **Partager**

### Étape 4 : Installation Python

- [ ] Créer le dossier **PMO_Orchestre**
- [ ] Y placer les 3 fichiers (credentials.json, test_connexion.py, requirements.txt)
- [ ] Ouvrir le terminal dans ce dossier
- [ ] Créer l'environnement virtuel : `python -m venv venv`
- [ ] Activer l'environnement :
  - Windows : `venv\Scripts\activate`
  - Mac/Linux : `source venv/bin/activate`
- [ ] Installer les dépendances : `pip install -r requirements.txt`

### Étape 5 : Test de Connexion

- [ ] Exécuter : `python test_connexion.py`
- [ ] Vérifier que tous les tests passent avec ✅
- [ ] Faire 2 captures d'écran (terminal + Google Sheet)
- [ ] Confirmer à l'encadrant que ça fonctionne

---

## 🔗 LIENS UTILES

### Documentation fournie

1. **Guide complet de configuration**
   - Fichier : `guide_api_google_sheets.md`
   - Contenu : Étapes détaillées avec captures d'écran

2. **Guide d'installation et test**
   - Fichier : `guide_installation_test.md`
   - Contenu : Installation Python + exécution du test

3. **Script de test**
   - Fichier : `test_connexion.py`
   - Fonction : Vérifier que tout fonctionne

4. **Dépendances**
   - Fichier : `requirements.txt`
   - Contenu : Liste des packages Python nécessaires

### Google Sheet du projet

```
URL : https://docs.google.com/spreadsheets/d/1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs/edit
ID : 1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs
```

### Google Cloud Console

```
URL : https://console.cloud.google.com/
Projet : PMO-Orchestre
```

---

## 📧 INFORMATIONS À FOURNIR APRÈS LE TEST

Une fois le test réussi, me communiquer :

1. ✅ **Email complet du service account**
   - Format : `pmo-orchestre-service@pmo-orchestre-xxxxx.iam.gserviceaccount.com`
   - Trouvable dans credentials.json, ligne "client_email"

2. ✅ **Confirmation que le Google Sheet est partagé**
   - Vérifier que l'email du service account apparaît dans les personnes avec accès

3. ✅ **Capture d'écran du test réussi**
   - Terminal montrant tous les ✅ verts
   - Message final "TEST DE CONNEXION RÉUSSI !"

4. ✅ **Capture d'écran du Google Sheet**
   - Les 3 onglets visibles (Projets, Chefs_Projet, Ponderations)
   - Quelques données présentes

---

## ⏱️ DURÉE ESTIMÉE PAR ÉTAPE

| Étape | Description | Durée |
|-------|-------------|-------|
| 1 | Configuration Google Cloud | 10-15 min |
| 2 | Installation Python | 5-10 min |
| 3 | Test de connexion | 2 min |
| **TOTAL** | **Configuration complète** | **20-30 min** |

---

## 🚀 APRÈS LA CONFIGURATION

### Ce qui se passe ensuite

1. ✅ Vous me confirmez que le test passe
2. ✅ Je développe l'application Streamlit complète (3-5 jours)
3. ✅ Vous recevez :
   - Application web fonctionnelle
   - Code source complet
   - Documentation utilisateur
   - Guide de déploiement

### Livrables attendus

- **Application Streamlit** : Interface web avec 5 pages
  - Dashboard PMO
  - Gestion des chefs de projet
  - Gestion des projets
  - Module d'affectation intelligente
  - Analyses et rapports

- **Modules Python** :
  - data_manager.py (connexion Google Sheets)
  - algorithme.py (calculs d'affectation)
  - scoring.py (scores de compatibilité)
  - visualisation.py (graphiques interactifs)

- **Documentation** :
  - Guide utilisateur PMO
  - Documentation technique
  - Présentation PowerPoint pour soutenance

---

## 🔒 SÉCURITÉ

### Fichier credentials.json

⚠️ **RÈGLES STRICTES :**

- ❌ **NE JAMAIS** partager ce fichier
- ❌ **NE JAMAIS** le mettre sur GitHub public
- ❌ **NE JAMAIS** l'envoyer par email
- ✅ **TOUJOURS** le garder sur votre ordinateur local
- ✅ **TOUJOURS** l'ajouter à .gitignore

### Email du service account

✅ **Vous POUVEZ** partager l'email du service account avec moi
✅ Cet email n'est pas sensible (c'est juste une adresse)
❌ Le fichier JSON est sensible (contient les clés privées)

---

## 📞 SUPPORT

### En cas de problème

**Me contacter avec :**
1. Capture d'écran de l'erreur
2. Message d'erreur complet du terminal
3. Étape où vous êtes bloqué

**Je réponds rapidement avec la solution ! 💪**

---

## 🎯 OBJECTIF

**Configuration API réussie = Développement peut commencer !**

Une fois que votre test affiche tous les ✅ verts, le développement de l'application complète démarre immédiatement.

---

**Bonne configuration ! 🚀**

**PMO Orchestre - Orchestrez vos projets avec intelligence ! 🎼**
