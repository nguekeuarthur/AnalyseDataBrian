#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Streamlit pour l'analyse du formulaire
Visualisations des métriques clés
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# Configuration de la page AMÉLIORÉE
st.set_page_config(
    page_title="📊 Analyse du Formulaire - Dashboard Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/streamlit/streamlit',
        'Report a bug': "mailto:support@example.com",
        'About': "# Dashboard d'Analyse Formulaire\nVersion 2.0 - Design Pro"
    }
)

# Import et injection du CSS personnalisé
def load_css():
    """Charge et injecte le CSS personnalisé"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.html(f"<style>{css}</style>")
    except FileNotFoundError:
        st.warning("⚠️ Fichier styles.css non trouvé. Design par défaut utilisé.")

# CSS personnalisé (fallback si le fichier externe n'existe pas)
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_donnees():
    """
    Charge les données nettoyées avec validation
    """
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        
        # Nettoyage et validation des données
        # Convertir les dates
        if 'horodateur' in df.columns:
            df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        if 'date_de_naissance' in df.columns:
            df['date_de_naissance'] = pd.to_datetime(df['date_de_naissance'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Nettoyage des colonnes texte pour éviter les problèmes d'affichage
        if 'pays' in df.columns:
            df['pays'] = df['pays'].astype(str).str.strip()
            # CORRECTION: Exclure les valeurs numériques de la colonne pays
            # Ces valeurs sont des erreurs de saisie (15000, 2005, etc.)
            mask_pays_valides = ~df['pays'].str.isdigit()
            if not mask_pays_valides.all():
                pays_invalides = df[~mask_pays_valides]['pays'].unique()
                st.sidebar.warning(f"⚠️ Pays invalides exclus: {pays_invalides}")
                df = df[mask_pays_valides].copy()
        
        if 'type_pack' in df.columns:
            df['type_pack'] = df['type_pack'].astype(str).str.strip()
        
        if 'methode_paiement_std' in df.columns:
            df['methode_paiement_std'] = df['methode_paiement_std'].astype(str).str.strip()
        
        # Log pour debug
        st.sidebar.text(f"✅ {len(df)} lignes valides chargées")
        if 'pays' in df.columns:
            st.sidebar.text(f"🌍 {df['pays'].nunique()} pays uniques")
            # Afficher un échantillon des pays pour vérification
            pays_sample = sorted(df['pays'].unique())[:5]
            st.sidebar.text(f"📝 Échantillon: {', '.join(pays_sample)}")
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

def obtenir_coordonnees_pays(pays):
    """
    Retourne les coordonnées approximatives d'un pays
    """
    coordonnees = {
        'Cameroun': [7.3697, 12.3547],
        'République Démocratique du Congo': [-4.0383, 21.7587],
        'Côte d\'Ivoire': [7.5400, -5.5471],
        'Bénin': [9.3077, 2.3158],
        'Togo': [8.6195, 0.8248],
        'Burkina Faso': [12.2383, -1.5616],
        'Mali': [17.5707, -3.9962],
        'Gabon': [-0.8037, 11.6094],
        'Sénégal': [14.4974, -14.4524],
        'Niger': [17.6078, 8.0817],
        'Congo': [-0.2280, 15.8277],
        'Ghana': [7.9465, -1.0232],
        'Nigeria': [9.0820, 8.6753],
        'France': [46.6034, 1.8883],
        'Maroc': [31.7917, -7.0926],
        'Algérie': [28.0339, 1.6596],
        'Tunisie': [33.8869, 9.5375]
    }
    return coordonnees.get(pays, [0, 0])

def main():
    # Chargement du CSS personnalisé
    load_css()
    
    # Logo et titre principal avec design amélioré
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h1 class="main-header">Dashboard d'Analyse du Formulaire</h1>
            <p style="font-size: 1.2rem; color: #666; margin-top: 1rem;">
                🚀 Analyse complète et interactive des données
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chargement des données
    df = charger_donnees()
    
    if df is None:
        st.error("⚠️ Impossible de charger les données. Vérifiez que le fichier 'Formulaire_FINAL_OPTIMISE.xlsx' existe.")
        return
    
    # Sidebar avec design amélioré
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #1f77b4, #ff7f0e); border-radius: 12px; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0;">🎛️ Centre de Contrôle</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 📋 Informations générales")
        
        # Métriques sidebar avec style
        st.markdown(f"""
        <div class="metric-card animated-card">
            <div class="metric-label">📊 Total Réponses</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card animated-card">
            <div class="metric-label">📂 Colonnes</div>
            <div class="metric-value">{len(df.columns)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton pour vider le cache
        if st.button("🔄 Actualiser les données", help="Vide le cache et recharge les données"):
            st.cache_data.clear()
            st.rerun()
    
    # Filtres de période
    df_filtered = df.copy()
    
    if 'horodateur' in df.columns and df['horodateur'].notna().any():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 1rem; border-radius: 12px; margin: 1rem 0;">
            <h3 style="color: #1976d2; margin: 0 0 1rem 0;">📅 Filtres de Période</h3>
        </div>
        """, unsafe_allow_html=True)
        
        date_min = df['horodateur'].min().date()
        date_max = df['horodateur'].max().date()
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📆 Période Complète</div>
            <div style="color: #1f77b4; font-weight: 600;">{date_min.strftime('%d/%m/%Y')} - {date_max.strftime('%d/%m/%Y')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélecteurs de date avec style
        col1, col2 = st.columns(2)
        
        with col1:
            date_debut_selectionnee = st.date_input(
                "📅 Date début",
                value=date_min,
                min_value=date_min,
                max_value=date_max,
                key="date_debut",
                help="Sélectionnez la date de début de votre analyse"
            )
        
        with col2:
            date_fin_selectionnee = st.date_input(
                "📅 Date fin",
                value=date_max,
                min_value=date_min,
                max_value=date_max,
                key="date_fin",
                help="Sélectionnez la date de fin de votre analyse"
            )
        
        # Vérification des dates avec alertes stylées
        if date_debut_selectionnee > date_fin_selectionnee:
            st.error("❌ La date de début doit être antérieure à la date de fin")
        else:
            # Filtrage des données
            mask_date = (
                (df['horodateur'].dt.date >= date_debut_selectionnee) & 
                (df['horodateur'].dt.date <= date_fin_selectionnee)
            )
            df_filtered = df[mask_date].copy()
            
            # Affichage de la période sélectionnée avec style
            if len(df_filtered) > 0:
                st.success(f"✅ **Période sélectionnée:** {date_debut_selectionnee.strftime('%d/%m/%Y')} - {date_fin_selectionnee.strftime('%d/%m/%Y')}")
                st.info(f"📊 **{len(df_filtered)} réponses** dans cette période")
                
                # Bouton de réinitialisation stylé
                if st.button("🔄 Réinitialiser la période", type="secondary"):
                    st.rerun()
            else:
                st.warning("⚠️ Aucune donnée dans cette période")
    
    # Filtres additionnels avec design moderne
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 1rem; border-radius: 12px; margin: 1rem 0;">
        <h3 style="color: #f57c00; margin: 0 0 1rem 0;">🎯 Filtres Additionnels</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Mettre les trois filtres sur la même ligne pour économiser l'espace
    col1, col2, col3 = st.columns(3)
    
    # Filtre par pays avec style - utiliser les données complètes pour la liste
    with col1:
        if 'pays' in df.columns:
            # Utiliser df original pour avoir tous les pays disponibles
            tous_pays = sorted(df['pays'].dropna().unique().tolist())
            pays_disponibles = ['Tous'] + tous_pays
            
            pays_selectionne = st.selectbox(
                "🌍 Sélectionnez un pays",
                pays_disponibles,
                key="filtre_pays",
                help="Filtrez les données par pays spécifique"
            )
            
            if pays_selectionne != 'Tous':
                df_filtered = df_filtered[df_filtered['pays'] == pays_selectionne]
    
    # Filtre par type de pack avec style - utiliser les données complètes
    with col2:
        if 'type_pack' in df.columns:
            tous_packs = sorted(df['type_pack'].dropna().unique().tolist())
            packs_disponibles = ['Tous'] + tous_packs
            
            pack_selectionne = st.selectbox(
                "📦 Sélectionnez un type de pack",
                packs_disponibles,
                key="filtre_pack",
                help="Filtrez les données par type de pack"
            )
            
            if pack_selectionne != 'Tous':
                df_filtered = df_filtered[df_filtered['type_pack'] == pack_selectionne]
    
    # Filtre par méthode de paiement avec style - utiliser les données complètes
    with col3:
        if 'methode_paiement_std' in df.columns:
            tous_paiements = sorted(df['methode_paiement_std'].dropna().unique().tolist())
            paiements_disponibles = ['Tous'] + tous_paiements
            
            paiement_selectionne = st.selectbox(
                "💳 Sélectionnez une méthode de paiement",
                paiements_disponibles,
                key="filtre_paiement",
                help="Filtrez les données par méthode de paiement"
            )
            
            if paiement_selectionne != 'Tous':
                df_filtered = df_filtered[df_filtered['methode_paiement_std'] == paiement_selectionne]
    
    # Informations sur le filtrage avec design
    if len(df_filtered) != len(df):
        st.markdown("---")
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f3e5f5, #e1bee7);">
            <h3 style="color: #7b1fa2; margin: 0 0 1rem 0;">📊 Résumé du Filtrage</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card animated-card">
                <div class="metric-label">📋 Données Originales</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card animated-card">
                <div class="metric-label">🎯 Données Filtrées</div>
                <div class="metric-value">{len(df_filtered)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            reduction = ((len(df) - len(df_filtered)) / len(df)) * 100
            st.markdown(f"""
            <div class="metric-card animated-card">
                <div class="metric-label">📉 Réduction</div>
                <div class="metric-value">{reduction:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Métriques clés avec design premium
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 class="section-title">🎯 Métriques Clés de Performance</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage d'alerte si données filtrées avec style
    if len(df_filtered) != len(df):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e8f5e8, #c8e6c9); padding: 1rem; border-radius: 12px; margin: 1rem 0; border-left: 5px solid #4caf50;">
            <h4 style="color: #2e7d32; margin: 0;">📊 Affichage basé sur <strong>{len(df_filtered)} réponses filtrées</strong> (sur {len(df)} au total)</h4>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card animated-card" style="background: linear-gradient(135deg, #e3f2fd, #bbdefb);">
            <div class="metric-label">📊 Total Réponses</div>
            <div class="metric-value" style="color: #1976d2;">{len(df_filtered)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'pays' in df_filtered.columns:
            nb_pays = df_filtered['pays'].nunique()
            st.markdown(f"""
            <div class="metric-card animated-card" style="background: linear-gradient(135deg, #e8f5e8, #c8e6c9);">
                <div class="metric-label">🌍 Pays Représentés</div>
                <div class="metric-value" style="color: #2e7d32;">{nb_pays}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'age' in df_filtered.columns and df_filtered['age'].notna().any():
            age_moyen = df_filtered['age'].mean()
            st.markdown(f"""
            <div class="metric-card animated-card" style="background: linear-gradient(135deg, #fff3e0, #ffe0b2);">
                <div class="metric-label">🎂 Âge Moyen</div>
                <div class="metric-value" style="color: #f57c00;">{age_moyen:.1f} ans</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-card" style="background: linear-gradient(135deg, #fff3e0, #ffe0b2);">
                <div class="metric-label">🎂 Âge Moyen</div>
                <div class="metric-value" style="color: #f57c00;">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'type_pack' in df_filtered.columns and len(df_filtered) > 0:
            pack_populaire = df_filtered['type_pack'].mode()[0] if len(df_filtered['type_pack'].mode()) > 0 else 'N/A'
            st.markdown(f"""
            <div class="metric-card animated-card" style="background: linear-gradient(135deg, #f3e5f5, #e1bee7);">
                <div class="metric-label">📦 Pack Populaire</div>
                <div class="metric-value" style="color: #7b1fa2;">{pack_populaire}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card animated-card" style="background: linear-gradient(135deg, #f3e5f5, #e1bee7);">
                <div class="metric-label">📦 Pack Populaire</div>
                <div class="metric-value" style="color: #7b1fa2;">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 1. Répartition des offres choisies avec design premium
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 class="section-title">🎯 Répartition des Offres Choisies</h2>
        <p style="color: #666; font-size: 1.1rem;">Analyse détaillée des packs sélectionnés par les utilisateurs</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'type_pack' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="plot-container">
                <h3 style="color: #1f77b4; text-align: center; margin-bottom: 1rem;">📊 Graphique en Camembert</h3>
            </div>
            """, unsafe_allow_html=True)
            pack_counts = df_filtered['type_pack'].value_counts()
            
            if len(pack_counts) > 0:
                fig_pie = px.pie(
                    values=pack_counts.values,
                    names=pack_counts.index,
                    title="Répartition des Packs Choisis",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Aucune donnée de pack disponible pour cette période")
        
        with col2:
            st.markdown("""
            <div class="plot-container">
                <h3 style="color: #1f77b4; text-align: center; margin-bottom: 1rem;">📊 Graphique en Barres</h3>
            </div>
            """, unsafe_allow_html=True)
            if len(pack_counts) > 0:
                fig_bar = px.bar(
                    x=pack_counts.values,
                    y=pack_counts.index,
                    orientation='h',
                    title="Nombre d'Inscrits par Pack",
                    labels={'x': 'Nombre d\'inscrits', 'y': 'Type de Pack'},
                    color=pack_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Aucune donnée de pack disponible pour cette période")
        
        # Tableau détaillé
        if len(df_filtered) > 0 and 'prix_pack_fcfa' in df_filtered.columns:
            st.markdown("### 📋 Détails par Pack")
            pack_stats = df_filtered.groupby('type_pack').agg({
                'type_pack': 'count',
                'prix_pack_fcfa': ['mean', 'min', 'max']
            }).round(0)
            pack_stats.columns = ['Nombre d\'inscrits', 'Prix moyen (FCFA)', 'Prix min (FCFA)', 'Prix max (FCFA)']
            st.dataframe(pack_stats, use_container_width=True)
    else:
        st.info("Aucune donnée d'offre disponible pour les filtres sélectionnés")
    
    # 2. Répartition géographique
    st.markdown("---")
    st.markdown("## 🌍 Répartition Géographique")
    
    if 'pays' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Top 10 des Pays")
            pays_counts = df_filtered['pays'].value_counts().head(10)
            
            if len(pays_counts) > 0:
                fig_geo = px.bar(
                    x=pays_counts.values,
                    y=pays_counts.index,
                    orientation='h',
                    title="Nombre de Participants par Pays",
                    labels={'x': 'Nombre de participants', 'y': 'Pays'},
                    color=pays_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig_geo.update_layout(height=500)
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("Aucune donnée géographique disponible")
        
        with col2:
            st.markdown("### 🗺️ Carte Interactive")
            
            if len(pays_counts) > 0:
                # Créer une carte
                m = folium.Map(location=[0, 0], zoom_start=2)
                
                for pays, count in pays_counts.head(15).items():
                    coords = obtenir_coordonnees_pays(pays)
                    if coords != [0, 0]:
                        folium.CircleMarker(
                            location=coords,
                            radius=max(5, count/10),  # Taille proportionnelle
                            popup=f"{pays}: {count} participants",
                            color='blue',
                            fill=True,
                            fillColor='lightblue'
                        ).add_to(m)
                
                st_folium(m, width=700, height=400)
            else:
                st.info("Aucune donnée géographique disponible pour la carte")
    else:
        st.info("Aucune donnée géographique disponible pour les filtres sélectionnés")
    
    # 3. Modes de paiement
    st.markdown("---")
    st.markdown("## 💳 Modes de Paiement Choisis")
    
    if 'methode_paiement_std' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Graphique en Donuts")
            paiement_counts = df_filtered['methode_paiement_std'].value_counts()
            
            if len(paiement_counts) > 0:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=paiement_counts.index,
                    values=paiement_counts.values,
                    hole=0.4
                )])
                fig_donut.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                fig_donut.update_layout(
                    title="Répartition des Méthodes de Paiement",
                    showlegend=True
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Aucune donnée de paiement disponible")
        
        with col2:
            st.markdown("### 📊 Graphique en Barres")
            if len(paiement_counts) > 0:
                fig_payment = px.bar(
                    x=paiement_counts.index,
                    y=paiement_counts.values,
                    title="Choix des Méthodes de Paiement",
                    labels={'x': 'Méthode de paiement', 'y': 'Nombre d\'utilisateurs'},
                    color=paiement_counts.values,
                    color_continuous_scale='Plasma'
                )
                fig_payment.update_xaxes(tickangle=45)
                st.plotly_chart(fig_payment, use_container_width=True)
            else:
                st.info("Aucune donnée de paiement disponible")
    else:
        st.info("Aucune donnée de paiement disponible pour les filtres sélectionnés")
    
    # 4. Évolution temporelle
    st.markdown("---")
    st.markdown("## 📈 Évolution Temporelle des Inscriptions")
    
    if 'horodateur' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Inscriptions par Jour")
            df_filtered['date'] = df_filtered['horodateur'].dt.date
            daily_counts = df_filtered.groupby('date').size().reset_index(name='count')
            
            if len(daily_counts) > 0:
                fig_daily = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    title="Nombre d'Inscriptions par Jour",
                    labels={'date': 'Date', 'count': 'Nombre d\'inscriptions'}
                )
                fig_daily.update_traces(mode='lines+markers')
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("Aucune donnée temporelle disponible")
        
        with col2:
            st.markdown("### 🕐 Inscriptions par Heure")
            df_filtered['heure'] = df_filtered['horodateur'].dt.hour
            hourly_counts = df_filtered.groupby('heure').size().reset_index(name='count')
            
            if len(hourly_counts) > 0:
                fig_hourly = px.bar(
                    hourly_counts,
                    x='heure',
                    y='count',
                    title="Nombre d'Inscriptions par Heure",
                    labels={'heure': 'Heure de la journée', 'count': 'Nombre d\'inscriptions'},
                    color='count',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info("Aucune donnée horaire disponible")
        
        # Analyse par jour de la semaine
        if len(df_filtered) > 0:
            st.markdown("### 📅 Inscriptions par Jour de la Semaine")
            df_filtered['jour_semaine'] = df_filtered['horodateur'].dt.day_name()
            ordre_jours = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            weekly_counts = df_filtered['jour_semaine'].value_counts().reindex(ordre_jours)
            weekly_counts.index = jours_fr
            
            if weekly_counts.sum() > 0:
                fig_weekly = px.bar(
                    x=weekly_counts.index,
                    y=weekly_counts.values,
                    title="Répartition par Jour de la Semaine",
                    labels={'x': 'Jour de la semaine', 'y': 'Nombre d\'inscriptions'},
                    color=weekly_counts.values,
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_weekly, use_container_width=True)
    else:
        st.info("Aucune donnée temporelle disponible pour les filtres sélectionnés")
    
    # 5. Statistiques d'âge
    st.markdown("---")
    st.markdown("## 🎂 Statistiques d'Âge")
    
    if 'age' in df_filtered.columns and len(df_filtered) > 0:
        st.markdown("### 📊 Distribution des Âges")
        ages_valides = df_filtered['age'].dropna()
        
        if len(ages_valides) > 0:
            fig_age_hist = px.histogram(
                ages_valides,
                nbins=20,
                title="Distribution des Âges",
                labels={'value': 'Âge', 'count': 'Nombre de personnes'},
                color_discrete_sequence=['skyblue']
            )
            fig_age_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_age_hist, use_container_width=True)
        else:
            st.info("Aucune donnée d'âge disponible")
        
        
        # Tranches d'âge
        if 'tranche_age' in df_filtered.columns and df_filtered['tranche_age'].notna().any():
            st.markdown("### 👥 Répartition par Tranches d'Âge")
            tranches_counts = df_filtered['tranche_age'].value_counts().sort_index()
            
            if len(tranches_counts) > 0:
                fig_tranches = px.bar(
                    x=tranches_counts.index,
                    y=tranches_counts.values,
                    title="Nombre de Personnes par Tranche d'Âge",
                    labels={'x': 'Tranche d\'âge', 'y': 'Nombre de personnes'},
                    color=tranches_counts.values,
                    color_continuous_scale='YlOrRd'
                )
                st.plotly_chart(fig_tranches, use_container_width=True)
    else:
        st.info("Aucune donnée d'âge disponible pour les filtres sélectionnés")
    
    # Section de téléchargement des données
    st.markdown("---")
    st.markdown("## 📥 Téléchargement des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Télécharger les données filtrées CSV"):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="💾 Télécharger CSV",
                data=csv,
                file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Télécharger les données filtrées Excel"):
            # Créer un buffer pour le fichier Excel
            from io import BytesIO
            buffer = BytesIO()
            df_filtered.to_excel(buffer, index=False)
            buffer.seek(0)
            
            st.download_button(
                label="💾 Télécharger Excel",
                data=buffer,
                file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Informations sur le téléchargement
    if len(df_filtered) != len(df):
        st.info(f"💡 Les fichiers téléchargés contiendront {len(df_filtered)} lignes (données filtrées) au lieu de {len(df)} lignes (données complètes)")
    else:
        st.info(f"💡 Les fichiers téléchargés contiendront toutes les {len(df)} lignes de données")
    
    # Footer premium
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <div style="text-align: center;">
            <h3 style="color: #1f77b4; margin-bottom: 1rem;">📊 Dashboard Pro - Analyse Formulaire</h3>
            <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: #1f77b4;">�</div>
                    <div style="font-weight: 600;">Streamlit</div>
                    <div style="color: #666; font-size: 0.9rem;">Framework</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: #ff7f0e;">📈</div>
                    <div style="font-weight: 600;">Plotly</div>
                    <div style="color: #666; font-size: 0.9rem;">Visualisations</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: #2ca02c;">🐼</div>
                    <div style="font-weight: 600;">Pandas</div>
                    <div style="color: #666; font-size: 0.9rem;">Analyse</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: #d62728;">🗺️</div>
                    <div style="font-weight: 600;">Folium</div>
                    <div style="color: #666; font-size: 0.9rem;">Cartographie</div>
                </div>
            </div>
            <div style="margin-top: 2rem; padding-top: 1rem; border-top: 2px solid #e9ecef;">
                <p style="color: #666; margin: 0;">
                    📅 Dernière mise à jour: {} | 
                    ⚡ Version 2.0 - Design Pro | 
                    📧 Analyse complète des données formulaire
                </p>
                <p style="color: #999; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                    Développé avec ❤️ par l'équipe analyse - Tous droits réservés
                </p>
            </div>
        </div>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
