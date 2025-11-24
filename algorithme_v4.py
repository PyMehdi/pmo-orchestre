"""
Algorithme d'Affectation V4 - PMO Orchestre
============================================

VERSION 4 : Recalibrage échelle 5 plages (0, 0.2, 0.4, 0.6, 0.8, 1.0)

Modifications principales :
- Normalisation 3 plages → 5 plages
- Maturité client simplifiée (Engagement uniquement)
- Conversion ICM/ICC → heures/semaine
- Planification temporelle

Auteur : PFE - ENCG Settat
Projet : PMO Orchestre
Date : Novembre 2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math


# ========================================
# CONSTANTES DE CALIBRAGE V4
# ========================================

# Ratio de conversion points → heures/semaine
RATIO_CONVERSION = 0.4  # 1 point ICM/ICC = 0.4h/semaine
HEURES_SEMAINE_PLAFOND = 40  # Capacité maximale standard

# Seuils de normalisation (grilles 5 plages)
SEUILS_CHARGE_JH = [20, 50, 100, 200, 300]
SEUILS_BUDGET_MAD = [100000, 300000, 800000, 2000000, 5000000]
SEUILS_NB_INTERVENANTS = [3, 6, 11, 16, 25]
SEUILS_EXPERIENCE_ANNEES = [1, 3, 6, 11, 16]

# Coefficients score compatibilité
COEFF_ADEQUATION = 0.6  # α : Poids adéquation capacité/charge
COEFF_DISPONIBILITE = 0.3  # β : Poids disponibilité
COEFF_EXPERIENCE_SECTEUR = 0.1  # γ : Poids expérience sectorielle


# ========================================
# FONCTIONS DE NORMALISATION 5 PLAGES
# ========================================

def normaliser_parametre_5_plages(valeur: float, seuils: List[float]) -> float:
    """
    Normalise un paramètre sur échelle 0-1 avec 5 plages.
    
    Args:
        valeur: Valeur brute à normaliser
        seuils: Liste de 5 seuils [s1, s2, s3, s4, s5]
    
    Returns:
        Valeur normalisée : 0.0, 0.2, 0.4, 0.6, 0.8, ou 1.0
    
    Exemple:
        >>> normaliser_parametre_5_plages(75, [20, 50, 100, 200, 300])
        0.4  # Car 75 est dans plage [50-100] → plage 2 → 0.4
    """
    if valeur < seuils[0]:
        return 0.0
    elif valeur < seuils[1]:
        return 0.2
    elif valeur < seuils[2]:
        return 0.4
    elif valeur < seuils[3]:
        return 0.6
    elif valeur < seuils[4]:
        return 0.8
    else:
        return 1.0


def normaliser_echelle_1_5(valeur: int) -> float:
    """
    Convertit échelle 1-5 en 0-1 normalisé.
    
    Args:
        valeur: Note sur échelle 1-5
    
    Returns:
        Valeur normalisée 0-1
    
    Exemple:
        >>> normaliser_echelle_1_5(3)
        0.4  # (3-1) / (5-1) = 2/4 = 0.5 → arrondi à plage 0.4
    """
    if valeur <= 1:
        return 0.0
    elif valeur == 2:
        return 0.2
    elif valeur == 3:
        return 0.4
    elif valeur == 4:
        return 0.6
    else:  # valeur >= 5
        return 0.8


def extraire_nombre_texte(texte: str) -> int:
    """
    Extrait le nombre d'un texte format "X=Description".
    
    Args:
        texte: Format "4=Élevé" ou juste "4"
    
    Returns:
        Nombre extrait
    
    Exemple:
        >>> extraire_nombre_texte("4=Élevé")
        4
        >>> extraire_nombre_texte("3")
        3
    """
    if isinstance(texte, (int, float)):
        return int(texte)
    
    texte_str = str(texte).strip()
    if '=' in texte_str:
        return int(texte_str.split('=')[0])
    else:
        return int(texte_str)


# ========================================
# CONVERSIONS HEURES/SEMAINE
# ========================================

def icm_to_heures_semaine(icm: float) -> float:
    """Convertit ICM en heures/semaine."""
    return icm * RATIO_CONVERSION


def icc_to_heures_semaine(icc: float) -> float:
    """Convertit ICC en heures/semaine."""
    return icc * RATIO_CONVERSION


def heures_to_icm(heures: float) -> float:
    """Convertit heures/semaine en ICM."""
    return heures / RATIO_CONVERSION


def heures_to_icc(heures: float) -> float:
    """Convertit heures/semaine en ICC."""
    return heures / RATIO_CONVERSION


# ========================================
# CLASSE ALGORITHME AFFECTATION V4
# ========================================

class AlgorithmeAffectationV4:
    """
    Classe contenant tous les algorithmes d'affectation V4.
    """
    
    def __init__(self, ponderations: Dict):
        """
        Initialise l'algorithme avec les pondérations.
        
        Args:
            ponderations: Dict avec clés 'charge' et 'capacite'
                charge: Dict {parametre: poids%}
                capacite: Dict {parametre: poids%}
        """
        self.ponderations = ponderations
    
    # ========================================
    # CALCUL ICM (Indice Charge Managériale)
    # ========================================
    
    def calculer_icm(self, projet: Dict) -> float:
        """
        Calcule l'ICM d'un projet (version V4 - 5 plages).
        
        Args:
            projet: Dict avec clés:
                - Charge_JH (nombre)
                - Complexite_Tech (1-5 ou "X=Texte")
                - Budget_MAD (nombre)
                - Niveau_Risque (1-5 ou "X=Texte")
                - Nb_Intervenants (nombre)
                - Engagement_Client (1-5 ou "X=Texte")
                - Freq_Instances (1-5 ou "X=Texte")
                - Dispersion_Geo (1-5 ou "X=Texte")
        
        Returns:
            ICM sur échelle 0-100
        """
        poids = self.ponderations['charge']
        
        # Normaliser chaque paramètre
        charge_jh_norm = normaliser_parametre_5_plages(
            projet['Charge_JH'], 
            SEUILS_CHARGE_JH
        )
        
        complexite_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(projet['Complexite_Tech'])
        )
        
        budget_norm = normaliser_parametre_5_plages(
            projet['Budget_MAD'],
            SEUILS_BUDGET_MAD
        )
        
        risque_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(projet['Niveau_Risque'])
        )
        
        intervenants_norm = normaliser_parametre_5_plages(
            projet['Nb_Intervenants'],
            SEUILS_NB_INTERVENANTS
        )
        
        engagement_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(projet['Engagement_Client'])
        )
        
        freq_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(projet['Freq_Instances'])
        )
        
        dispersion_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(projet['Dispersion_Geo'])
        )
        
        # Calcul ICM
        icm = (
            charge_jh_norm * poids.get('Charge_JH', 19.75) +
            complexite_norm * poids.get('Complexite_Tech', 18.5) +
            budget_norm * poids.get('Budget', 14.9) +
            risque_norm * poids.get('Niveau_Risque', 16.8) +
            intervenants_norm * poids.get('Nb_Intervenants', 11.25) +
            engagement_norm * poids.get('Engagement_Client', 9.3) +
            freq_norm * poids.get('Freq_Instances', 4.65) +
            dispersion_norm * poids.get('Dispersion_Geo', 4.9)
        )
        
        return round(icm, 2)
    
    # ========================================
    # CALCUL ICC (Indice Capacité Chef)
    # ========================================
    
    def calculer_icc(self, chef: Dict) -> float:
        """
        Calcule l'ICC d'un chef (version V4 - 5 plages).
        
        Args:
            chef: Dict avec clés:
                - Competences_Mgmt (1-5 ou "X=Texte")
                - Annees_Experience (nombre)
                - Competences_Tech (1-5 ou "X=Texte")
                - Utilisation_IA (1-5 ou "X=Texte")
        
        Returns:
            ICC sur échelle 0-100
        """
        poids = self.ponderations['capacite']
        
        # Normaliser paramètres
        mgmt_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(chef['Competences_Mgmt'])
        )
        
        experience_norm = normaliser_parametre_5_plages(
            chef['Annees_Experience'],
            SEUILS_EXPERIENCE_ANNEES
        )
        
        tech_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(chef['Competences_Tech'])
        )
        
        ia_norm = normaliser_echelle_1_5(
            extraire_nombre_texte(chef['Utilisation_IA'])
        )
        
        # Calcul ICC
        icc = (
            mgmt_norm * poids.get('Competences_Mgmt', 35.0) +
            experience_norm * poids.get('Annees_Experience', 30.0) +
            tech_norm * poids.get('Competences_Tech', 25.0) +
            ia_norm * poids.get('Utilisation_IA', 10.0)
        )
        
        return round(icc, 2)
    
    # ========================================
    # TAUX D'UTILISATION
    # ========================================
    
    def calculer_taux_utilisation(
        self, 
        chef_id: str, 
        projets_df: pd.DataFrame,
        chefs_df: pd.DataFrame
    ) -> Dict:
        """
        Calcule le taux d'utilisation actuel d'un chef avec détails en heures.
        
        Args:
            chef_id: ID du chef
            projets_df: DataFrame des projets
            chefs_df: DataFrame des chefs
        
        Returns:
            Dict avec:
                - charge_icm: Charge totale en points ICM
                - charge_h_semaine: Charge en heures/semaine
                - capacite_icc: Capacité ICC
                - capacite_h_semaine: Capacité en heures/semaine
                - taux_pct: Taux utilisation en %
                - marge_icm: Marge disponible en points
                - marge_h_semaine: Marge en heures/semaine
                - surcharge: Boolean (True si taux > 100%)
                - details_projets: Liste détails projets actifs
        """
        # Récupérer ICC du chef
        chef = chefs_df[chefs_df['ID_Chef'] == chef_id].iloc[0]
        icc = chef.get('Capacite_Max', 100)
        capacite_h = icm_to_heures_semaine(icc)
        
        # Projets en cours du chef
        projets_chef = projets_df[
            (projets_df['Chef_Affecte'] == chef_id) & 
            (projets_df['Statut'] == 'En cours')
        ]
        
        # Charge actuelle
        charge_icm = projets_chef['Indice_Charge'].sum()
        charge_h = icm_to_heures_semaine(charge_icm)
        
        # Taux utilisation
        taux = (charge_h / capacite_h * 100) if capacite_h > 0 else 0
        
        # Détails projets
        details = []
        for _, p in projets_chef.iterrows():
            details.append({
                'nom': p['Nom_Projet'],
                'icm': p['Indice_Charge'],
                'h_semaine': icm_to_heures_semaine(p['Indice_Charge'])
            })
        
        return {
            'charge_icm': charge_icm,
            'charge_h_semaine': round(charge_h, 1),
            'capacite_icc': icc,
            'capacite_h_semaine': round(capacite_h, 1),
            'taux_pct': round(taux, 1),
            'marge_icm': icc - charge_icm,
            'marge_h_semaine': round(capacite_h - charge_h, 1),
            'surcharge': taux > 100,
            'details_projets': details
        }
    
    # ========================================
    # SCORE DE COMPATIBILITÉ
    # ========================================
    
    def calculer_score_compatibilite(
        self,
        projet: Dict,
        chef: Dict,
        taux_utilisation: float,
        experience_sectorielle: bool = False
    ) -> float:
        """
        Calcule le score de compatibilité chef/projet.
        
        Formule: S = α×(ICC/ICM) + β×(1-U) + γ×E
        
        Args:
            projet: Dict projet avec ICM
            chef: Dict chef avec ICC
            taux_utilisation: Taux actuel 0-1
            experience_sectorielle: Boolean
        
        Returns:
            Score 0-100
        """
        icc = chef.get('Capacite_Max', 100)
        icm = projet.get('Indice_Charge', 50)
        
        # Composante 1 : Adéquation (60%)
        adequation = COEFF_ADEQUATION * (icc / icm if icm > 0 else 0)
        
        # Composante 2 : Disponibilité (30%)
        disponibilite = COEFF_DISPONIBILITE * (1 - taux_utilisation)
        
        # Composante 3 : Expérience sectorielle (10%)
        bonus_exp = COEFF_EXPERIENCE_SECTEUR * (1 if experience_sectorielle else 0)
        
        score = (adequation + disponibilite + bonus_exp) * 100
        
        # Plafonner à 100
        return min(round(score, 1), 100.0)
    
    # ========================================
    # RECOMMANDATION AFFECTATION
    # ========================================
    
    def recommander_affectation(
        self,
        projet: Dict,
        chefs_df: pd.DataFrame,
        projets_df: pd.DataFrame,
        chef_favori_id: str = None
    ) -> List[Dict]:
        """
        Recommande les meilleurs chefs pour un projet.
        
        Args:
            projet: Dict projet à affecter
            chefs_df: DataFrame chefs
            projets_df: DataFrame projets
            chef_favori_id: ID du chef favori du client (bonus +10 points)
        
        Returns:
            Liste de Dict triée par score décroissant
        """
        recommendations = []
        icm_projet = projet['Indice_Charge']
        
        for _, chef in chefs_df.iterrows():
            # Calculer taux utilisation
            util = self.calculer_taux_utilisation(
                chef['ID_Chef'], 
                projets_df,
                chefs_df
            )
            
            # Vérifier expérience sectorielle (à implémenter selon vos données)
            exp_secteur = False  # TODO: logique métier
            
            # Calculer score
            score = self.calculer_score_compatibilite(
                projet,
                chef.to_dict(),
                util['taux_pct'] / 100,
                exp_secteur
            )
            
            # BONUS : Chef favori du client (+10 points)
            if chef_favori_id and chef['ID_Chef'] == chef_favori_id:
                score = min(score + 10, 100)  # Plafonné à 100
                is_favori = True
            else:
                is_favori = False
            
            # Charge future si affecté
            charge_future_h = util['charge_h_semaine'] + icm_to_heures_semaine(icm_projet)
            
            recommendations.append({
                'chef_id': chef['ID_Chef'],
                'chef_nom': chef['Nom_Prenom'],
                'icc': chef['Capacite_Max'],
                'icc_h_semaine': round(icc_to_heures_semaine(chef['Capacite_Max']), 1),
                'util_pct': util['taux_pct'],
                'charge_h_actuelle': util['charge_h_semaine'],
                'charge_h_future': round(charge_future_h, 1),
                'marge_h': round(HEURES_SEMAINE_PLAFOND - charge_future_h, 1),
                'surcharge': charge_future_h > HEURES_SEMAINE_PLAFOND,
                'score': score,
                'is_favori': is_favori,
                'projets_actuels': util['details_projets']
            })
        
        # Trier par score décroissant
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations


# ========================================
# FONCTIONS UTILITAIRES SUPPLÉMENTAIRES
# ========================================

def valider_affectation(
    chef_id: str,
    nouveau_projet_icm: float,
    projets_df: pd.DataFrame,
    chefs_df: pd.DataFrame
) -> Dict:
    """
    Valide qu'une affectation est réaliste en heures.
    
    Returns:
        Dict avec validation + alertes
    """
    algo = AlgorithmeAffectationV4({
        'charge': {},
        'capacite': {}
    })
    
    utilisation = algo.calculer_taux_utilisation(chef_id, projets_df, chefs_df)
    
    nouveau_projet_h = icm_to_heures_semaine(nouveau_projet_icm)
    charge_future_h = utilisation['charge_h_semaine'] + nouveau_projet_h
    
    # Alertes progressives
    alertes = []
    
    if charge_future_h > HEURES_SEMAINE_PLAFOND:
        alertes.append({
            'niveau': 'CRITIQUE',
            'message': f'Surcharge : {charge_future_h:.1f}h/semaine (>40h plafond)'
        })
    elif charge_future_h > 36:
        alertes.append({
            'niveau': 'ATTENTION',
            'message': f'Proche saturation : {charge_future_h:.1f}h/semaine'
        })
    elif charge_future_h > 30:
        alertes.append({
            'niveau': 'INFO',
            'message': f'Utilisation élevée : {charge_future_h:.1f}h/semaine'
        })
    
    return {
        'valide': charge_future_h <= HEURES_SEMAINE_PLAFOND,
        'charge_actuelle_h': utilisation['charge_h_semaine'],
        'nouveau_projet_h': round(nouveau_projet_h, 1),
        'charge_future_h': round(charge_future_h, 1),
        'marge_h': round(HEURES_SEMAINE_PLAFOND - charge_future_h, 1),
        'alertes': alertes
    }
