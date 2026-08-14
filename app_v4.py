"""
Application Streamlit V5 - PMO Orchestre
=========================================

Interface web pour l'affectation intelligente des chefs de projet.

VERSION 4 : Recalibrage 5 plages + Visualisation temporelle
VERSION 5 : Corrections post-recette (affichage chefs, dépendances Streamlit 1.35, nettoyage résidus dev)

Auteur : PFE - ENCG Settat
Date v4: Novembre 2025
Date v5: Aout 2026
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys

# Plotly désactivé (non installé dans cet environnement)
# import plotly.graph_objects as go
# import plotly.express as px

# Imports locaux
from data_manager_v5 import DataManagerV5, init_data_manager
from algorithme_v5 import AlgorithmeAffectationV5, icm_to_heures_semaine, icc_to_heures_semaine


# ========================================
# CONFIGURATION PAGE
# ========================================

st.set_page_config(
    page_title="PMO Orchestre V5",
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
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #27AE60 !important;
    border-color: #27AE60 !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #1E8449 !important;
    border-color: #1E8449 !important;
}
</style>
""", unsafe_allow_html=True)


# ========================================
# INITIALISATION SESSION
# ========================================

# Pas de cache pour permettre les mises à jour
# (cache_resource ci-dessous : uniquement la connexion, pas les données)
@st.cache_resource
def get_data_manager():
    """Initialise le DataManager (mis en cache : une seule connexion réutilisée)."""
    if 'gcp_service_account' in st.secrets:
        import json
        credentials_dict = dict(st.secrets["gcp_service_account"])
        with open('/tmp/credentials.json', 'w') as f:
            json.dump(credentials_dict, f)
        credentials_file = '/tmp/credentials.json'
    else:
        credentials_file = '/Users/mac/Documents/DSMIA_PFE/PMO_Orchestre/credentials.json'
    
    return init_data_manager(
        credentials_file=credentials_file,
        sheet_id='1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs'
    )
    
def get_data_manager():
    """Initialise le DataManager (sans cache pour permettre affectations)."""
    # Charger credentials depuis Streamlit Cloud ou local
    if 'gcp_service_account' in st.secrets:
        # En production (Streamlit Cloud)
        import json
        credentials_dict = dict(st.secrets["gcp_service_account"])
        # Sauvegarder temporairement pour data_manager
        with open('/tmp/credentials.json', 'w') as f:
            json.dump(credentials_dict, f)
        credentials_file = '/tmp/credentials.json'
    else:
        # En local
        credentials_file = '/Users/mac/Documents/DSMIA_PFE/PMO_Orchestre/credentials.json'
    
    return init_data_manager(
        credentials_file=credentials_file,
        sheet_id='1TFCyjjWZirBQG45xXnJ8vzHMo5YrhkiIwHdHaMx7lfs'
    )
@st.cache_data(ttl=30)
def cached_get_projets():
    return get_data_manager().get_projets()

@st.cache_data(ttl=30)
def cached_get_chefs():
    return get_data_manager().get_chefs()

@st.cache_data(ttl=30)
def cached_get_clients():
    return get_data_manager().get_clients()
    
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
    st.title("📈 Dashboard PMO")
    
    dm = get_data_manager()
    projets = cached_get_projets()
    chefs = cached_get_chefs()
    
    if len(projets) == 0 or len(chefs) == 0:
        st.warning("⚠️ Impossible de charger les données pour le moment (quota Google Sheets probablement dépassé). Réessayez dans une minute.")
        return
    
    # Métriques globales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Total Projets = projets NON clôturés (pas le total brut de la feuille)
        nb_non_clotures = len(projets[projets['Statut'] != 'Clôturé']) if 'Statut' in projets.columns else len(projets)
        nb_affectes = 0
        if 'Statut' in projets.columns:
            nb_affectes = len(projets[projets['Statut'] == 'Actif'])
        st.metric(
            "Total Projets",
            nb_non_clotures,
            delta=f"{nb_affectes} affectés"
        )
    
    with col2:
        st.metric("Total Chefs", len(chefs), delta=f"{len(chefs)} actifs")
    
    with col3:
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
        charges_reelles = []
        for _, chef in chefs.iterrows():
            chef_id = chef['ID_Chef']
            icc = chef.get('Capacite_Max', 100)
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
    
    with col5:
        nb_surcharges = sum(1 for t in charges_reelles if t > 100)
        st.metric(
            "Chefs surchargés",
            nb_surcharges,
            delta="⚠️ À surveiller" if nb_surcharges > 0 else "OK"
        )

    
    st.markdown("---")
    
    # Vue d'ensemble des chefs (avec colonne Capacité Max ajoutée)
    st.subheader("👷 Vue d'ensemble des chefs de projet")
    
    chefs_summary = chefs.copy()
    for idx, chef in chefs_summary.iterrows():
        chef_id = chef['ID_Chef']
        nb_projets = len(projets[(projets['Chef_Affecte'] == chef_id) & (projets['Statut'] == 'Actif')])
        charge_icm = projets[(projets['Chef_Affecte'] == chef_id) & (projets['Statut'] == 'Actif')]['Indice_Charge'].sum()
        charge_h = charge_icm * 0.4
        icc = chef['Capacite_Max']
        taux_reel = (charge_icm / icc * 100) if icc > 0 else 0
        chefs_summary.at[idx, 'Projets_Actifs'] = nb_projets
        chefs_summary.at[idx, 'Charge_H'] = charge_h
        chefs_summary.at[idx, 'Taux_Calc'] = taux_reel
    
    df_summary_display = chefs_summary[['Nom_Prenom', 'Capacite_Max', 'Charge_H', 'Projets_Actifs', 'Taux_Calc']].copy()
    df_summary_display['Charge_H'] = df_summary_display['Charge_H'].apply(lambda x: f"{x:.1f}")
    df_summary_display['Taux_Calc'] = df_summary_display['Taux_Calc'].apply(lambda x: f"{x:.0f}%")
    
    st.dataframe(
        df_summary_display.rename(columns={
            'Nom_Prenom': 'Chef',
            'Capacite_Max': 'Capacité Max (ICC)',
            'Charge_H': 'Charge (h/sem)',
            'Projets_Actifs': 'Nb Projets',
            'Taux_Calc': 'Taux'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Utilisation des chefs — triée par charge décroissante
    st.subheader("👥 Utilisation des chefs de projet")
    
    chefs_summary_sorted = chefs_summary.sort_values('Taux_Calc', ascending=False)
    
    for _, chef in chefs_summary_sorted.iterrows():
        if 'Statut' in chef.index and chef.get('Statut') == 'Indisponible':
            continue
        
        taux = chef.get('Taux_Calc', 0)
        couleur = get_color_taux(taux)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.write(f"**{chef['Nom_Prenom']}**")
        
        with col2:
            st.progress(min(taux / 100, 1.0))
            st.caption(f"{taux:.0f}%")
        
        with col3:
            icc = chef.get('Capacite_Max', 0)
            icc_h = icc * 0.4
            charge_h = chef.get('Charge_H', 0)
            st.metric("Charge", f"{charge_h:.1f}h/sem", delta=f"{icc_h - charge_h:.1f}h dispo")
        
        with col4:
            st.metric("Projets", int(chef.get('Projets_Actifs', 0)))
        
        projets_chef = projets[(projets['Chef_Affecte'] == chef['ID_Chef']) & (projets['Statut'] == 'Actif')]
        if len(projets_chef) > 0:
            with st.expander(f"{couleur} Détail projets"):
                for _, p in projets_chef.iterrows():
                    icm_h = p.get('ICM_H_Semaine', 0)
                    client_id = p.get('ID_Client', '')
                    client = dm.get_client_by_id(client_id)
                    client_nom = client.get('Nom_Client', client_id) if client else client_id
                    st.write(f"• **{p['ID_Projet']}** - {client_nom} - {p['Nom_Projet']} : {p['Indice_Charge']:.0f} pts ({icm_h:.1f}h/sem)")
    
    st.markdown("---")
    st.subheader("📐 Santé du portefeuille (projets actifs)")
    
    projets_actifs = projets[projets['Statut'] == 'Actif'].copy()
    for col in ['CPI', 'SPI']:
        if col in projets_actifs.columns:
            projets_actifs[col] = pd.to_numeric(projets_actifs[col], errors='coerce')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpi_moy = projets_actifs['CPI'].mean() if 'CPI' in projets_actifs.columns else None
        st.metric("CPI moyen", f"{cpi_moy:.2f}" if pd.notna(cpi_moy) else "N/A",
                   delta="Sous budget" if cpi_moy and cpi_moy >= 1 else "En dérive budget" if cpi_moy else None)
    
    with col2:
        spi_moy = projets_actifs['SPI'].mean() if 'SPI' in projets_actifs.columns else None
        st.metric("SPI moyen", f"{spi_moy:.2f}" if pd.notna(spi_moy) else "N/A",
                   delta="Dans les temps" if spi_moy and spi_moy >= 1 else "En retard" if spi_moy else None)
    
    with col3:
        nb_derive = 0
        if 'CPI' in projets_actifs.columns and 'SPI' in projets_actifs.columns:
            nb_derive = len(projets_actifs[(projets_actifs['CPI'] < 1) | (projets_actifs['SPI'] < 1)])
        st.metric("Projets en dérive", nb_derive,
                   delta="⚠️ À surveiller" if nb_derive > 0 else "OK")


# ========================================
# PAGE : AFFECTATION INTELLIGENTE
# ========================================

def page_affectation():
    """Page d'affectation intelligente."""
    st.title("🧩 Affectation Intelligente")
    
    dm = get_data_manager()
    projets = cached_get_projets()
    chefs = cached_get_chefs()
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
    
    # Réinitialiser les recommandations si le projet sélectionné a changé
    if st.session_state.get('projet_id_precedent') != projet_id:
        st.session_state.pop('recommendations', None)
        st.session_state.pop('projet_actuel', None)
        st.session_state['projet_id_precedent'] = projet_id
    
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
            algo = AlgorithmeAffectationV5(ponderations)
            
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
        
        st.subheader(f"🏆 Classement des {len(recommendations)} chefs disponibles")
        
        for i, reco in enumerate(recommendations, 1):
            # Bouton d'affectation directement visible
            col_btn1, col_btn2 = st.columns([3, 1])
            
            with col_btn1:
                # Badge chef favori
                favori_badge = " ⭐ **CHEF FAVORI CLIENT**" if reco.get('is_favori', False) else ""
                st.write(f"**#{i} - {reco['chef_nom']}** (Score {reco['score']:.0f}/100){favori_badge}")
            
            with col_btn2:
                btn_key = f"affecter_{projet['ID_Projet']}_{reco['chef_id']}_{i}"
                confirm_key = f"confirm_surcharge_{projet['ID_Projet']}_{reco['chef_id']}_{i}"
                
                if reco['surcharge']:
                    st.checkbox("⚠️ Je confirme malgré la surcharge", key=confirm_key)
                
                peut_affecter = (not reco['surcharge']) or st.session_state.get(confirm_key, False)
                
                if st.button(f"✅ Affecter", key=btn_key, type="primary" if i==1 else "secondary", disabled=not peut_affecter):
                    with st.spinner("Affectation en cours..."):
                        dm_temp = get_data_manager()
                        success = dm_temp.affecter_projet(
                            projet['ID_Projet'],
                            reco['chef_id']
                        )
                        
                        if success:
                            cached_get_projets.clear()
                            cached_get_chefs.clear()
                            st.success(f"✅ Projet affecté à {reco['chef_nom']} !")
                            st.balloons()
                            if 'recommendations' in st.session_state:
                                del st.session_state['recommendations']
                            if 'projet_actuel' in st.session_state:
                                del st.session_state['projet_actuel']
                            import time
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de l'affectation")
            
            # Détails dans expander (lecture seule)
            with st.expander(f"Détails #{i}", expanded=(i <= 3)):
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
                    st.metric(
                        "Charge si affecté",
                        f"{reco['charge_h_future']:.1f}h/sem",
                        delta=f"{reco['marge_h']:.1f}h marge",
                        delta_color="normal"
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
        
def color_statut(val):
    """Couleur de fond selon le statut du projet."""
    if val == 'Actif':
        return 'background-color: #D5F5E3; color: #196F3D; font-weight: bold;'
    elif val == 'En attente':
        return 'background-color: #D6EAF8; color: #1B4F72; font-weight: bold;'
    elif val == 'Clôturé':
        return 'background-color: #EAECEE; color: #566573;'
    return ''


def page_projets():
    """Page liste des projets."""
    st.title("📁 Gestion des Projets")
    
    dm = get_data_manager()
    projets = cached_get_projets()
    chefs = cached_get_chefs()
    
    if len(projets) == 0:
        st.warning("⚠️ Impossible de charger les projets pour le moment (quota Google Sheets probablement dépassé). Réessayez dans une minute.")
        return
    
    # ========================================
    # CREATION D'UN NOUVEAU PROJET
    # ========================================
    with st.expander("➕ Créer un nouveau projet"):
        clients_df = cached_get_clients()
        clients_options = clients_df['ID_Client'].tolist() if len(clients_df) > 0 else []
        
        with st.form("form_nouveau_projet"):
            col1, col2 = st.columns(2)
            with col1:
                nom_projet = st.text_input("Nom du projet *")
                id_client = st.selectbox("Client *", clients_options)
                budget = st.number_input("Budget (MAD)", min_value=0, value=100000, step=10000)
                charge_jh = st.number_input("Charge (jours/homme)", min_value=0, value=50)
                nb_interv = st.number_input("Nombre d'intervenants", min_value=1, value=5)
            with col2:
                complexite = st.selectbox("Complexité technique", ["2=Faible", "3=Moyen", "4=Élevé", "5=Très élevé"])
                risque = st.selectbox("Niveau de risque", ["2=Faible", "3=Moyen", "4=Élevé", "5=Très élevé"])
                engagement = st.selectbox("Engagement client", ["2=Minimal", "3=Modéré", "4=Impliqué", "5=Très impliqué"])
                freq = st.selectbox("Fréquence instances", ["1=Mensuelle", "2=Bi-mensuelle", "3=Hebdo", "4=Bi-hebdo"])
                dispersion = st.selectbox("Dispersion géographique", ["1=1 site", "2=2 sites", "3=National", "4=International"])
            
            date_debut = st.date_input("Date de début")
            duree = st.number_input("Durée (semaines)", min_value=1, value=12)
            commentaires = st.text_area("Commentaires")
            
            submitted = st.form_submit_button("Créer le projet", type="primary")
            
            if submitted:
                if not nom_projet or not id_client:
                    st.error("Le nom du projet et le client sont obligatoires")
                else:
                    ponderations = dm.get_ponderations()
                    algo = AlgorithmeAffectationV5(ponderations)
                    
                    criteres_icm = {
                        'Charge_JH': charge_jh, 'Complexite_Tech': complexite,
                        'Budget_MAD': budget, 'Niveau_Risque': risque,
                        'Nb_Intervenants': nb_interv, 'Engagement_Client': engagement,
                        'Freq_Instances': freq, 'Dispersion_Geo': dispersion
                    }
                    icm_calcule = algo.calculer_icm(criteres_icm)
                    
                    ponderations = dm.get_ponderations()
                    algo = AlgorithmeAffectationV5(ponderations)
                    criteres_icc = {
                        'Competences_Mgmt': mgmt, 'Annees_Experience': experience,
                        'Competences_Tech': tech, 'Utilisation_IA': ia
                    }
                    icc_calcule = algo.calculer_icc(criteres_icc)
                    
                    data = {
                        'Nom_Prenom': nom, 'Email': email,
                        'Annees_Experience': experience, 'Competences_Tech': tech,
                        'Competences_Mgmt': mgmt, 'Utilisation_IA': ia,
                        'Capacite_Max': icc_calcule, 'ICC_H_Semaine': round(icc_to_heures_semaine(icc_calcule), 1),
                        'Secteurs_Expertise': secteurs,
                        'Commentaires': commentaires, 'Statut': 'Disponible'
                    }
                    succes, resultat = dm.creer_chef(data)
                    
                    if succes:
                        st.success(f"✅ Chef {resultat} créé (ICC calculé = {icc_calcule}/100) !")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur : {resultat}")
    
    st.markdown("---")
    
    # ========================================
    # FILTRES
    # ========================================
    map_chefs_nom = dict(zip(chefs['ID_Chef'], chefs['Nom_Prenom'])) if len(chefs) > 0 else {}
    
    col1, col2 = st.columns(2)
    with col1:
        statut_filtre = st.multiselect(
            "Statut", options=projets['Statut'].unique().tolist(), default=['Actif']
        )
    with col2:
        chefs_avec_projets = [c for c in projets['Chef_Affecte'].unique().tolist() if c and c in map_chefs_nom]
        noms_options = sorted([map_chefs_nom[c] for c in chefs_avec_projets])
        noms_selectionnes = st.multiselect("Chef affecté", options=noms_options)
        ids_selectionnes = [cid for cid, nom in map_chefs_nom.items() if nom in noms_selectionnes]
    
    df_filtre = projets.copy()
    if statut_filtre:
        df_filtre = df_filtre[df_filtre['Statut'].isin(statut_filtre)]
    if noms_selectionnes:
        df_filtre = df_filtre[df_filtre['Chef_Affecte'].isin(ids_selectionnes)]
    
    colonnes_affichees = ['ID_Projet', 'Nom_Projet', 'Statut', 'Indice_Charge', 
                          'ICM_H_Semaine', 'Chef_Affecte', 'Date_Debut', 
                          'Date_Fin_Prev', 'CPI', 'SPI', 'KPI Facturation']
    colonnes_disponibles = [col for col in colonnes_affichees if col in df_filtre.columns]
    df_display = df_filtre[colonnes_disponibles].copy()
    
    clients_df = cached_get_clients()
    map_clients = dict(zip(clients_df['ID_Client'], clients_df['Nom_Client'])) if len(clients_df) > 0 else {}
    df_display.insert(2, 'Nom_Client', df_filtre['ID_Client'].apply(lambda x: map_clients.get(x, x)))
    
    if 'Chef_Affecte' in df_display.columns:
        df_display['Nom_Chef'] = df_display['Chef_Affecte'].apply(lambda x: map_chefs_nom.get(x, x))
        idx = list(df_display.columns).index('Chef_Affecte')
        cols = list(df_display.columns)
        cols.remove('Nom_Chef')
        cols.insert(idx + 1, 'Nom_Chef')
        df_display = df_display[cols]
    
    for col in ['Date_Debut', 'Date_Fin_Prev']:
        if col in df_display.columns:
            df_display[col] = pd.to_datetime(df_display[col], errors='coerce').dt.strftime('%Y-%m-%d')

    colonnes_numeriques = ['Indice_Charge', 'ICM_H_Semaine', 'CPI', 'SPI', 'KPI Facturation']
    for col in colonnes_numeriques:
        if col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce').apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else ''
            )
            
    styler = df_display.style.map(color_statut, subset=['Statut']).hide(axis='index')
    st.dataframe(styler, use_container_width=True)
    st.caption(f"**{len(df_filtre)}** projet(s) affiché(s)")
    
    st.markdown("---")
    
    # ========================================
    # ACTIONS PAR PROJET
    # ========================================
    st.subheader("Actions")
    
    clients_options_edit = clients_df['ID_Client'].tolist() if len(clients_df) > 0 else []
    chefs_options_edit = [''] + chefs['ID_Chef'].tolist() if len(chefs) > 0 else ['']
    
    for idx, projet in df_filtre.iterrows():
        projet_id = projet['ID_Projet']
        col1, col2, col3, col4 = st.columns([3, 1.3, 1.3, 1.3])
        
        with col1:
            st.write(f"**{projet['Nom_Projet']}** ({projet_id}) — {projet.get('Statut','-')}")
        
        with col2:
            if st.button("✏️ Modifier", key=f"edit_proj_{projet_id}"):
                st.session_state[f"editing_proj_{projet_id}"] = not st.session_state.get(f"editing_proj_{projet_id}", False)
        
        with col3:
            if projet.get('Statut') == 'Clôturé':
                st.caption("🔒 Déjà clôturé")
            else:
                if st.button("🔒 Clôturer", key=f"cloture_{projet_id}"):
                    if dm.cloturer_projet(projet_id):
                        st.success("Projet clôturé")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la clôture")
        
        with col4:
            chef_actuel = projet.get('Chef_Affecte', '')
            if not chef_actuel or projet.get('Statut') != 'Actif':
                st.caption("— pas de chef à retirer")
            else:
                if st.button("🔓 Désaffecter", key=f"desaffect_{projet_id}"):
                    if dm.desaffecter_projet(projet_id):
                        st.success("Projet désaffecté, capacité du chef libérée")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la désaffectation")
        
        # ---- FORMULAIRE DE MODIFICATION COMPLET ----
        if st.session_state.get(f"editing_proj_{projet_id}", False):
            with st.form(f"form_edit_proj_{projet_id}"):
                st.write(f"**Modifier {projet['Nom_Projet']}** — tous les champs de la base")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Identification**")
                    nom_e = st.text_input("Nom du projet", value=projet.get('Nom_Projet', ''))
                    idx_client = clients_options_edit.index(projet.get('ID_Client')) if projet.get('ID_Client') in clients_options_edit else 0
                    client_e = st.selectbox("Client", clients_options_edit, index=idx_client)
                    statuts_possibles = ["En attente", "Actif", "Clôturé"]
                    statut_actuel = projet.get('Statut', 'En attente')
                    idx_statut = statuts_possibles.index(statut_actuel) if statut_actuel in statuts_possibles else 0
                    statut_e = st.selectbox("Statut", statuts_possibles, index=idx_statut)
                    idx_chef = chefs_options_edit.index(projet.get('Chef_Affecte')) if projet.get('Chef_Affecte') in chefs_options_edit else 0
                    chef_e = st.selectbox("Chef affecté", chefs_options_edit, index=idx_chef,
                                           format_func=lambda x: map_chefs_nom.get(x, "— Aucun —") if x else "— Aucun —")
                    
                    st.markdown("**Critères ICM**")
                    budget_e = st.number_input("Budget (MAD)", value=int(projet.get('Budget_MAD', 0) or 0))
                    charge_e = st.number_input("Charge (j/h)", value=int(projet.get('Charge_JH', 0) or 0))
                    nb_interv_e = st.number_input("Nb intervenants", value=int(projet.get('Nb_Intervenants', 1) or 1))
                
                with c2:
                    complexite_opts = ["2=Faible", "3=Moyen", "4=Élevé", "5=Très élevé"]
                    risque_opts = ["2=Faible", "3=Moyen", "4=Élevé", "5=Très élevé"]
                    engagement_opts = ["2=Minimal", "3=Modéré", "4=Impliqué", "5=Très impliqué"]
                    freq_opts = ["1=Mensuelle", "2=Bi-mensuelle", "3=Hebdo", "4=Bi-hebdo"]
                    dispersion_opts = ["1=1 site", "2=2 sites", "3=National", "4=International"]
                    
                    def _idx(opts, val, default=0):
                        return opts.index(val) if val in opts else default
                    
                    complexite_e = st.selectbox("Complexité technique", complexite_opts, index=_idx(complexite_opts, projet.get('Complexite_Tech')))
                    risque_e = st.selectbox("Niveau de risque", risque_opts, index=_idx(risque_opts, projet.get('Niveau_Risque')))
                    engagement_e = st.selectbox("Engagement client", engagement_opts, index=_idx(engagement_opts, projet.get('Engagement_Client')))
                    freq_e = st.selectbox("Fréquence instances", freq_opts, index=_idx(freq_opts, projet.get('Freq_Instances')))
                    dispersion_e = st.selectbox("Dispersion géo", dispersion_opts, index=_idx(dispersion_opts, projet.get('Dispersion_Geo')))
                    
                    st.markdown("**Suivi**")
                    duree_e = st.number_input("Durée (semaines)", value=int(projet.get('Duree_Semaines', 12) or 12))
                    cpi_e = st.number_input("CPI", value=float(projet.get('CPI', 1.0) or 1.0), format="%.2f")
                    spi_e = st.number_input("SPI", value=float(projet.get('SPI', 1.0) or 1.0), format="%.2f")
                
                commentaires_e = st.text_area("Commentaires", value=projet.get('Commentaires', '') or '')
                
                col_s, col_c = st.columns(2)
                with col_s:
                    save = st.form_submit_button("💾 Enregistrer", type="primary")
                with col_c:
                    cancel = st.form_submit_button("Annuler")
                
                if save:
                    ponderations = dm.get_ponderations()
                    algo = AlgorithmeAffectationV5(ponderations)
                    criteres_icm = {
                        'Charge_JH': charge_e, 'Complexite_Tech': complexite_e,
                        'Budget_MAD': budget_e, 'Niveau_Risque': risque_e,
                        'Nb_Intervenants': nb_interv_e, 'Engagement_Client': engagement_e,
                        'Freq_Instances': freq_e, 'Dispersion_Geo': dispersion_e
                    }
                    icm_recalcule = algo.calculer_icm(criteres_icm)
                    
                    data = {
                        'Nom_Projet': nom_e, 'ID_Client': client_e, 'Statut': statut_e,
                        'Chef_Affecte': chef_e, 'Budget_MAD': budget_e, 'Charge_JH': charge_e,
                        'Nb_Intervenants': nb_interv_e, 'Complexite_Tech': complexite_e,
                        'Niveau_Risque': risque_e, 'Engagement_Client': engagement_e,
                        'Freq_Instances': freq_e, 'Dispersion_Geo': dispersion_e,
                        'Duree_Semaines': duree_e, 'CPI': cpi_e, 'SPI': spi_e,
                        'Commentaires': commentaires_e,
                        'Indice_Charge': icm_recalcule,
                        'ICM_H_Semaine': round(icm_to_heures_semaine(icm_recalcule), 1),
                    }
                    if dm.modifier_projet(projet_id, data):
                        st.success(f"✅ Modifié (ICM recalculé = {icm_recalcule})")
                        st.session_state[f"editing_proj_{projet_id}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la modification")
                if cancel:
                    st.session_state[f"editing_proj_{projet_id}"] = False
                    st.rerun()
        
        st.markdown("---")


# ========================================
# PAGE : CHEFS
# ========================================

def page_chefs():
    """Page liste des chefs."""
    st.title("👥 Gestion des Chefs de Projet")
    
    dm = get_data_manager()
    chefs = cached_get_chefs()
    projets = cached_get_projets()
    
    # ========================================
    # CREATION D'UN NOUVEAU CHEF
    # ========================================
    with st.expander("➕ Créer un nouveau chef de projet"):
        with st.form("form_nouveau_chef"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom et prénom *")
                email = st.text_input("Email")
                experience = st.number_input("Années d'expérience", min_value=0, max_value=50, value=1)
                capacite = st.number_input("Capacité max (ICC, 0-100)", min_value=0, max_value=100, value=50)
            with col2:
                tech = st.selectbox("Compétences techniques", ["2=Basique", "3=Moyen", "4=Bon", "5=Excellent"])
                mgmt = st.selectbox("Compétences management", ["2=Débutant", "3=Moyen", "4=Bon", "5=Excellent"])
                ia = st.selectbox("Utilisation IA", ["1=Aucune", "2=Occasionnelle", "3=Régulière", "4=Quotidienne", "5=Avancée"])
                secteurs = st.text_input("Secteurs d'expertise")
            
            commentaires = st.text_area("Commentaires")
            submitted = st.form_submit_button("Créer le chef", type="primary")
            
            if submitted:
                if not nom:
                    st.error("Le nom est obligatoire")
                else:
                    data = {
                        'Nom_Prenom': nom, 'Email': email,
                        'Annees_Experience': experience, 'Competences_Tech': tech,
                        'Competences_Mgmt': mgmt, 'Utilisation_IA': ia,
                        'Capacite_Max': capacite, 'Secteurs_Expertise': secteurs,
                        'Commentaires': commentaires, 'Statut': 'Disponible'
                    }
                    succes, resultat = dm.creer_chef(data)
                    if succes:
                        st.success(f"✅ Chef {resultat} créé avec succès !")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur : {resultat}")
    
    st.markdown("---")
    
    # ========================================
    # CALCUL METRIQUES REELLES (inchangé)
    # ========================================
    chefs_display = chefs.copy()
    for idx, chef in chefs_display.iterrows():
        chef_id = chef['ID_Chef']
        nb_projets = len(projets[
            (projets['Chef_Affecte'] == chef_id) & (projets['Statut'] == 'Actif')
        ])
        charge_icm = projets[
            (projets['Chef_Affecte'] == chef_id) & (projets['Statut'] == 'Actif')
        ]['Indice_Charge'].sum()
        icc = chef['Capacite_Max']
        taux_reel = (charge_icm / icc * 100) if icc > 0 else 0
        chefs_display.at[idx, 'Nb_Projets_Actifs'] = nb_projets
        chefs_display.at[idx, 'Charge_Actuelle'] = charge_icm
        chefs_display.at[idx, 'Taux_Charge_Pct'] = taux_reel
    
    # ========================================
    # TABLEAU RECAPITULATIF
    # ========================================
    colonnes_affichees = ['ID_Chef', 'Nom_Prenom', 'Capacite_Max', 'ICC_H_Semaine',
                          'Charge_Actuelle', 'Taux_Charge_Pct', 'Nb_Projets_Actifs']
    colonnes_disponibles = [col for col in colonnes_affichees if col in chefs_display.columns]
    df_display = chefs_display[colonnes_disponibles].copy()
    
    for col in ['Capacite_Max', 'ICC_H_Semaine', 'Charge_Actuelle']:
        if col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce').apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else ''
            )
    
    if 'Taux_Charge_Pct' in df_display.columns:
        df_display['Taux_Charge_Pct'] = pd.to_numeric(df_display['Taux_Charge_Pct'], errors='coerce').apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else ''
        )
    
    if 'Nb_Projets_Actifs' in df_display.columns:
        df_display['Nb_Projets_Actifs'] = pd.to_numeric(df_display['Nb_Projets_Actifs'], errors='coerce').fillna(0).astype(int)
        
    def highlight_surcharge(row):
        try:
            taux_num = float(str(row['Taux_Charge_Pct']).replace('%', ''))
        except (ValueError, KeyError):
            taux_num = 0
        if taux_num > 100:
            return ['background-color: #FADBD8; color: #922B21; font-weight: bold;'] * len(row)
        return [''] * len(row)
    
    styler = df_display.style.apply(highlight_surcharge, axis=1).hide(axis='index')
    st.dataframe(styler, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================
    # ACTIONS PAR CHEF (Modifier / Rendre indisponible)
    # ========================================
    st.subheader("Actions")
    
    for idx, chef in chefs_display.iterrows():
        chef_id = chef['ID_Chef']
        col1, col2, col3 = st.columns([3, 1.5, 2])
        
        with col1:
            st.write(f"**{chef['Nom_Prenom']}** ({chef_id}) — {chef.get('Statut','-')}")
        
        with col2:
            if st.button("✏️ Modifier", key=f"edit_chef_{chef_id}"):
                st.session_state[f"editing_chef_{chef_id}"] = not st.session_state.get(f"editing_chef_{chef_id}", False)
        
        with col3:
            if chef.get('Statut') == 'Indisponible':
                st.caption("⛔ Déjà indisponible")
            else:
                autorise, message = dm.peut_devenir_indisponible(chef_id, projets)
                if st.button("⛔ Rendre indisponible", key=f"indispo_{chef_id}", disabled=not autorise):
                    succes, msg = dm.rendre_indisponible_chef(chef_id, projets)
                    if succes:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                if not autorise:
                    st.caption(f"ℹ️ {message}")
        
        if st.session_state.get(f"editing_chef_{chef_id}", False):
            with st.form(f"form_edit_chef_{chef_id}"):
                st.write(f"**Modifier {chef['Nom_Prenom']}**")
                nom_e = st.text_input("Nom et prénom", value=chef.get('Nom_Prenom', ''))
                email_e = st.text_input("Email", value=chef.get('Email', ''))
                exp_e = st.number_input("Années d'expérience", value=int(chef.get('Annees_Experience', 0) or 0))
                capa_e = st.number_input("Capacité max", value=int(chef.get('Capacite_Max', 50) or 50))
                statuts_possibles = ["Disponible", "Indisponible"]
                statut_actuel = chef.get('Statut', 'Disponible')
                idx_statut = statuts_possibles.index(statut_actuel) if statut_actuel in statuts_possibles else 0
                statut_e = st.selectbox("Statut", statuts_possibles, index=idx_statut)
                
                col_s, col_c = st.columns(2)
                with col_s:
                    save = st.form_submit_button("💾 Enregistrer", type="primary")
                with col_c:
                    cancel = st.form_submit_button("Annuler")
                
                if save:
                    data = {'Nom_Prenom': nom_e, 'Email': email_e, 'Annees_Experience': exp_e,
                            'Capacite_Max': capa_e, 'Statut': statut_e}
                    if dm.modifier_chef(chef_id, data):
                        st.success("✅ Modifié")
                        st.session_state[f"editing_chef_{chef_id}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la modification")
                if cancel:
                    st.session_state[f"editing_chef_{chef_id}"] = False
                    st.rerun()
        
        st.markdown("---")
        
# ========================================
# PAGE : PLANIFICATION
# ========================================
def page_planification():
    """Page de prévision de charge sur les prochaines semaines."""
    st.title("📅 Planification Hebdomadaire")
    
    dm = get_data_manager()
    chefs = cached_get_chefs()
    map_chefs_nom = dict(zip(chefs['ID_Chef'], chefs['Nom_Prenom'])) if len(chefs) > 0 else {}
    
    st.markdown("Génère une projection de la charge de chaque chef sur les semaines à venir, à partir des projets actifs et planifiés.")
    
    nb_semaines = st.slider("Nombre de semaines à projeter", min_value=4, max_value=26, value=12)
    
    if st.button("🔄 Générer la prévision", type="primary"):
        with st.spinner("Calcul en cours..."):
            planning_df = dm.generer_planification_hebdo(nb_semaines=nb_semaines)
            st.session_state['planning_genere'] = planning_df
            if len(planning_df) == 0:
                st.warning("⚠️ Aucune ligne générée. Cause probable : aucun projet « Actif » avec Chef affecté n'a de période (Date_Debut → Date_Fin_Prev) recoupant les prochaines semaines. Vérifiez les dates dans Google Sheets.")
    
    if 'planning_genere' in st.session_state and len(st.session_state['planning_genere']) > 0:
        planning_df = st.session_state['planning_genere'].copy()
        
        # Nom du chef au lieu de l'ID
        planning_df['Nom_Chef'] = planning_df['Chef_ID'].apply(lambda x: map_chefs_nom.get(x, x))
        
        # Date du lundi (premier jour) de chaque semaine, à partir de la date générée
        planning_df['Date'] = pd.to_datetime(planning_df['Date'], errors='coerce')
        planning_df['Lundi_Semaine'] = planning_df['Date'] - pd.to_timedelta(planning_df['Date'].dt.weekday, unit='D')
        
        st.markdown("---")
        st.subheader("Vue par chef / semaine (heures prévues)")
        
        # Construire le tableau : ligne "Date" en haut, puis une ligne par chef
        semaine_to_date = planning_df.groupby('Semaine')['Lundi_Semaine'].first().to_dict()
        
        pivot = planning_df.pivot_table(
            index='Nom_Chef', columns='Semaine', values='Charge_H', aggfunc='sum', fill_value=0
        )
        pivot = pivot.reindex(sorted(pivot.columns), axis=1)
        
        col_labels = [f"S{s}" for s in pivot.columns]
        date_row = [
            semaine_to_date[s].strftime('%d/%m/%Y') if pd.notna(semaine_to_date[s]) else ''
            for s in pivot.columns
        ]
        
        pivot_display = pivot.applymap(lambda x: f"{x:.1f}")
        pivot_display.columns = col_labels
        pivot_display.columns.name = "Semaine"
        
        date_df = pd.DataFrame([date_row], columns=col_labels, index=["Date"])
        date_df.columns.name = "Semaine"
        
        table_finale = pd.concat([date_df, pivot_display])
        
        st.dataframe(table_finale, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Évolution de la charge par chef")
        
        chart_data = pivot.copy()
        chart_data.columns = [
            semaine_to_date[s].strftime('%d/%m') if pd.notna(semaine_to_date[s]) else f"S{s}"
            for s in pivot.columns
        ]
        chart_data = chart_data.T  # une ligne du graphe par chef, une colonne par semaine
        chart_data.index.name = "Semaine"
        
        st.line_chart(chart_data, use_container_width=True)
        st.caption(f"{len(planning_df)} lignes générées sur {nb_semaines} semaines")
        
        if st.button("💾 Enregistrer cette prévision dans Google Sheets"):
            if dm.sauvegarder_planification_hebdo(st.session_state['planning_genere']):
                st.success("✅ Prévision enregistrée dans la feuille Planification_Hebdo")
            else:
                st.error("❌ Erreur lors de l'enregistrement")
    
    st.markdown("---")
    st.subheader("Dernière prévision enregistrée")
    planning_existant = dm.get_planification_hebdo()
    if len(planning_existant) > 0:
        planning_existant = planning_existant.copy()
        planning_existant['Nom_Chef'] = planning_existant['Chef_ID'].apply(lambda x: map_chefs_nom.get(x, x))
        if 'Annee' in planning_existant.columns:
            planning_existant['Annee'] = planning_existant['Annee'].astype(str)
        colonnes_finales = ['Semaine', 'Annee', 'Nom_Chef', 'Projet_ID', 'Projet_Nom', 'ICM', 'Charge_H']
        colonnes_dispo = [c for c in colonnes_finales if c in planning_existant.columns]
        st.dataframe(planning_existant[colonnes_dispo], use_container_width=True, hide_index=True)
    else:
        st.info("Aucune prévision enregistrée pour le moment.")
        
# ========================================
# MENU PRINCIPAL
# ========================================
def check_password():
    """Affiche un champ mot de passe ; retourne True si correct."""
    def password_entered():
        entered = st.session_state.get("password", "")
        attendu = st.secrets.get("app_password", "")
        if entered.strip() == attendu.strip():
            st.session_state["password_correct"] = True
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🎯 PMO Orchestre")
        st.text_input("🔒 Mot de passe", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🎯 PMO Orchestre")
        st.text_input("🔒 Mot de passe", type="password", on_change=password_entered, key="password")
        st.error("😕 Mot de passe incorrect")
        return False
    else:
        return True
        
def main():
    """Fonction principale de l'application."""
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 PMO Orchestre V5")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Affectation", "Projets", "Chefs de projet", "Planification"],
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
    elif page == "Chefs de projet":
        page_chefs()
    elif page == "Planification":
        page_planification()


if __name__ == "__main__":
    if check_password():
        main()
