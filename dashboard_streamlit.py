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

# Configuration de la page
st.set_page_config(
    page_title="📊 Analyse du Formulaire - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
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
    Charge les données nettoyées
    """
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        
        # Convertir les dates
        if 'horodateur' in df.columns:
            df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        if 'date_de_naissance' in df.columns:
            df['date_de_naissance'] = pd.to_datetime(df['date_de_naissance'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
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
    # Titre principal
    st.markdown('<h1 class="main-header">📊 Dashboard d\'Analyse du Formulaire</h1>', 
                unsafe_allow_html=True)
    
    # Chargement des données
    df = charger_donnees()
    
    if df is None:
        st.error("⚠️ Impossible de charger les données. Vérifiez que le fichier 'Formulaire_FINAL_OPTIMISE.xlsx' existe.")
        return
    
    # Sidebar avec informations générales et filtres
    st.sidebar.markdown("## 📋 Informations générales")
    st.sidebar.markdown(f"**Nombre total de réponses:** {len(df)}")
    st.sidebar.markdown(f"**Colonnes disponibles:** {len(df.columns)}")
    
    # Filtres de période
    df_filtered = df.copy()
    
    if 'horodateur' in df.columns and df['horodateur'].notna().any():
        st.sidebar.markdown("## 📅 Filtres de Période")
        
        # Dates min/max disponibles
        date_min = df['horodateur'].min().date()
        date_max = df['horodateur'].max().date()
        
        st.sidebar.markdown(f"**Période complète:** {date_min.strftime('%d/%m/%Y')} - {date_max.strftime('%d/%m/%Y')}")
        
        # Sélecteurs de date
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            date_debut_selectionnee = st.date_input(
                "📅 Date début",
                value=date_min,
                min_value=date_min,
                max_value=date_max,
                key="date_debut"
            )
        
        with col2:
            date_fin_selectionnee = st.date_input(
                "📅 Date fin",
                value=date_max,
                min_value=date_min,
                max_value=date_max,
                key="date_fin"
            )
        
        # Vérification des dates
        if date_debut_selectionnee > date_fin_selectionnee:
            st.sidebar.error("❌ La date de début doit être antérieure à la date de fin")
        else:
            # Filtrage des données
            mask_date = (
                (df['horodateur'].dt.date >= date_debut_selectionnee) & 
                (df['horodateur'].dt.date <= date_fin_selectionnee)
            )
            df_filtered = df[mask_date].copy()
            
            # Affichage de la période sélectionnée
            if len(df_filtered) > 0:
                st.sidebar.success(f"✅ **Période sélectionnée:** {date_debut_selectionnee.strftime('%d/%m/%Y')} - {date_fin_selectionnee.strftime('%d/%m/%Y')}")
                st.sidebar.info(f"📊 **{len(df_filtered)} réponses** dans cette période")
                
                # Bouton de réinitialisation
                if st.sidebar.button("🔄 Réinitialiser la période"):
                    st.rerun()
            else:
                st.sidebar.warning("⚠️ Aucune donnée dans cette période")
    
    # Filtres additionnels
    st.sidebar.markdown("## 🎯 Filtres Additionnels")
    
    # Filtre par pays
    if 'pays' in df_filtered.columns:
        pays_disponibles = ['Tous'] + sorted(df_filtered['pays'].dropna().unique().tolist())
        pays_selectionne = st.sidebar.selectbox(
            "🌍 Pays",
            pays_disponibles,
            key="filtre_pays"
        )
        
        if pays_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['pays'] == pays_selectionne]
    
    # Filtre par type de pack
    if 'type_pack' in df_filtered.columns:
        packs_disponibles = ['Tous'] + sorted(df_filtered['type_pack'].dropna().unique().tolist())
        pack_selectionne = st.sidebar.selectbox(
            "📦 Type de Pack",
            packs_disponibles,
            key="filtre_pack"
        )
        
        if pack_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['type_pack'] == pack_selectionne]
    
    # Filtre par méthode de paiement
    if 'methode_paiement_std' in df_filtered.columns:
        paiements_disponibles = ['Tous'] + sorted(df_filtered['methode_paiement_std'].dropna().unique().tolist())
        paiement_selectionne = st.sidebar.selectbox(
            "💳 Méthode de Paiement",
            paiements_disponibles,
            key="filtre_paiement"
        )
        
        if paiement_selectionne != 'Tous':
            df_filtered = df_filtered[df_filtered['methode_paiement_std'] == paiement_selectionne]
    
    # Informations sur le filtrage
    if len(df_filtered) != len(df):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Résumé du Filtrage")
        st.sidebar.markdown(f"**Données originales:** {len(df)}")
        st.sidebar.markdown(f"**Données filtrées:** {len(df_filtered)}")
        reduction = ((len(df) - len(df_filtered)) / len(df)) * 100
        st.sidebar.markdown(f"**Réduction:** {reduction:.1f}%")
    
    # Métriques clés en haut
    st.markdown("## 🎯 Métriques Clés")
    
    # Affichage d'alerte si données filtrées
    if len(df_filtered) != len(df):
        st.info(f"📊 Affichage basé sur **{len(df_filtered)} réponses filtrées** (sur {len(df)} au total)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Réponses</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(df_filtered)), unsafe_allow_html=True)
    
    with col2:
        if 'pays' in df_filtered.columns:
            nb_pays = df_filtered['pays'].nunique()
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Pays Représentés</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(nb_pays), unsafe_allow_html=True)
    
    with col3:
        if 'age' in df_filtered.columns and df_filtered['age'].notna().any():
            age_moyen = df_filtered['age'].mean()
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Âge Moyen</div>
                <div class="metric-value">{:.1f} ans</div>
            </div>
            """.format(age_moyen), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Âge Moyen</div>
                <div class="metric-value">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'type_pack' in df_filtered.columns and len(df_filtered) > 0:
            pack_populaire = df_filtered['type_pack'].mode()[0] if len(df_filtered['type_pack'].mode()) > 0 else 'N/A'
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Pack Populaire</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(pack_populaire), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Pack Populaire</div>
                <div class="metric-value">N/A</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 1. Répartition des offres choisies
    st.markdown("---")
    st.markdown("## 🎯 Répartition des Offres Choisies")
    
    if 'type_pack' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Graphique en Camembert")
            pack_counts = df_filtered['type_pack'].value_counts()
            
            if len(pack_counts) > 0:
                fig_pie = px.pie(
                    values=pack_counts.values,
                    names=pack_counts.index,
                    title="Répartition des Packs Choisis",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Aucune donnée de pack disponible pour cette période")
        
        with col2:
            st.markdown("### 📊 Graphique en Barres")
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
                fig_bar.update_layout(showlegend=False)
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
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        📊 Dashboard créé avec Streamlit | 
        📅 Dernière mise à jour: {} | 
        📧 Données du formulaire analysées
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
