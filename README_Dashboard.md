# 📊 Dashboard d'Analyse du Formulaire

Ce dashboard Streamlit fournit une interface web interactive pour analyser les données du formulaire nettoyé.

## 🚀 Lancement Rapide

### Méthode 1 : Script de lancement
```bash
python lancer_dashboard.py
```

### Méthode 2 : Commande directe
```bash
streamlit run dashboard_streamlit.py
```

## 📈 Fonctionnalités du Dashboard

### 🎯 Métriques Clés Affichées

#### 1. **Répartition des Offres Choisies**
- 📊 **Graphiques** : Camembert et barres horizontales
- 📋 **Détails** : Nombre d'inscrits par pack (Premium, Essentiel, Standard, Avantage)
- 💰 **Analyse** : Prix moyens, min et max par pack

#### 2. **Répartition Géographique**
- 🌍 **Graphiques** : Histogramme et carte interactive
- 📍 **Données** : Nombre de participants par pays
- 🗺️ **Visualisation** : Carte avec marqueurs proportionnels

#### 3. **Modes de Paiement**
- 💳 **Graphiques** : Barres et donuts
- 📊 **Analyse** : Répartition des choix (Mobile Money, Carte Bancaire, etc.)

#### 4. **Évolution Temporelle**
- 📈 **Graphiques** : Lignes temporelles
- 🕐 **Analyses** : 
  - Inscriptions par jour
  - Inscriptions par heure
  - Répartition par jour de la semaine

#### 5. **Validation des Numéros**
- 📞 **Statistiques** : Compteurs valide/invalide
- ✅ **Taux** : Pourcentage de numéros au bon format
- 🔍 **Détails** : Échantillon des numéros problématiques

#### 6. **Statistiques d'Âge**
- 🎂 **Graphiques** : Histogramme des âges
- 📊 **Statistiques** : Moyenne, médiane, écart-type
- 👥 **Tranches** : Distribution par groupes d'âge

## 🛠️ Configuration Technique

### Prérequis
- Python 3.7+
- Fichier `Formulaire_FINAL_OPTIMISE.xlsx` dans le même répertoire

### Bibliothèques Utilisées
- `streamlit` : Interface web
- `plotly` : Graphiques interactifs
- `pandas` : Manipulation des données
- `folium` : Cartes interactives
- `matplotlib` & `seaborn` : Graphiques statistiques

### Port par Défaut
- **URL locale** : http://localhost:8501

## 📁 Structure des Fichiers

```
├── dashboard_streamlit.py       # Application principale
├── lancer_dashboard.py         # Script de lancement
├── Formulaire_FINAL_OPTIMISE.xlsx  # Données nettoyées
├── .streamlit/
│   └── config.toml             # Configuration Streamlit
└── README_Dashboard.md         # Ce fichier
```

## 🎨 Fonctionnalités Interactives

### 📊 Graphiques Interactifs
- **Zoom** et **panoramique** sur tous les graphiques
- **Survol** pour afficher les détails
- **Légendes** cliquables pour filtrer

### 💾 Téléchargements
- **CSV** : Export des données pour Excel/analyse
- **Excel** : Fichier formaté avec toutes les colonnes

### 📱 Interface Responsive
- Compatible mobile, tablette et desktop
- Sidebar avec informations générales
- Cartes métriques en haut de page

## 🚨 Dépannage

### Le dashboard ne se lance pas
```bash
# Vérifier l'installation de Streamlit
pip install streamlit plotly folium streamlit-folium

# Relancer avec plus de détails
streamlit run dashboard_streamlit.py --logger.level=debug
```

### Données non trouvées
- Vérifier que `Formulaire_FINAL_OPTIMISE.xlsx` est dans le bon répertoire
- S'assurer que le fichier n'est pas corrompu

### Port déjà utilisé
```bash
# Utiliser un autre port
streamlit run dashboard_streamlit.py --server.port 8502
```

## 📈 Utilisation Recommandée

1. **Lancement** : Utilisez `python lancer_dashboard.py`
2. **Navigation** : Explorez les différentes sections dans l'ordre
3. **Analyse** : Utilisez les graphiques interactifs pour approfondir
4. **Export** : Téléchargez les données pour des analyses externes

## 🎯 Cas d'Usage

### Pour le Marketing
- Analyser les préférences géographiques
- Identifier les heures d'affluence
- Comprendre les choix de packs

### Pour les Ventes
- Suivre l'évolution des inscriptions
- Analyser les méthodes de paiement préférées
- Identifier les segments d'âge cibles

### Pour la Qualité
- Vérifier la validité des données de contact
- Identifier les problèmes de saisie
- Contrôler la cohérence géographique

---

**🎉 Profitez de votre analyse de données interactive !**
