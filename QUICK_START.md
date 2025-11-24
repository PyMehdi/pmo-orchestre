# ⚡ GUIDE DE DÉMARRAGE RAPIDE - PMO ORCHESTRE

## Lancez l'application en 5 minutes !

---

## ✅ PRÉREQUIS

Avant de commencer, assurez-vous d'avoir :

- [x] Python installé
- [x] Dossier `PMO_Orchestre` avec tous les fichiers
- [x] Fichier `credentials.json` dans le dossier
- [x] Test de connexion réussi (test_connexion.py)

---

## 🚀 LANCEMENT EN 4 ÉTAPES

### **ÉTAPE 1 : Ouvrir le terminal dans le dossier**

**Mac/Linux :**
```bash
cd ~/Documents/PMO_Orchestre
```

**Windows :**
- Naviguer vers le dossier dans l'Explorateur
- Taper `cmd` dans la barre d'adresse
- Appuyer sur Entrée

---

### **ÉTAPE 2 : Activer l'environnement virtuel**

**Mac/Linux :**
```bash
source venv/bin/activate
```

**Windows :**
```bash
venv\Scripts\activate
```

**✅ Vous devez voir `(venv)` au début de la ligne**

---

### **ÉTAPE 3 : Lancer l'application**

```bash
streamlit run app.py
```

---

### **ÉTAPE 4 : Ouvrir dans le navigateur**

L'application s'ouvre automatiquement à :
```
http://localhost:8501
```

Si elle ne s'ouvre pas automatiquement, copier l'URL depuis le terminal.

---

## 🎯 PREMIÈRE UTILISATION

### **1. Dashboard (Page d'accueil)**

Vous verrez :
- ✅ Nombre de projets actifs
- ✅ Nombre de chefs disponibles
- ✅ Graphiques de répartition
- ✅ Alertes éventuelles

### **2. Ajouter des données de test**

#### **Ajouter un Chef :**
1. Menu latéral : **👤 Gestion Chefs**
2. Onglet **➕ Ajouter/Modifier**
3. Remplir :
   - ID Chef : `CP-001`
   - Nom : `Test CHEF`
   - Email : `test@email.com`
   - Expérience : `5` ans
   - Compétences : Niveau 3 partout
4. Cliquer **💾 Enregistrer**

#### **Ajouter un Projet :**
1. Menu latéral : **📁 Gestion Projets**
2. Onglet **➕ Ajouter/Modifier**
3. Remplir :
   - ID Projet : `PROJ-001`
   - Nom : `Test Projet`
   - Client : `Test Client`
   - Budget : `1000000`
   - Charge JH : `100`
4. Cliquer **💾 Enregistrer**

### **3. Tester l'affectation**

1. Menu latéral : **🎯 Affectation**
2. Sélectionner le projet `PROJ-001`
3. Cliquer **🔍 Trouver les Meilleurs Chefs**
4. Voir les suggestions avec scores
5. Cliquer **✅ Affecter**

---

## 📖 NAVIGATION

### **Pages disponibles :**

| Icône | Page | Fonction |
|-------|------|----------|
| 📊 | Dashboard | Vue d'ensemble |
| 👤 | Gestion Chefs | CRUD chefs de projet |
| 📁 | Gestion Projets | CRUD projets |
| 🎯 | Affectation | Suggestions intelligentes |
| 📈 | Analyses | Statistiques et graphiques |

---

## 🎨 FONCTIONNALITÉS PRINCIPALES

### **CRUD (Create, Read, Update, Delete)**

**Ajouter** un élément :
- Aller dans la page correspondante
- Onglet **➕ Ajouter/Modifier**
- Remplir le formulaire
- Cliquer **💾 Enregistrer**

**Consulter** les éléments :
- Onglet **📋 Liste**
- Utiliser les filtres pour affiner
- Voir le tableau complet

**Modifier** un élément :
- ⚠️ Fonction à venir dans version 1.1
- Pour l'instant : modifier directement dans Google Sheets

**Supprimer** un élément :
- ⚠️ Fonction à venir dans version 1.1
- Pour l'instant : supprimer directement dans Google Sheets

---

## 🔧 ARRÊTER L'APPLICATION

### **Dans le terminal :**

Appuyer sur **Ctrl + C**

L'application s'arrête.

---

## 🔄 RELANCER L'APPLICATION

### **Si l'environnement est déjà activé :**

```bash
streamlit run app.py
```

### **Si l'environnement n'est pas activé :**

```bash
# Mac/Linux
source venv/bin/activate
streamlit run app.py

# Windows
venv\Scripts\activate
streamlit run app.py
```

---

## 🐛 PROBLÈMES COURANTS

### **Erreur : "ModuleNotFoundError: No module named 'streamlit'"**

**Solution :**
```bash
pip install streamlit
```

### **L'application ne charge pas les données**

**Solution :**
1. Vérifier que `credentials.json` est dans le dossier
2. Vérifier que le Google Sheet est partagé
3. Relancer `python test_connexion.py` pour vérifier

### **Port 8501 déjà utilisé**

**Solution :**
```bash
streamlit run app.py --server.port 8502
```

---

## 💡 ASTUCES

### **Rafraîchir les données**

Appuyer sur **R** dans le navigateur pour recharger l'application.

### **Mode plein écran**

Appuyer sur **F** dans le menu Streamlit (en haut à droite).

### **Thème sombre**

Cliquer sur **⚙️ Settings** → **Theme** → **Dark**

---

## 📊 DONNÉES DE DÉMONSTRATION

### **Ajouter rapidement plusieurs chefs**

Copier-coller ces données directement dans Google Sheets (onglet Chefs_Projet) :

```
CP-001 | Ahmed BENALI | ahmed@test.ma | Disponible | 8 | 15 | 4 - Avancé | 5 - Expert | 3 - Intermédiaire
CP-002 | Fatima ALAMI | fatima@test.ma | Disponible | 12 | 28 | 5 - Expert | 4 - Avancé | 4 - Avancé
CP-003 | Youssef BENNANI | youssef@test.ma | Disponible | 5 | 8 | 3 - Intermédiaire | 3 - Intermédiaire | 2 - Élémentaire
```

### **Ajouter rapidement plusieurs projets**

Copier-coller ces données dans Google Sheets (onglet Projets) :

```
PROJ-001 | Migration ERP | Banque XX | En attente | 2500000 | 180 | 4 - Élevée | 3 - Modéré | 12 | 2 - Standard | 8 | 2 - Multi-sites
PROJ-002 | App Mobile | CIH Bank | En attente | 800000 | 95 | 3 - Modérée | 2 - Faible | 6 | 1 - Partenaire | 4 | 1 - Même bureau
PROJ-003 | Cloud Migration | Ministère | En attente | 5000000 | 350 | 5 - Très élevée | 5 - Critique | 25 | 3 - Difficile | 12 | 4 - Multi-offshore
```

---

## ✅ CHECKLIST DE DÉMARRAGE

- [ ] Terminal ouvert dans le bon dossier
- [ ] Environnement virtuel activé `(venv)`
- [ ] Commande `streamlit run app.py` exécutée
- [ ] Application ouverte dans le navigateur
- [ ] Données de test ajoutées
- [ ] Test d'affectation réussi

---

## 🎯 PROCHAINES ÉTAPES

1. ✅ **Familiarisez-vous** avec l'interface (15 min)
2. ✅ **Ajoutez vos vrais projets** dans Gestion Projets
3. ✅ **Ajoutez vos vrais chefs** dans Gestion Chefs
4. ✅ **Testez les affectations** dans Affectation Intelligente
5. ✅ **Ajustez les pondérations** dans Google Sheets (après questionnaire)
6. ✅ **Analysez les résultats** dans Analyses

---

## 📞 BESOIN D'AIDE ?

### **Problème technique**

1. Vérifier les logs dans le terminal
2. Consulter le README.md complet
3. Relancer le test de connexion

### **Fonctionnalité manquante**

Consulter la section "Évolutions futures" du README.md

---

## 🎉 FÉLICITATIONS !

Vous êtes prêt à utiliser **PMO Orchestre** !

**Durée de prise en main : 15-20 minutes**

---

**🎼 Orchestrez vos projets IT avec intelligence ! 🎼**
