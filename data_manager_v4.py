"""
Data Manager V4 - Gestion des données Google Sheets
====================================================

VERSION 4 : Support structure V4 (5 plages, Engagement_Client unique)

Auteur : PFE - ENCG Settat
Projet : PMO Orchestre
Date : Novembre 2025
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import sys


class DataManagerV4:
    """
    Gestionnaire de données V4 pour Google Sheets.
    
    Gère la connexion et les opérations CRUD sur les feuilles :
    - Projets
    - Chefs_Projet  
    - Ponderations
    - Planification_Hebdo
    """
    
    def __init__(self, credentials_file: str, sheet_id: str):
        """
        Initialise la connexion à Google Sheets.
        
        Args:
            credentials_file: Chemin vers le fichier credentials.json
            sheet_id: ID du Google Sheet
        """
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.client = None
        self.spreadsheet = None
        self._connect()
    
    def _connect(self):
        """Établit la connexion avec Google Sheets."""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, 
                scope
            )
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
            print("✅ Connexion Google Sheets établie")
        except Exception as e:
            print(f"❌ Erreur de connexion : {str(e)}")
            print(f"   Vérifiez : credentials_file='{self.credentials_file}'")
            print(f"   Vérifiez : sheet_id='{self.sheet_id}'")
            sys.exit(1)
    
    # ========================================
    # GESTION DES PROJETS
    # ========================================
    
    def get_projets(self) -> pd.DataFrame:
        """
        Récupère tous les projets depuis Google Sheets.
        
        Returns:
            DataFrame avec colonnes V4 :
                ID_Projet, Nom_Projet, ID_Client, Statut, Budget_MAD,
                Charge_JH, Complexite_Tech, Niveau_Risque, Nb_Intervenants,
                Engagement_Client, Freq_Instances, Dispersion_Geo,
                Indice_Charge, ICM_H_Semaine, Chef_Affecte,
                Date_Debut, Date_Fin_Prev, Duree_Semaines, Commentaires,
                CPI, SPI, KPI Facturation
        """
        try:
            ws = self.spreadsheet.worksheet('Projets')
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            # Nettoyer les lignes vides
            if 'ID_Projet' in df.columns:
                df = df[df['ID_Projet'] != '']
            
            # Convertir types numériques
            colonnes_numeriques = [
                'Budget_MAD', 'Charge_JH', 'Nb_Intervenants',
                'Indice_Charge', 'ICM_H_Semaine', 'Duree_Semaines',
                'CPI', 'SPI', 'KPI Facturation'
            ]
            for col in colonnes_numeriques:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Convertir dates
            colonnes_dates = ['Date_Debut', 'Date_Fin_Prev']
            for col in colonnes_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
        except Exception as e:
            print(f"❌ Erreur lecture projets : {str(e)}")
            return pd.DataFrame()
    
    def get_projet_by_id(self, projet_id: str) -> Optional[Dict]:
        """
        Récupère un projet par son ID.
        
        Args:
            projet_id: ID du projet
        
        Returns:
            Dict avec données projet ou None
        """
        df = self.get_projets()
        projet = df[df['ID_Projet'] == projet_id]
        
        if len(projet) > 0:
            return projet.iloc[0].to_dict()
        return None
    
    def get_projets_non_affectes(self) -> pd.DataFrame:
        """Récupère les projets sans chef affecté."""
        df = self.get_projets()
        return df[
            (df['Chef_Affecte'].isna()) | 
            (df['Chef_Affecte'] == '') |
            (df['Chef_Affecte'] == 'Non affecté')
        ]
    
    def get_projets_en_cours(self) -> pd.DataFrame:
        """Récupère les projets en cours."""
        df = self.get_projets()
        return df[df['Statut'] == 'En cours']
    
    def affecter_projet(self, projet_id: str, chef_id: str) -> bool:
        """
        Affecte un chef à un projet et change le statut à "Actif".
        
        Args:
            projet_id: ID du projet
            chef_id: ID du chef
        
        Returns:
            True si succès, False sinon
        """
        try:
            ws = self.spreadsheet.worksheet('Projets')
            
            # Trouver la ligne du projet
            cell = ws.find(projet_id)
            if cell is None:
                print(f"❌ Projet {projet_id} introuvable")
                return False
            
            row = cell.row
            
            # Trouver les colonnes dynamiquement
            headers = ws.row_values(1)
            
            try:
                col_chef = headers.index('Chef_Affecte') + 1
                col_statut = headers.index('Statut') + 1
            except ValueError as e:
                print(f"❌ Colonne introuvable : {str(e)}")
                return False
            
            # Mettre à jour Chef ET Statut
            ws.update_cell(row, col_chef, chef_id)
            ws.update_cell(row, col_statut, 'Actif')
            
            print(f"✅ Projet {projet_id} affecté à {chef_id} (Statut: Actif)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur affectation : {str(e)}")
            return False
    
    # ========================================
    # GESTION DES CLIENTS
    # ========================================
    
    def get_clients(self) -> pd.DataFrame:
        """
        Récupère tous les clients depuis Google Sheets.
        
        Returns:
            DataFrame avec colonnes :
                ID_Client, Nom_Client, Chef_Favori, etc.
        """
        try:
            ws = self.spreadsheet.worksheet('Clients')
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            # Nettoyer les lignes vides
            if 'ID_Client' in df.columns:
                df = df[df['ID_Client'] != '']
            
            return df
        except Exception as e:
            print(f"❌ Erreur lecture clients : {str(e)}")
            return pd.DataFrame()
    
    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """
        Récupère un client par son ID.
        
        Args:
            client_id: ID du client
        
        Returns:
            Dict avec données client ou None
        """
        df = self.get_clients()
        client = df[df['ID_Client'] == client_id]
        
        if len(client) > 0:
            return client.iloc[0].to_dict()
        return None
    
    # ========================================
    # GESTION DES CHEFS
    # ========================================
    
    def get_chefs(self) -> pd.DataFrame:
        """
        Récupère tous les chefs depuis Google Sheets.
        
        Returns:
            DataFrame avec colonnes V4 :
                ID_Chef, Nom_Prenom, Email, Statut, Annees_Experience,
                Nb_Projets_Geres, Competences_Tech, Competences_Mgmt,
                Utilisation_IA, Secteurs_Expertise, Methodologies,
                Capacite_Max, ICC_H_Semaine, Capacite_Plafond_H,
                Charge_Actuelle, Taux_Charge_Pct, Projets_Actifs,
                Date_Embauche, Commentaires
        """
        try:
            ws = self.spreadsheet.worksheet('Chefs_Projets')
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            # Nettoyer les lignes vides
            if 'ID_Chef' in df.columns:
                df = df[df['ID_Chef'] != '']
            
            # Convertir types numériques
            colonnes_numeriques = [
                'Annees_Experience', 'Nb_Projets_Geres',
                'Capacite_Max', 'ICC_H_Semaine', 'Capacite_Plafond_H',
                'Charge_Actuelle', 'Taux_Charge_Pct', 'Projets_Actifs'
            ]
            for col in colonnes_numeriques:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Convertir dates
            if 'Date_Embauche' in df.columns:
                df['Date_Embauche'] = pd.to_datetime(df['Date_Embauche'], errors='coerce')
            
            return df
        except Exception as e:
            print(f"❌ Erreur lecture chefs : {str(e)}")
            return pd.DataFrame()
    
    def get_chef_by_id(self, chef_id: str) -> Optional[Dict]:
        """
        Récupère un chef par son ID.
        
        Args:
            chef_id: ID du chef
        
        Returns:
            Dict avec données chef ou None
        """
        df = self.get_chefs()
        chef = df[df['ID_Chef'] == chef_id]
        
        if len(chef) > 0:
            return chef.iloc[0].to_dict()
        return None
    
    def get_chefs_disponibles(self, seuil_pct: float = 80) -> pd.DataFrame:
        """
        Récupère les chefs disponibles (taux < seuil).
        
        Args:
            seuil_pct: Seuil de disponibilité (défaut 80%)
        
        Returns:
            DataFrame chefs disponibles
        """
        df = self.get_chefs()
        return df[df['Taux_Charge_Pct'] < seuil_pct]
    
    # ========================================
    # GESTION DES PONDÉRATIONS
    # ========================================
    
    def get_ponderations(self) -> Dict:
        """
        Récupère les pondérations depuis Google Sheets.
        
        Returns:
            Dict avec structure :
            {
                'charge': {parametre: poids_moyen},
                'capacite': {parametre: poids}
            }
        """
        try:
            ws = self.spreadsheet.worksheet('Ponderations')
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            # Structure retour
            ponderations = {
                'charge': {},
                'capacite': {}
            }
            
            # Paramètres charge (projets)
            params_charge = [
                'Charge_JH', 'Complexite_Tech', 'Budget', 'Niveau_Risque',
                'Nb_Intervenants', 'Engagement_Client', 'Freq_Instances', 
                'Dispersion_Geo'
            ]
            
            for param in params_charge:
                row = df[df['Paramètre'] == param]
                if len(row) > 0:
                    # Utiliser Poids_Moyen (colonne D)
                    poids = row.iloc[0].get('Poids_Moyen', 0)
                    ponderations['charge'][param] = float(poids)
            
            # Paramètres capacité (chefs) - À définir si besoin
            # Pour l'instant, valeurs par défaut
            ponderations['capacite'] = {
                'Competences_Mgmt': 35.0,
                'Annees_Experience': 30.0,
                'Competences_Tech': 25.0,
                'Utilisation_IA': 10.0
            }
            
            return ponderations
            
        except Exception as e:
            print(f"❌ Erreur lecture pondérations : {str(e)}")
            # Valeurs par défaut
            return {
                'charge': {
                    'Charge_JH': 19.75,
                    'Complexite_Tech': 18.5,
                    'Budget': 14.9,
                    'Niveau_Risque': 16.8,
                    'Nb_Intervenants': 11.25,
                    'Engagement_Client': 9.3,
                    'Freq_Instances': 4.65,
                    'Dispersion_Geo': 4.9
                },
                'capacite': {
                    'Competences_Mgmt': 35.0,
                    'Annees_Experience': 30.0,
                    'Competences_Tech': 25.0,
                    'Utilisation_IA': 10.0
                }
            }
    
    # ========================================
    # PLANIFICATION HEBDOMADAIRE
    # ========================================
    
    def get_planification_hebdo(self) -> pd.DataFrame:
        """
        Récupère la planification hebdomadaire.
        
        Returns:
            DataFrame avec colonnes :
                Semaine, Annee, Date, Chef_ID, Projet_ID, 
                Projet_Nom, ICM, Charge_H
        """
        try:
            ws = self.spreadsheet.worksheet('Planification_Hebdo')
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            
            # Convertir types
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            colonnes_num = ['Semaine', 'Annee', 'ICM', 'Charge_H']
            for col in colonnes_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        except Exception as e:
            print(f"⚠️ Planification_Hebdo non accessible : {str(e)}")
            return pd.DataFrame()
    
    def generer_planification_hebdo(
        self, 
        nb_semaines: int = 12
    ) -> pd.DataFrame:
        """
        Génère la planification pour les N prochaines semaines.
        
        Args:
            nb_semaines: Nombre de semaines à générer
        
        Returns:
            DataFrame planification
        """
        projets_df = self.get_projets()
        planning = []
        today = datetime.today()
        
        # Filtrer projets en cours ou à venir
        projets_actifs = projets_df[
            projets_df['Statut'].isin(['En cours', 'Planifié'])
        ].copy()
        
        for i in range(nb_semaines):
            semaine_date = today + timedelta(weeks=i)
            semaine_num = semaine_date.isocalendar()[1]
            annee = semaine_date.year
            
            for _, projet in projets_actifs.iterrows():
                # Vérifier si projet actif cette semaine
                date_debut = pd.to_datetime(projet.get('Date_Debut'))
                date_fin = pd.to_datetime(projet.get('Date_Fin_Prev'))
                
                if pd.isna(date_debut) or pd.isna(date_fin):
                    continue
                
                if date_debut <= semaine_date <= date_fin:
                    chef_id = projet.get('Chef_Affecte', '')
                    if chef_id and chef_id != '' and chef_id != 'Non affecté':
                        planning.append({
                            'Semaine': semaine_num,
                            'Annee': annee,
                            'Date': semaine_date,
                            'Chef_ID': chef_id,
                            'Projet_ID': projet['ID_Projet'],
                            'Projet_Nom': projet['Nom_Projet'],
                            'ICM': projet.get('Indice_Charge', 0),
                            'Charge_H': projet.get('ICM_H_Semaine', 0)
                        })
        
        return pd.DataFrame(planning)
    
    def sauvegarder_planification_hebdo(self, planning_df: pd.DataFrame) -> bool:
        """
        Sauvegarde la planification dans Google Sheets.
        
        Args:
            planning_df: DataFrame planification
        
        Returns:
            True si succès
        """
        try:
            ws = self.spreadsheet.worksheet('Planification_Hebdo')
            
            # Effacer contenu existant (sauf en-têtes)
            ws.clear()
            
            # Écrire en-têtes
            headers = [
                'Semaine', 'Annee', 'Date', 'Chef_ID', 
                'Projet_ID', 'Projet_Nom', 'ICM', 'Charge_H'
            ]
            ws.append_row(headers)
            
            # Écrire données
            for _, row in planning_df.iterrows():
                ws.append_row([
                    int(row['Semaine']),
                    int(row['Annee']),
                    row['Date'].strftime('%Y-%m-%d') if pd.notna(row['Date']) else '',
                    str(row['Chef_ID']),
                    str(row['Projet_ID']),
                    str(row['Projet_Nom']),
                    float(row['ICM']),
                    float(row['Charge_H'])
                ])
            
            print(f"✅ Planification sauvegardée ({len(planning_df)} lignes)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde planification : {str(e)}")
            return False
    
    # ========================================
    # UTILITAIRES
    # ========================================
    
    def refresh_connection(self):
        """Rafraîchit la connexion Google Sheets."""
        self._connect()
    
    def get_spreadsheet_url(self) -> str:
        """Retourne l'URL du Google Sheet."""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
    
    def test_connection(self) -> bool:
        """Teste la connexion et l'accès aux feuilles."""
        try:
            print("\n🔍 Test de connexion...")
            print(f"   URL: {self.get_spreadsheet_url()}")
            
            # Lister feuilles
            worksheets = self.spreadsheet.worksheets()
            print(f"\n✅ Feuilles disponibles ({len(worksheets)}) :")
            for ws in worksheets:
                print(f"   • {ws.title}")
            
            # Test lecture
            print("\n📊 Test lecture données...")
            projets = self.get_projets()
            chefs = self.get_chefs()
            ponderations = self.get_ponderations()
            
            print(f"   • Projets : {len(projets)} lignes")
            print(f"   • Chefs : {len(chefs)} lignes")
            print(f"   • Pondérations charge : {len(ponderations['charge'])} paramètres")
            
            print("\n✅ Connexion opérationnelle !")
            return True
            
        except Exception as e:
            print(f"\n❌ Erreur test connexion : {str(e)}")
            return False


# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def init_data_manager(credentials_file: str = None, sheet_id: str = None) -> DataManagerV4:
    """
    Initialise le DataManager avec credentials par défaut si non fournis.
    
    Args:
        credentials_file: Chemin credentials.json (optionnel)
        sheet_id: ID Google Sheet (optionnel)
    
    Returns:
        Instance DataManagerV4
    """
    # Valeurs par défaut (à adapter)
    if credentials_file is None:
        credentials_file = '/home/claude/credentials.json'
    
    if sheet_id is None:
        # Votre SHEET_ID par défaut
        sheet_id = '1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs'
    
    return DataManagerV4(credentials_file, sheet_id)
