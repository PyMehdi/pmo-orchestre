"""
Application Streamlit V4 - PMO Orchestre
=========================================

Interface web pour l'affectation intelligente des chefs de projet.

VERSION 4 : Recalibrage 5 plages + Visualisation temporelle

Auteur : PFE - ENCG Settat
Date : Novembre 2025
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys

# Plotly désactivé (non installé dans cet environnement)
# import plotly.graph_objects as go
# import plotly.express as px

# Imports locaux
sys.path.append('/home/claude')
from data_manager_v4 import DataManagerV4, init_data_manager
from algorithme_v4 import AlgorithmeAffectationV4, icm_to_heures_semaine, icc_to_heures_semaine


# ========================================
# CONFIGURATION PAGE
# ========================================

st.set_page_config(
    page_title="PMO Orchestre V4",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ========================================
# INITIALISATION SESSION
# ========================================

# Pas de cache pour permettre les mises à jour
def get_data_manager():
    """Initialise le DataManager (sans cache pour permettre affectations)."""
    return init_data_manager(
        credentials_file='/Users/mac/Documents/DSMIA_PFE/PMO_Orchestre/credentials.json',
        sheet_id='1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs'
    )

def init_session_state():
    """Initialise les variables de session."""
    if 'page' not in st.session_state:
        st.session_state.page = 'Dashboard'
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()


# ========================================
# FONCTIONS UTILITAIRES
# ========================================

def get_color_taux(taux_pct: float) -> str:
    """Retourne couleur selon taux utilisation."""
    if taux_pct >= 100:
        return '🔴'
    elif taux_pct >= 90:
        return '🟠'
    elif taux_pct >= 70:
        return '🟡'
    else:
        return '🟢'


def format_duree(semaines: float) -> str:
    """Formate une durée en semaines."""
    if pd.isna(semaines):
        return "N/A"
    return f"{semaines:.1f} sem"


# ========================================
# PAGE : DASHBOARD
# ========================================

def page_dashboard():
    """Page tableau de bord principal."""
    st.title("📊 Dashboard PMO")
    
    dm = get_data_manager()
    projets = dm.get_projets()
    chefs = dm.get_chefs()
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Gestion colonne Statut manquante
        nb_en_cours = 0
        if 'Statut' in projets.columns:
            nb_en_cours = len(projets[projets['Statut']=='Actif'])
        st.metric(
            "Total Projets",
            len(projets),
            delta=f"{nb_en_cours} en cours"
        )
    
    with col2:
        # Compter chefs actifs correctement
        nb_actifs = len(chefs)  # Tous les chefs récupérés sont actifs
        st.metric(
            "Total Chefs",
            len(chefs),
            delta=f"{nb_actifs} actifs"
        )
    
    with col3:
        # Gestion Chef_Affecte manquant
        projets_non_affectes = 0
        if 'Chef_Affecte' in projets.columns:
            projets_non_affectes = len(projets[
                (projets['Chef_Affecte'].isna()) | 
                (projets['Chef_Affecte'] == '') |
                (projets['Chef_Affecte'] == 'Non affecté')
            ])
        st.metric(
            "Non affectés",
            projets_non_affectes,
            delta="À traiter" if projets_non_affectes > 0 else "OK"
        )
    
    with col4:
        # Recalculer charge moyenne depuis les projets réels
        charges_reelles = []
        for _, chef in chefs.iterrows():
            chef_id = chef['ID_Chef']
            icc = chef.get('Capacite_Max', 100)
            
            # Somme ICM des projets actifs
            charge_icm = projets[
                (projets['Chef_Affecte'] == chef_id) & 
                (projets['Statut'] == 'Actif')
            ]['Indice_Charge'].sum()
            
            taux = (charge_icm / icc * 100) if icc > 0 else 0
            charges_reelles.append(taux)
        
        charge_moy = sum(charges_reelles) / len(charges_reelles) if charges_reelles else 0
        
        st.metric(
            "Charge moyenne",
            f"{charge_moy:.0f}%",
            delta="OK" if charge_moy < 80 else "Élevé"
        )
    
    st.markdown("---")
    
    # Graphique synthèse chefs
    st.subheader("📊 Vue d'ensemble des chefs")
    
    # Calculer métriques réelles pour chaque chef
    chefs_summary = chefs.copy()
    
    for idx, chef in chefs_summary.iterrows():
        chef_id = chef['ID_Chef']
        
        # Compter projets actifs réels
        nb_projets = len(projets[
            (projets['Chef_Affecte'] == chef_id) & 
            (projets['Statut'] == 'Actif')
        ])
        
        # Calculer charge réelle
        charge_icm = projets[
            (projets['Chef_Affecte'] == chef_id) & 
            (projets['Statut'] == 'Actif')
        ]['Indice_Charge'].sum()
        
        charge_h = charge_icm * 0.4
        
        # Calculer taux réel
        icc = chef['Capacite_Max']
        taux_reel = (charge_icm / icc * 100) if icc > 0 else 0
        
        # Mettre à jour
        chefs_summary.at[idx, 'Projets_Actifs'] = nb_projets
        chefs_summary.at[idx, 'Charge_H'] = charge_h
        chefs_summary.at[idx, 'Taux_Calc'] = taux_reel
    
    # Tableau synthèse
    df_summary_display = chefs_summary[['Nom_Prenom', 'Charge_H', 'Projets_Actifs', 'Taux_Calc']].copy()
    df_summary_display['Charge_H'] = df_summary_display['Charge_H'].apply(lambda x: f"{x:.1f}")
    df_summary_display['Taux_Calc'] = df_summary_display['Taux_Calc'].apply(lambda x: f"{x:.0f}%")
    
    st.dataframe(
        df_summary_display.rename(columns={
            'Nom_Prenom': 'Chef',
            'Charge_H': 'Charge (h/sem)',
            'Projets_Actifs': 'Nb Projets',
            'Taux_Calc': 'Taux'
        }),
        width='stretch',
        hide_index=True
    )
    
    st.markdown("---")
    
    # Utilisation des chefs
    st.subheader("👥 Utilisation des chefs de projet")
    
    for _, chef in chefs_summary.iterrows():
        # Vérifier si Statut existe
        if 'Statut' in chef.index and chef.get('Statut') != 'Actif':
            continue
        
        # Utiliser taux calculé
        taux = chef.get('Taux_Calc', 0)
        couleur = get_color_taux(taux)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.write(f"**{chef['Nom_Prenom']}**")
        
        with col2:
            st.progress(min(taux / 100, 1.0))
            st.caption(f"{taux:.0f}%")
        
        with col3:
            # Gestion ICC_H_Semaine manquante (calculer si besoin)
            icc = chef.get('Capacite_Max', 0)
            if 'ICC_H_Semaine' in chef.index:
                icc_h = chef.get('ICC_H_Semaine', 0)
            else:
                icc_h = icc * 0.4  # Conversion automatique
            
            charge_h = chef.get('Charge_H', 0)
            st.metric(
                "Charge",
                f"{charge_h:.1f}h/sem",
                delta=f"{icc_h - charge_h:.1f}h dispo"
            )
        
        with col4:
            st.metric(
                "Projets",
                int(chef.get('Projets_Actifs', 0))
            )
        
        # Détail projets (expander)
        projets_chef = projets[
            (projets['Chef_Affecte'] == chef['ID_Chef']) &
            (projets['Statut'] == 'Actif')
        ]
        
        if len(projets_chef) > 0:
            with st.expander(f"{couleur} Détail projets"):
                for _, p in projets_chef.iterrows():
                    icm_h = p.get('ICM_H_Semaine', 0)
                    # Récupérer nom client
                    client_id = p.get('ID_Client', '')
                    client = dm.get_client_by_id(client_id)
                    client_nom = client.get('Nom_Client', client_id) if client else client_id
                    
                    st.write(f"• **{p['ID_Projet']}** - {client_nom} - {p['Nom_Projet']} : {p['Indice_Charge']:.0f} pts ({icm_h:.1f}h/sem)")


# ========================================
# PAGE : AFFECTATION INTELLIGENTE
# ========================================

def page_affectation():
    """Page d'affectation intelligente."""
    st.title("🤖 Affectation Intelligente")
    
    dm = get_data_manager()
    projets = dm.get_projets()
    chefs = dm.get_chefs()
    ponderations = dm.get_ponderations()
    
    # Sélection projet avec ID et Client
    projets_non_affectes = dm.get_projets_non_affectes()
    
    if len(projets_non_affectes) == 0:
        st.info("✅ Tous les projets sont affectés !")
        return
    
    # Créer liste affichage avec ID + Client + Nom
    projets_options = []
    for _, p in projets_non_affectes.iterrows():
        option = f"{p['ID_Projet']} - {p.get('ID_Client', 'N/A')} - {p['Nom_Projet']}"
        projets_options.append(option)
    
    projet_selection = st.selectbox(
        "📌 Projet à affecter",
        projets_options
    )
    
    # Extraire ID_Projet de la sélection
    projet_id = projet_selection.split(' - ')[0]
    projet = projets[projets['ID_Projet'] == projet_id].iloc[0].to_dict()
    
    # Affichage projet
    col1, col2, col3 = st.columns(3)
    
    # Récupérer infos client
    client_id = projet.get('ID_Client', '')
    client = dm.get_client_by_id(client_id)
    client_nom = client.get('Nom_Client', client_id) if client else client_id
    chef_favori_id = client.get('Chef_Favori', '') if client else ''
    
    # Afficher infos projet + client
    st.info(f"📋 **Client :** {client_nom} ({client_id})")
    
    if chef_favori_id:
        chef_fav = chefs[chefs['ID_Chef'] == chef_favori_id]
        if len(chef_fav) > 0:
            chef_favori_nom = chef_fav.iloc[0]['Nom_Prenom']
            st.success(f"⭐ **Chef favori du client :** {chef_favori_nom} ({chef_favori_id})")
    
    with col1:
        st.metric("ICM", f"{projet['Indice_Charge']:.0f} pts")
    with col2:
        # Gestion ICM_H_Semaine manquante
        if 'ICM_H_Semaine' in projet:
            icm_h = projet.get('ICM_H_Semaine', 0)
        else:
            icm_h = projet.get('Indice_Charge', 0) * 0.4
        st.metric("Charge/semaine", f"{icm_h:.1f}h")
    with col3:
        duree = projet.get('Duree_Semaines', 0)
        st.metric("Durée", format_duree(duree))
    
    st.markdown("---")
    
    # Bouton recommandation
    if st.button("🔍 Obtenir Recommandations", type="primary"):
        with st.spinner("Calcul en cours..."):
            algo = AlgorithmeAffectationV4(ponderations)
            
            # Récupérer client et son chef favori
            client_id = projet.get('ID_Client')
            chef_favori_id = None
            chef_favori_nom = None
            
            if client_id:
                client = dm.get_client_by_id(client_id)
                if client and 'Chef_Favori' in client:
                    chef_favori_id = client.get('Chef_Favori')
                    # Récupérer nom du chef favori
                    if chef_favori_id:
                        chef_fav = chefs[chefs['ID_Chef'] == chef_favori_id]
                        if len(chef_fav) > 0:
                            chef_favori_nom = chef_fav.iloc[0]['Nom_Prenom']
                            st.success(f"⭐ **Chef favori du client :** {chef_favori_nom} ({chef_favori_id})")
            
            recommendations = algo.recommander_affectation(
                projet, chefs, projets, chef_favori_id=chef_favori_id
            )
            st.session_state['recommendations'] = recommendations
            st.session_state['projet_actuel'] = projet
    
    # Afficher recommandations si elles existent
    if 'recommendations' in st.session_state and st.session_state['recommendations']:
        recommendations = st.session_state['recommendations']
        projet = st.session_state['projet_actuel']
        
        st.subheader("🏆 Top 3 Recommandations")
        
        for i, reco in enumerate(recommendations[:3], 1):
            # Bouton d'affectation directement visible
            col_btn1, col_btn2 = st.columns([3, 1])
            
            with col_btn1:
                # Badge chef favori
                favori_badge = " ⭐ **CHEF FAVORI CLIENT**" if reco.get('is_favori', False) else ""
                st.write(f"**#{i} - {reco['chef_nom']}** (Score {reco['score']:.0f}/100){favori_badge}")
            
            with col_btn2:
                btn_key = f"affecter_{projet['ID_Projet']}_{reco['chef_id']}_{i}"
                
                if st.button(f"✅ Affecter", key=btn_key, type="primary" if i==1 else "secondary"):
                    if not reco['surcharge']:
                        with st.spinner("Affectation en cours..."):
                            dm_temp = get_data_manager()
                            success = dm_temp.affecter_projet(
                                projet['ID_Projet'],
                                reco['chef_id']
                            )
                            
                            if success:
                                st.success(f"✅ Projet affecté à {reco['chef_nom']} !")
                                st.balloons()
                                # Nettoyer session state
                                if 'recommendations' in st.session_state:
                                    del st.session_state['recommendations']
                                if 'projet_actuel' in st.session_state:
                                    del st.session_state['projet_actuel']
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de l'affectation")
                    else:
                        st.error(f"❌ Surcharge ! {reco['chef_nom']} dépasserait 40h/sem")
            
            # Détails dans expander (lecture seule)
            with st.expander(f"Détails #{i}", expanded=(i == 1)):
                # Métriques
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "ICC",
                        f"{reco['icc']:.0f} pts",
                        delta=f"{reco['icc_h_semaine']:.1f}h/sem capacité"
                    )
                
                with col2:
                    # Calculer utilisation réelle depuis projets actifs
                    chef_id = reco['chef_id']
                    charge_icm_reel = projets[
                        (projets['Chef_Affecte'] == chef_id) & 
                        (projets['Statut'] == 'Actif')
                    ]['Indice_Charge'].sum()
                    
                    icc = reco['icc']
                    util_reel = (charge_icm_reel / icc * 100) if icc > 0 else 0
                    charge_h_reel = charge_icm_reel * 0.4
                    
                    st.metric(
                        "Utilisation actuelle",
                        f"{util_reel:.0f}%",
                        delta=f"{charge_h_reel:.1f}h/sem"
                    )
                
                with col3:
                    delta_couleur = "inverse" if reco['surcharge'] else "normal"
                    st.metric(
                        "Charge si affecté",
                        f"{reco['charge_h_future']:.1f}h/sem",
                        delta=f"{reco['marge_h']:.1f}h marge",
                        delta_color=delta_couleur
                    )
                
                # Alerte surcharge
                if reco['surcharge']:
                    st.error(f"🔴 **SURCHARGE !** {reco['charge_h_future']:.1f}h/sem (>40h)")
                elif reco['charge_h_future'] > 36:
                    st.warning(f"⚠️ Proche saturation ({reco['charge_h_future']:.1f}h/sem)")
                
                # Projets actuels
                if len(reco['projets_actuels']) > 0:
                    st.caption("**Projets en cours :**")
                    for p in reco['projets_actuels']:
                        st.caption(f"• {p['nom']} : {p['icm']:.0f} pts ({p['h_semaine']:.1f}h/sem)")
            
            st.markdown("---")  # Séparateur entre recommandations


# ========================================
# PAGE : PROJETS
# ========================================

def page_projets():
    """Page liste des projets."""
    st.title("📁 Gestion des Projets")
    
    dm = get_data_manager()
    projets = dm.get_projets()
    chefs = dm.get_chefs()  # Charger les chefs pour afficher noms
    
    # Filtres
    col1, col2 = st.columns(2)
    
    with col1:
        statut_filtre = st.multiselect(
            "Statut",
            options=projets['Statut'].unique().tolist(),
            default=['Actif']
        )
    
    with col2:
        chef_filtre = st.multiselect(
            "Chef affecté",
            options=projets['Chef_Affecte'].unique().tolist()
        )
    
    # Appliquer filtres
    df_filtre = projets.copy()
    if statut_filtre:
        df_filtre = df_filtre[df_filtre['Statut'].isin(statut_filtre)]
    if chef_filtre:
        df_filtre = df_filtre[df_filtre['Chef_Affecte'].isin(chef_filtre)]
    
    # Affichage tableau
    colonnes_affichees = ['ID_Projet', 'Nom_Projet', 'Statut', 'Indice_Charge', 
                          'ICM_H_Semaine', 'Chef_Affecte', 'Date_Debut', 
                          'Date_Fin_Prev', 'CPI', 'SPI', 'KPI Facturation']
    
    # Vérifier quelles colonnes existent
    colonnes_disponibles = [col for col in colonnes_affichees if col in df_filtre.columns]
    
    # Créer copie pour affichage avec nom client
    df_display = df_filtre[colonnes_disponibles].copy()
    
    # Ajouter colonne Nom_Client
    df_display.insert(2, 'Nom_Client', df_filtre['ID_Client'].apply(
        lambda x: dm.get_client_by_id(x).get('Nom_Client', x) if dm.get_client_by_id(x) else x
    ))
    
    # Remplacer Chef_Affecte (ID) par Nom du chef
    if 'Chef_Affecte' in df_display.columns:
        df_display['Nom_Chef'] = df_display['Chef_Affecte'].apply(
            lambda x: chefs[chefs['ID_Chef'] == x]['Nom_Prenom'].iloc[0] if len(chefs[chefs['ID_Chef'] == x]) > 0 else x
        )
        # Insérer après Chef_Affecte
        idx = list(df_display.columns).index('Chef_Affecte')
        cols = list(df_display.columns)
        cols.remove('Nom_Chef')
        cols.insert(idx + 1, 'Nom_Chef')
        df_display = df_display[cols]
    
    # Formater dates sans heure
    for col in ['Date_Debut', 'Date_Fin_Prev']:
        if col in df_display.columns:
            df_display[col] = pd.to_datetime(df_display[col], errors='coerce').dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_display,
        width='stretch',
        hide_index=True
    )
    
    st.caption(f"**{len(df_filtre)}** projet(s) affiché(s)")


# ========================================
# PAGE : CHEFS
# ========================================

def page_chefs():
    """Page liste des chefs."""
    st.title("👥 Gestion des Chefs de Projet")
    
    dm = get_data_manager()
    chefs = dm.get_chefs()
    projets = dm.get_projets()
    
    # Calculer métriques réelles pour chaque chef
    chefs_display = chefs.copy()
    
    for idx, chef in chefs_display.iterrows():
        chef_id = chef['ID_Chef']
        
        # Compter projets actifs réels
        nb_projets = len(projets[
            (projets['Chef_Affecte'] == chef_id) & 
            (projets['Statut'] == 'Actif')
        ])
        
        # Calculer charge réelle
        charge_icm = projets[
            (projets['Chef_Affecte'] == chef_id) & 
            (projets['Statut'] == 'Actif')
        ]['Indice_Charge'].sum()
        
        # Calculer taux réel
        icc = chef['Capacite_Max']
        taux_reel = (charge_icm / icc * 100) if icc > 0 else 0
        
        # Mettre à jour
        chefs_display.at[idx, 'Nb_Projets_Actifs'] = nb_projets
        chefs_display.at[idx, 'Charge_Actuelle'] = charge_icm
        chefs_display.at[idx, 'Taux_Charge_Pct'] = taux_reel
    
    # Réorganiser colonnes
    colonnes_affichees = ['ID_Chef', 'Nom_Prenom', 'Capacite_Max', 'ICC_H_Semaine',
                          'Charge_Actuelle', 'Taux_Charge_Pct', 'Nb_Projets_Actifs']
    
    # Vérifier colonnes disponibles
    colonnes_disponibles = [col for col in colonnes_affichees if col in chefs_display.columns]
    
    df_display = chefs_display[colonnes_disponibles].copy()
    
    # Formater charge avec 1 décimale
    if 'Charge_Actuelle' in df_display.columns:
        df_display['Charge_Actuelle'] = df_display['Charge_Actuelle'].apply(lambda x: f"{x:.1f}")
    
    # Formater taux sans décimales avec %
    if 'Taux_Charge_Pct' in df_display.columns:
        df_display['Taux_Charge_Pct'] = df_display['Taux_Charge_Pct'].apply(lambda x: f"{x:.0f}%")
    
    # Affichage tableau
    st.dataframe(
        df_display,
        width='stretch',
        hide_index=True
    )


# ========================================
# MENU PRINCIPAL
# ========================================

def main():
    """Fonction principale de l'application."""
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 PMO Orchestre V4")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Affectation", "Projets", "Chefs"],
            key='page_selector'
        )
        
        st.markdown("---")
        
        # Bouton refresh
        if st.button("🔄 Actualiser"):
            st.cache_resource.clear()
            st.rerun()
        
        st.caption(f"Dernière mise à jour : {st.session_state.last_refresh.strftime('%H:%M')}")
    
    # Routing
    if page == "Dashboard":
        page_dashboard()
    elif page == "Affectation":
        page_affectation()
    elif page == "Projets":
        page_projets()
    elif page == "Chefs":
        page_chefs()


if __name__ == "__main__":
    main()
