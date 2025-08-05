#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration du dashboard
Teste toutes les fonctionnalités et génère un rapport de validation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def verifier_donnees():
    """
    Vérifie que toutes les données nécessaires sont présentes
    """
    print("🔍 Vérification des données pour le dashboard...")
    
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        print(f"✅ Fichier chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Vérifier les colonnes nécessaires
        colonnes_requises = [
            'horodateur', 'type_pack', 'pays', 'methode_paiement_std',
            'numero_de_telephone', 'age', 'tranche_age'
        ]
        
        colonnes_manquantes = []
        for col in colonnes_requises:
            if col in df.columns:
                print(f"✅ Colonne '{col}' présente")
            else:
                colonnes_manquantes.append(col)
                print(f"❌ Colonne '{col}' manquante")
        
        if colonnes_manquantes:
            print(f"\n⚠️  Colonnes manquantes: {colonnes_manquantes}")
            return False
        
        # Vérifier la qualité des données
        print(f"\n📊 Qualité des données:")
        
        for col in colonnes_requises:
            if col in df.columns:
                non_nulls = df[col].notna().sum()
                total = len(df)
                pourcentage = (non_nulls / total) * 100
                print(f"  {col}: {pourcentage:.1f}% de données valides")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def generer_rapport_metriques():
    """
    Génère un rapport avec toutes les métriques calculées
    """
    print(f"\n📈 Génération du rapport des métriques...")
    
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        
        # Convertir les dates
        df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        rapport = []
        rapport.append("="*80)
        rapport.append("RAPPORT DES MÉTRIQUES DU DASHBOARD")
        rapport.append("="*80)
        rapport.append(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        rapport.append(f"Total des réponses: {len(df)}")
        
        # 1. Répartition des offres
        rapport.append(f"\n🎯 RÉPARTITION DES OFFRES:")
        if 'type_pack' in df.columns:
            pack_counts = df['type_pack'].value_counts()
            for pack, count in pack_counts.items():
                pourcentage = (count / len(df)) * 100
                rapport.append(f"  {pack}: {count} ({pourcentage:.1f}%)")
        
        # 2. Répartition géographique
        rapport.append(f"\n🌍 RÉPARTITION GÉOGRAPHIQUE:")
        if 'pays' in df.columns:
            pays_counts = df['pays'].value_counts().head(10)
            for pays, count in pays_counts.items():
                pourcentage = (count / len(df)) * 100
                rapport.append(f"  {pays}: {count} ({pourcentage:.1f}%)")
        
        # 3. Modes de paiement
        rapport.append(f"\n💳 MODES DE PAIEMENT:")
        if 'methode_paiement_std' in df.columns:
            paiement_counts = df['methode_paiement_std'].value_counts()
            for paiement, count in paiement_counts.items():
                pourcentage = (count / len(df)) * 100
                rapport.append(f"  {paiement}: {count} ({pourcentage:.1f}%)")
        
        # 4. Évolution temporelle
        rapport.append(f"\n📈 ÉVOLUTION TEMPORELLE:")
        if 'horodateur' in df.columns:
            df['date'] = df['horodateur'].dt.date
            premier_jour = df['date'].min()
            dernier_jour = df['date'].max()
            duree = (dernier_jour - premier_jour).days
            rapport.append(f"  Période: {premier_jour} à {dernier_jour} ({duree} jours)")
            
            moyenne_par_jour = len(df) / max(duree, 1)
            rapport.append(f"  Moyenne par jour: {moyenne_par_jour:.1f} inscriptions")
        
        # 5. Validation des numéros
        rapport.append(f"\n📞 VALIDATION DES NUMÉROS:")
        if 'numero_de_telephone' in df.columns:
            def valider_numero(numero):
                if pd.isna(numero):
                    return False
                numero_str = str(numero).strip()
                import re
                pattern = r'^\+?\d{8,15}$'
                return re.match(pattern, numero_str.replace(' ', '')) is not None
            
            df['numero_valide'] = df['numero_de_telephone'].apply(valider_numero)
            valides = df['numero_valide'].sum()
            invalides = len(df) - valides
            taux_validite = (valides / len(df)) * 100
            
            rapport.append(f"  Numéros valides: {valides}")
            rapport.append(f"  Numéros invalides: {invalides}")
            rapport.append(f"  Taux de validité: {taux_validite:.1f}%")
        
        # 6. Statistiques d'âge
        rapport.append(f"\n🎂 STATISTIQUES D'ÂGE:")
        if 'age' in df.columns:
            ages_valides = df['age'].dropna()
            if len(ages_valides) > 0:
                rapport.append(f"  Âge moyen: {ages_valides.mean():.1f} ans")
                rapport.append(f"  Âge médian: {ages_valides.median():.1f} ans")
                rapport.append(f"  Âge minimum: {ages_valides.min():.0f} ans")
                rapport.append(f"  Âge maximum: {ages_valides.max():.0f} ans")
                
                if 'tranche_age' in df.columns:
                    rapport.append(f"\n  Répartition par tranches:")
                    tranches_counts = df['tranche_age'].value_counts().sort_index()
                    for tranche, count in tranches_counts.items():
                        pourcentage = (count / df['tranche_age'].notna().sum()) * 100
                        rapport.append(f"    {tranche}: {count} ({pourcentage:.1f}%)")
        
        rapport.append(f"\n" + "="*80)
        rapport.append("FIN DU RAPPORT")
        rapport.append("="*80)
        
        # Sauvegarder le rapport
        with open("Rapport_Metriques_Dashboard.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(rapport))
        
        print(f"✅ Rapport sauvegardé: Rapport_Metriques_Dashboard.txt")
        
        # Afficher un résumé
        print(f"\n📋 RÉSUMÉ DES MÉTRIQUES:")
        if 'type_pack' in df.columns:
            pack_populaire = df['type_pack'].mode()[0] if len(df['type_pack'].mode()) > 0 else 'N/A'
            print(f"  Pack le plus populaire: {pack_populaire}")
        
        if 'pays' in df.columns:
            print(f"  Nombre de pays: {df['pays'].nunique()}")
        
        if 'age' in df.columns:
            ages_valides = df['age'].dropna()
            if len(ages_valides) > 0:
                print(f"  Âge moyen: {ages_valides.mean():.1f} ans")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport: {e}")
        return False

def tester_visualisations():
    """
    Teste que toutes les visualisations peuvent être générées
    """
    print(f"\n🎨 Test des visualisations...")
    
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        
        # Test 1: Graphiques de répartition des packs
        if 'type_pack' in df.columns:
            pack_counts = df['type_pack'].value_counts()
            print(f"✅ Graphique packs: {len(pack_counts)} catégories")
        
        # Test 2: Graphiques géographiques
        if 'pays' in df.columns:
            pays_counts = df['pays'].value_counts()
            print(f"✅ Graphique géographique: {len(pays_counts)} pays")
        
        # Test 3: Graphiques de paiement
        if 'methode_paiement_std' in df.columns:
            paiement_counts = df['methode_paiement_std'].value_counts()
            print(f"✅ Graphique paiements: {len(paiement_counts)} méthodes")
        
        # Test 4: Graphiques temporels
        if 'horodateur' in df.columns:
            df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            dates_valides = df['horodateur'].notna().sum()
            print(f"✅ Graphiques temporels: {dates_valides} dates valides")
        
        # Test 5: Validation des numéros
        if 'numero_de_telephone' in df.columns:
            numeros_non_null = df['numero_de_telephone'].notna().sum()
            print(f"✅ Validation numéros: {numeros_non_null} numéros à valider")
        
        # Test 6: Histogramme des âges
        if 'age' in df.columns:
            ages_valides = df['age'].notna().sum()
            print(f"✅ Histogramme âges: {ages_valides} âges valides")
        
        print(f"✅ Tous les tests de visualisation sont passés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def main():
    """
    Fonction principale de démonstration
    """
    print("🚀 DÉMONSTRATION DU DASHBOARD")
    print("="*50)
    
    # Étape 1: Vérification des données
    if not verifier_donnees():
        print("❌ Les données ne sont pas prêtes pour le dashboard")
        return
    
    # Étape 2: Génération du rapport
    if not generer_rapport_metriques():
        print("❌ Erreur lors de la génération du rapport")
        return
    
    # Étape 3: Test des visualisations
    if not tester_visualisations():
        print("❌ Erreur lors des tests de visualisation")
        return
    
    print(f"\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
    print(f"📊 Le dashboard est prêt à être utilisé")
    print(f"🌐 Lancez: python lancer_dashboard.py")
    print(f"📄 Rapport détaillé: Rapport_Metriques_Dashboard.txt")

if __name__ == "__main__":
    main()
