# 🎼 PMO ORCHESTRE

Application web d'aide à la décision pour l'affectation optimisée des chefs de projets IT.

**Projet de Fin d'Études - ENCG Settat**  
**Master : Data Science pour le Management et l'IA**  
**Année : 2024-2025**

---

## 📋 DESCRIPTION

PMO Orchestre est une application web développée en Python avec Streamlit qui permet aux PMO (Project Management Office) d'optimiser l'affectation des chefs de projets IT aux projets en fonction :

- Des **paramètres de charge** des projets (budget, complexité, risque, etc.)
- Des **capacités** des chefs de projet (expérience, compétences, charge actuelle)
- D'un **algorithme de scoring** intelligent basé sur le PMBOK 7

---

## 🚀 FONCTIONNALITÉS

### 📊 **Dashboard PMO**
- Vue d'ensemble des projets et ressources
- KPIs en temps réel
- Alertes de surcharge
- Graphiques de répartition

### 👤 **Gestion des Chefs de Projet**
- CRUD complet (Create, Read, Update, Delete)
- Calcul automatique de capacité
- Suivi de la charge en temps réel
- Filtres et recherche

### 📁 **Gestion des Projets**
- CRUD complet
- Calcul automatique de l'indice de charge
- Filtres par statut
- Historique des affectations

### 🎯 **Affectation Intelligente**
- Algorithme de suggestion des 3 meilleurs chefs
- Score de compatibilité (0-100)
- Zones de charge (verte/orange/rouge)
- Justifications détaillées
- Affectation en un clic

### 📈 **Analyses & Rapports**
- Statistiques globales
- Analyse de la charge d'équipe
- Graphiques interactifs
- Visualisations en temps réel

---

## 🛠️ ARCHITECTURE TECHNIQUE

### **Stack Technique**
- **Langage** : Python 3.8+
- **Framework** : Streamlit 1.29+
- **Base de données** : Google Sheets (via API)
- **Visualisations** : Plotly, Matplotlib
- **Manipulation données** : Pandas, NumPy

### **Modules**

```
pmo_orchestre/
├── app.py                 # Application Streamlit principale (5 pages)
├── data_manager.py        # Gestion Google Sheets (CRUD)
├── algorithme.py          # Algorithmes d'affectation
├── credentials.json       # Credentials Google API (SECRET)
├── requirements.txt       # Dépendances Python
└── README.md             # Cette documentation
```

---

## ⚙️ INSTALLATION

### **Prérequis**
- Python 3.8 ou supérieur
- Compte Google avec Google Sheets API configuré
- Fichier `credentials.json` (voir guide de configuration)

### **Étape 1 : Cloner/Télécharger les fichiers**

Placer tous les fichiers dans un dossier `PMO_Orchestre/`

### **Étape 2 : Créer l'environnement virtuel**

```bash
python -m venv venv
```

### **Étape 3 : Activer l'environnement virtuel**

**Windows :**
```bash
venv\Scripts\activate
```

**Mac/Linux :**
```bash
source venv/bin/activate
```

### **Étape 4 : Installer les dépendances**

```bash
pip install -r requirements.txt
```

### **Étape 5 : Configurer Google Sheets**

1. Placer le fichier `credentials.json` dans le dossier
2. Vérifier que le Google Sheet est partagé avec le service account
3. Vérifier l'ID du Sheet dans `app.py` (ligne 56)

---

## 🚀 LANCEMENT DE L'APPLICATION

### **Commande**

```bash
streamlit run app.py
```

### **Résultat**

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

---

## 📖 GUIDE D'UTILISATION

### **1. Dashboard**
- Consultez les KPIs globaux
- Identifiez les alertes de surcharge
- Visualisez la répartition des charges

### **2. Ajouter un Chef de Projet**
1. Aller dans **👤 Gestion Chefs**
2. Onglet **➕ Ajouter/Modifier**
3. Remplir le formulaire
4. Cliquer sur **💾 Enregistrer**

### **3. Ajouter un Projet**
1. Aller dans **📁 Gestion Projets**
2. Onglet **➕ Ajouter/Modifier**
3. Remplir le formulaire
4. Cliquer sur **💾 Enregistrer**

### **4. Affecter un Projet**
1. Aller dans **🎯 Affectation**
2. Sélectionner le projet à affecter
3. Cliquer sur **🔍 Trouver les Meilleurs Chefs**
4. Consulter les 3 suggestions avec scores
5. Cliquer sur **✅ Affecter** pour le chef choisi

### **5. Analyser les Charges**
1. Aller dans **📈 Analyses**
2. Consulter les statistiques
3. Identifier les chefs surchargés
4. Prendre des décisions d'optimisation

---

## 🎯 ALGORITHME D'AFFECTATION

### **Calcul de l'Indice de Charge (IC)**

```
IC = Σ(Paramètre_normalisé × Poids)
```

**Paramètres :**
- Budget (15%)
- Charge JH (20%)
- Complexité Technique (18%)
- Niveau de Risque (15%)
- Nb Intervenants (12%)
- Type Client (10%)
- Fréquence Instances (5%)
- Dispersion Géo (5%)

### **Calcul de la Capacité Chef**

```
CAP = Σ(Compétence_normalisée × Poids)
```

**Paramètres :**
- Expérience (30%)
- Compétences Techniques (25%)
- Compétences Managériales (35%)
- Utilisation IA (10%)

### **Score de Compatibilité**

```
Score (0-100) = f(Charge_après, Capacité, Taux_charge)
```

**Zones :**
- 🟢 **Verte** (< 70%) : Affectation recommandée
- 🟠 **Orange** (70-90%) : Affectation possible avec surveillance
- 🔴 **Rouge** (> 90%) : Risque de surcharge

---

## 📊 STRUCTURE GOOGLE SHEETS

### **Feuille 1 : Projets**
- ID_Projet, Nom_Projet, Client, Statut
- Budget_MAD, Charge_JH
- Complexité, Risque, Intervenants, etc.
- **Indice_Charge** (calculé automatiquement)
- Chef_Affecté, Dates

### **Feuille 2 : Chefs_Projet**
- ID_Chef, Nom_Prenom, Email, Statut
- Années_Experience, Compétences
- **Capacite_Max** (calculé automatiquement)
- **Charge_Actuelle** (calculé automatiquement)
- **Taux_Charge_Pct** (calculé automatiquement)

### **Feuille 3 : Ponderations**
- Paramètres de Charge (8 lignes)
- Paramètres de Capacité (4 lignes)
- Valeurs modifiables pour tuning

---

## 🔒 SÉCURITÉ

### **Fichiers Sensibles**

❌ **NE JAMAIS partager ou commit** :
- `credentials.json` (contient les clés privées Google)

✅ **Peut être partagé** :
- Tous les autres fichiers Python
- README, documentation
- requirements.txt

### **.gitignore Recommandé**

```
# Credentials
credentials.json
*.json

# Python
__pycache__/
*.pyc
venv/
env/

# Streamlit
.streamlit/secrets.toml
```

---

## 🐛 DÉPANNAGE

### **Erreur : "No module named 'gspread'"**

**Solution :**
```bash
pip install -r requirements.txt
```

### **Erreur : "SpreadsheetNotFound"**

**Solution :**
1. Vérifier que le Google Sheet est partagé avec le service account
2. Vérifier l'ID du Sheet dans `app.py`

### **Erreur : "Authentication failed"**

**Solution :**
1. Vérifier que `credentials.json` est dans le bon dossier
2. Vérifier que les API sont activées sur Google Cloud

### **L'application ne se lance pas**

**Solution :**
```bash
# Vérifier que l'environnement est activé
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Vérifier que Streamlit est installé
pip list | grep streamlit

# Réinstaller si nécessaire
pip install streamlit
```

---

## 📈 ÉVOLUTIONS FUTURES

### **Phase 2 (Optionnel)**
- [ ] Export des rapports en PDF/Excel
- [ ] Historique des affectations
- [ ] Notifications par email
- [ ] Tableau de bord personnalisable
- [ ] Module de Machine Learning pour prédictions
- [ ] API REST pour intégration externe

---

## 👨‍💻 DÉVELOPPEMENT

### **Tests**

Tester les modules individuellement :

```bash
# Test data_manager
python data_manager.py

# Test algorithme
python algorithme.py
```

### **Logs**

Les logs sont affichés dans la console Streamlit.

---

## 📞 SUPPORT

### **Contact**

- **Étudiant** : [Votre Nom]
- **Email** : [Votre Email]
- **Institution** : ENCG Settat
- **Encadrant** : [Nom Encadrant]

---

## 📜 LICENCE

Projet académique - ENCG Settat  
© 2024 - Tous droits réservés

---

## 🙏 REMERCIEMENTS

- **PMBOK 7** pour le cadre méthodologique
- **Chefs de projet** ayant participé au questionnaire REX
- **Encadrants académiques** pour leur soutien
- **Google** pour l'API Sheets
- **Streamlit** pour le framework

---

## 📊 STATISTIQUES DU PROJET

- **Lignes de code** : ~2000 lignes Python
- **Modules** : 3 modules principaux
- **Pages** : 5 pages interactives
- **Fonctionnalités** : CRUD complet + Algorithme intelligent
- **Temps de développement** : 3-5 jours

---

**🎼 PMO Orchestre - Orchestrez vos projets IT avec intelligence ! 🎼**
