#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse post-nettoyage pour identifier les colonnes non exploitables
"""

import pandas as pd
import numpy as np

def analyser_colonnes_exploitables(chemin_fichier):
    """
    Analyse les colonnes pour déterminer leur exploitabilité
    """
    print("🔍 Analyse de l'exploitabilité des colonnes...")
    
    df = pd.read_excel(chemin_fichier)
    
    print(f"📊 Analyse du fichier: {df.shape[0]} lignes, {df.shape[1]} colonnes\n")
    
    colonnes_a_supprimer = []
    colonnes_exploitables = []
    
    for col in df.columns:
        print(f"📋 Analyse de la colonne: '{col}'")
        
        # Statistiques de base
        total_valeurs = len(df[col])
        valeurs_non_nulles = df[col].notna().sum()
        valeurs_nulles = total_valeurs - valeurs_non_nulles
        taux_remplissage = (valeurs_non_nulles / total_valeurs) * 100
        
        print(f"  • Taux de remplissage: {taux_remplissage:.1f}% ({valeurs_non_nulles}/{total_valeurs})")
        
        # Analyser les valeurs uniques
        valeurs_uniques = df[col].dropna().nunique()
        print(f"  • Valeurs uniques: {valeurs_uniques}")
        
        # Analyser le contenu des valeurs non nulles
        valeurs_non_nulles_serie = df[col].dropna().astype(str)
        
        if len(valeurs_non_nulles_serie) > 0:
            # Vérifier si ce sont principalement des URLs, liens ou messages
            urls_ou_liens = valeurs_non_nulles_serie.str.contains(r'http|www\.|whatsapp|telegram|@', case=False, na=False).sum()
            messages_automatiques = valeurs_non_nulles_serie.str.contains(r'ecris|ecrire|whatsapp|telegram|contact|groupe', case=False, na=False).sum()
            
            print(f"  • URLs/Liens détectés: {urls_ou_liens}")
            print(f"  • Messages automatiques: {messages_automatiques}")
            
            # Afficher quelques exemples de valeurs
            echantillon = valeurs_non_nulles_serie.head(3).tolist()
            print(f"  • Exemples: {echantillon}")
        
        # Critères pour déterminer si une colonne est exploitable
        exploitable = True
        raisons_non_exploitable = []
        
        # Critère 1: Taux de remplissage très faible
        if taux_remplissage < 5:
            exploitable = False
            raisons_non_exploitable.append(f"Taux de remplissage très faible ({taux_remplissage:.1f}%)")
        
        # Critère 2: Colonne contenant principalement des messages/instructions
        if len(valeurs_non_nulles_serie) > 0:
            taux_messages = (messages_automatiques / len(valeurs_non_nulles_serie)) * 100
            if taux_messages > 80:
                exploitable = False
                raisons_non_exploitable.append(f"Contient principalement des messages automatiques ({taux_messages:.1f}%)")
        
        # Critère 3: Valeur unique répétée (pas d'information)
        if valeurs_uniques <= 1:
            exploitable = False
            raisons_non_exploitable.append("Une seule valeur unique (pas d'information discriminante)")
        
        # Critère 4: Colonnes contenant des instructions ou des liens
        nom_col_lower = col.lower()
        if any(mot in nom_col_lower for mot in ['ecrire', 'whatsapp', 'telegram', 'groupe', 'contact', 'finaliser']):
            exploitable = False
            raisons_non_exploitable.append("Colonne d'instruction ou de contact")
        
        if exploitable:
            colonnes_exploitables.append(col)
            print(f"  ✅ EXPLOITABLE")
        else:
            colonnes_a_supprimer.append(col)
            print(f"  ❌ NON EXPLOITABLE - Raisons: {'; '.join(raisons_non_exploitable)}")
        
        print()
    
    # Résumé
    print("="*80)
    print("📊 RÉSUMÉ DE L'ANALYSE")
    print("="*80)
    
    print(f"\n✅ COLONNES EXPLOITABLES ({len(colonnes_exploitables)}):")
    for i, col in enumerate(colonnes_exploitables, 1):
        print(f"  {i}. {col}")
    
    print(f"\n❌ COLONNES À SUPPRIMER ({len(colonnes_a_supprimer)}):")
    for i, col in enumerate(colonnes_a_supprimer, 1):
        print(f"  {i}. {col}")
    
    return df, colonnes_exploitables, colonnes_a_supprimer

def creer_fichier_final(df, colonnes_exploitables, chemin_sortie):
    """
    Crée le fichier final avec seulement les colonnes exploitables
    """
    print(f"\n💾 Création du fichier final avec {len(colonnes_exploitables)} colonnes exploitables...")
    
    df_final = df[colonnes_exploitables].copy()
    
    try:
        df_final.to_excel(chemin_sortie, index=False)
        print(f"✅ Fichier final sauvegardé: {chemin_sortie}")
        print(f"📏 Dimensions finales: {df_final.shape[0]} lignes, {df_final.shape[1]} colonnes")
        
        # Afficher les statistiques finales
        print(f"\n📋 COLONNES FINALES:")
        for i, col in enumerate(df_final.columns, 1):
            taux_remplissage = (df_final[col].notna().sum() / len(df_final)) * 100
            print(f"  {i}. {col} (remplissage: {taux_remplissage:.1f}%)")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

def analyser_donnees_metier(df):
    """
    Analyse spécifique aux données métier du formulaire
    """
    print("\n🎯 ANALYSE MÉTIER DES DONNÉES")
    print("="*50)
    
    # Analyser les offres/packs
    if 'quelle_offre_choisis_-tu' in df.columns:
        print("\n📦 ANALYSE DES OFFRES:")
        offres = df['quelle_offre_choisis_-tu'].value_counts()
        print(offres)
        
        # Nettoyer et standardiser les offres
        print("\n🧹 Standardisation des offres suggérée:")
        for offre in offres.index:
            if pd.notna(offre):
                if 'premium' in str(offre).lower():
                    print(f"  '{offre}' → 'Pack Premium'")
                elif 'essentiel' in str(offre).lower():
                    print(f"  '{offre}' → 'Pack Essentiel'")
                elif 'standard' in str(offre).lower():
                    print(f"  '{offre}' → 'Pack Standard'")
    
    # Analyser les pays
    if 'pays' in df.columns:
        print(f"\n🌍 ANALYSE DES PAYS:")
        pays = df['pays'].value_counts()
        print(pays.head(10))
    
    # Analyser les méthodes de paiement
    if 'comment_souhaites-tu_payer' in df.columns:
        print(f"\n💳 ANALYSE DES MÉTHODES DE PAIEMENT:")
        paiements = df['comment_souhaites-tu_payer'].value_counts()
        print(paiements)
    
    # Analyser les âges
    if 'date_de_naissance' in df.columns:
        print(f"\n👥 ANALYSE DES ÂGES:")
        # Calculer les âges à partir des dates de naissance
        try:
            from datetime import datetime
            dates_naissance = pd.to_datetime(df['date_de_naissance'], errors='coerce')
            ages = (datetime.now() - dates_naissance).dt.days // 365
            ages_valides = ages.dropna()
            
            if len(ages_valides) > 0:
                print(f"  Âge moyen: {ages_valides.mean():.1f} ans")
                print(f"  Âge médian: {ages_valides.median():.1f} ans")
                print(f"  Âge min: {ages_valides.min()} ans")
                print(f"  Âge max: {ages_valides.max()} ans")
                
                # Distribution par tranches d'âge
                tranches = pd.cut(ages_valides, bins=[0, 18, 25, 30, 35, 40, 100], labels=['<18', '18-25', '25-30', '30-35', '35-40', '40+'])
                print(f"\n  Distribution par tranches d'âge:")
                print(tranches.value_counts().sort_index())
        except:
            print("  Impossible de calculer les âges")

if __name__ == "__main__":
    # Analyser le fichier nettoyé
    chemin_fichier_nettoye = "Formulaire sans titre (réponses)_nettoye.xlsx"
    
    df, colonnes_exploitables, colonnes_a_supprimer = analyser_colonnes_exploitables(chemin_fichier_nettoye)
    
    # Créer le fichier final optimisé
    chemin_final = "Formulaire_nettoye_final.xlsx"
    df_final = creer_fichier_final(df, colonnes_exploitables, chemin_final)
    
    if df_final is not None:
        # Analyse métier
        analyser_donnees_metier(df_final)
        
        print(f"\n🎉 NETTOYAGE COMPLET TERMINÉ!")
        print(f"📁 Fichier original: Formulaire sans titre (réponses).xlsx")
        print(f"📁 Fichier nettoyé: {chemin_fichier_nettoye}")
        print(f"📁 Fichier final optimisé: {chemin_final}")
