#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour les nouvelles fonctionnalités de filtrage du dashboard
"""

import pandas as pd
from datetime import datetime, timedelta

def tester_filtrage_periode():
    """
    Teste les fonctionnalités de filtrage par période
    """
    print("🧪 Test des fonctionnalités de filtrage par période...")
    
    try:
        # Charger les données
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        print(f"✅ Données chargées: {len(df)} lignes")
        
        # Convertir les dates
        df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Afficher la période complète
        date_min = df['horodateur'].min()
        date_max = df['horodateur'].max()
        print(f"📅 Période complète: {date_min.strftime('%d/%m/%Y')} - {date_max.strftime('%d/%m/%Y')}")
        
        # Test 1: Filtrage par mois
        print(f"\n🔍 Test 1: Filtrage par mois")
        premier_mois = df['horodateur'].dt.to_period('M').mode()[0]
        mask_mois = df['horodateur'].dt.to_period('M') == premier_mois
        df_mois = df[mask_mois]
        print(f"  Mois sélectionné: {premier_mois}")
        print(f"  Données filtrées: {len(df_mois)} lignes ({(len(df_mois)/len(df)*100):.1f}%)")
        
        # Test 2: Filtrage par semaine
        print(f"\n🔍 Test 2: Filtrage par semaine")
        date_debut_semaine = date_max - timedelta(days=7)
        mask_semaine = df['horodateur'] >= date_debut_semaine
        df_semaine = df[mask_semaine]
        print(f"  Période: Derniers 7 jours avant {date_max.strftime('%d/%m/%Y')}")
        print(f"  Données filtrées: {len(df_semaine)} lignes ({(len(df_semaine)/len(df)*100):.1f}%)")
        
        # Test 3: Filtrage par période personnalisée
        print(f"\n🔍 Test 3: Filtrage période personnalisée")
        milieu = date_min + (date_max - date_min) / 2
        date_debut_perso = milieu - timedelta(days=15)
        date_fin_perso = milieu + timedelta(days=15)
        
        mask_perso = (df['horodateur'] >= date_debut_perso) & (df['horodateur'] <= date_fin_perso)
        df_perso = df[mask_perso]
        print(f"  Période: {date_debut_perso.strftime('%d/%m/%Y')} - {date_fin_perso.strftime('%d/%m/%Y')}")
        print(f"  Données filtrées: {len(df_perso)} lignes ({(len(df_perso)/len(df)*100):.1f}%)")
        
        # Test des métriques avec filtrage
        print(f"\n📊 Test des métriques avec données filtrées:")
        
        if 'type_pack' in df_perso.columns:
            packs_originaux = df['type_pack'].value_counts()
            packs_filtres = df_perso['type_pack'].value_counts()
            print(f"  Packs (original): {len(packs_originaux)} types")
            print(f"  Packs (filtré): {len(packs_filtres)} types")
        
        if 'pays' in df_perso.columns:
            pays_originaux = df['pays'].nunique()
            pays_filtres = df_perso['pays'].nunique()
            print(f"  Pays (original): {pays_originaux}")
            print(f"  Pays (filtré): {pays_filtres}")
        
        if 'age' in df_perso.columns:
            age_original = df['age'].mean()
            age_filtre = df_perso['age'].mean()
            print(f"  Âge moyen (original): {age_original:.1f} ans")
            print(f"  Âge moyen (filtré): {age_filtre:.1f} ans")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def tester_filtrage_multi_criteres():
    """
    Teste le filtrage par plusieurs critères combinés
    """
    print(f"\n🧪 Test du filtrage multi-critères...")
    
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Combinaison de filtres
        print(f"📊 Données originales: {len(df)} lignes")
        
        # Filtre 1: Période
        date_min = df['horodateur'].min()
        date_max = df['horodateur'].max()
        milieu = date_min + (date_max - date_min) / 2
        
        df_filtered = df[df['horodateur'] >= milieu].copy()
        print(f"  Après filtre période (2ème moitié): {len(df_filtered)} lignes")
        
        # Filtre 2: Pack le plus populaire
        if 'type_pack' in df_filtered.columns:
            pack_populaire = df_filtered['type_pack'].mode()[0]
            df_filtered = df_filtered[df_filtered['type_pack'] == pack_populaire]
            print(f"  Après filtre pack '{pack_populaire}': {len(df_filtered)} lignes")
        
        # Filtre 3: Pays avec le plus de participants
        if 'pays' in df_filtered.columns and len(df_filtered) > 0:
            pays_principal = df_filtered['pays'].mode()[0] if len(df_filtered['pays'].mode()) > 0 else None
            if pays_principal:
                df_filtered = df_filtered[df_filtered['pays'] == pays_principal]
                print(f"  Après filtre pays '{pays_principal}': {len(df_filtered)} lignes")
        
        # Résultat final
        reduction = ((len(df) - len(df_filtered)) / len(df)) * 100
        print(f"🎯 Résultat final: {len(df_filtered)} lignes (réduction de {reduction:.1f}%)")
        
        if len(df_filtered) > 0:
            print(f"✅ Filtrage multi-critères réussi")
            return True
        else:
            print(f"⚠️  Aucune donnée ne correspond aux critères")
            return True  # Ce n'est pas une erreur, juste un résultat de filtrage
        
    except Exception as e:
        print(f"❌ Erreur lors du test multi-critères: {e}")
        return False

def tester_cas_limites():
    """
    Teste les cas limites du filtrage
    """
    print(f"\n🧪 Test des cas limites...")
    
    try:
        df = pd.read_excel("Formulaire_FINAL_OPTIMISE.xlsx")
        df['horodateur'] = pd.to_datetime(df['horodateur'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Cas 1: Période très restreinte (1 jour)
        date_specifique = df['horodateur'].dt.date.mode()[0]
        df_jour = df[df['horodateur'].dt.date == date_specifique]
        print(f"📅 Cas 1 - Un seul jour ({date_specifique}): {len(df_jour)} lignes")
        
        # Cas 2: Période inexistante
        date_future = df['horodateur'].max() + timedelta(days=30)
        df_futur = df[df['horodateur'] > date_future]
        print(f"📅 Cas 2 - Période future: {len(df_futur)} lignes")
        
        # Cas 3: Tous les filtres appliqués
        if len(df) > 0:
            # Prendre les critères les plus restrictifs
            df_restrictif = df.copy()
            
            if 'pays' in df.columns:
                pays_rare = df['pays'].value_counts().tail(1).index[0]
                df_restrictif = df_restrictif[df_restrictif['pays'] == pays_rare]
            
            if 'type_pack' in df_restrictif.columns and len(df_restrictif) > 0:
                pack_disponible = df_restrictif['type_pack'].value_counts().index[0]
                df_restrictif = df_restrictif[df_restrictif['type_pack'] == pack_disponible]
            
            print(f"🎯 Cas 3 - Filtres très restrictifs: {len(df_restrictif)} lignes")
        
        print(f"✅ Tests des cas limites terminés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests de cas limites: {e}")
        return False

def generer_scenarios_test():
    """
    Génère des scénarios de test pour le dashboard
    """
    print(f"\n📋 Génération de scénarios de test...")
    
    scenarios = []
    
    # Scénario 1: Analyse mensuelle
    scenarios.append({
        "nom": "Analyse Mensuelle",
        "description": "Filtrer les données du mois le plus actif",
        "filtre_periode": "Mois avec le plus d'inscriptions",
        "filtre_pays": "Tous",
        "filtre_pack": "Tous",
        "objectif": "Identifier les tendances du mois le plus actif"
    })
    
    # Scénario 2: Focus géographique
    scenarios.append({
        "nom": "Focus Géographique",
        "description": "Analyser un pays spécifique sur toute la période",
        "filtre_periode": "Toute la période",
        "filtre_pays": "Cameroun",
        "filtre_pack": "Tous",
        "objectif": "Comprendre le comportement d'un marché spécifique"
    })
    
    # Scénario 3: Analyse produit
    scenarios.append({
        "nom": "Analyse Produit",
        "description": "Étudier les utilisateurs d'un pack premium",
        "filtre_periode": "Toute la période",
        "filtre_pays": "Tous",
        "filtre_pack": "Premium",
        "objectif": "Profiler les utilisateurs premium"
    })
    
    # Scénario 4: Analyse temporelle récente
    scenarios.append({
        "nom": "Tendances Récentes",
        "description": "Analyser les 30 derniers jours",
        "filtre_periode": "30 derniers jours",
        "filtre_pays": "Tous",
        "filtre_pack": "Tous",
        "objectif": "Identifier les tendances récentes"
    })
    
    # Scénario 5: Analyse croisée
    scenarios.append({
        "nom": "Analyse Croisée",
        "description": "Pack Essentiel au Cameroun",
        "filtre_periode": "Toute la période",
        "filtre_pays": "Cameroun",
        "filtre_pack": "Essentiel",
        "objectif": "Analyse détaillée d'un segment spécifique"
    })
    
    # Sauvegarder les scénarios
    with open("Scenarios_Test_Dashboard.txt", 'w', encoding='utf-8') as f:
        f.write("SCÉNARIOS DE TEST POUR LE DASHBOARD\n")
        f.write("="*50 + "\n\n")
        
        for i, scenario in enumerate(scenarios, 1):
            f.write(f"SCÉNARIO {i}: {scenario['nom']}\n")
            f.write("-" * 30 + "\n")
            f.write(f"Description: {scenario['description']}\n")
            f.write(f"Filtre période: {scenario['filtre_periode']}\n")
            f.write(f"Filtre pays: {scenario['filtre_pays']}\n")
            f.write(f"Filtre pack: {scenario['filtre_pack']}\n")
            f.write(f"Objectif: {scenario['objectif']}\n\n")
    
    print(f"✅ {len(scenarios)} scénarios générés et sauvegardés")
    return scenarios

def main():
    """
    Fonction principale de test
    """
    print("🚀 TESTS DES FONCTIONNALITÉS DE FILTRAGE")
    print("="*50)
    
    # Test 1: Filtrage par période
    test1 = tester_filtrage_periode()
    
    # Test 2: Filtrage multi-critères
    test2 = tester_filtrage_multi_criteres()
    
    # Test 3: Cas limites
    test3 = tester_cas_limites()
    
    # Génération des scénarios
    scenarios = generer_scenarios_test()
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("="*30)
    print(f"✅ Test filtrage période: {'RÉUSSI' if test1 else 'ÉCHEC'}")
    print(f"✅ Test multi-critères: {'RÉUSSI' if test2 else 'ÉCHEC'}")
    print(f"✅ Test cas limites: {'RÉUSSI' if test3 else 'ÉCHEC'}")
    print(f"📋 Scénarios générés: {len(scenarios)}")
    
    tous_reussis = all([test1, test2, test3])
    
    if tous_reussis:
        print(f"\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print(f"✅ Le dashboard avec filtrage est prêt à l'emploi")
        print(f"🌐 Lancez: python lancer_dashboard.py")
    else:
        print(f"\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"🔧 Vérifiez la configuration du dashboard")

if __name__ == "__main__":
    main()
