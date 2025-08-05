#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de finalisation du nettoyage avec standardisation avancée des packs
"""

import pandas as pd
import numpy as np
import re

def standardiser_packs_avance(df):
    """
    Standardise les noms de packs et extrait les prix
    """
    print("📦 Standardisation avancée des packs...")
    
    if 'quelle_offre_choisis_-tu' not in df.columns:
        return df
    
    # Créer deux nouvelles colonnes
    df['type_pack'] = ''
    df['prix_pack_fcfa'] = np.nan
    
    for index, row in df.iterrows():
        offre = str(row['quelle_offre_choisis_-tu']).lower().strip()
        
        # Extraire le type de pack
        if 'essentiel' in offre:
            df.at[index, 'type_pack'] = 'Essentiel'
        elif 'premium' in offre:
            df.at[index, 'type_pack'] = 'Premium'
        elif 'standard' in offre:
            df.at[index, 'type_pack'] = 'Standard'
        elif 'avantage' in offre:
            df.at[index, 'type_pack'] = 'Avantage'
        else:
            df.at[index, 'type_pack'] = 'Autre'
        
        # Extraire le prix
        prix_match = re.search(r'(\d+\s*\d*)\s*000\s*fcfa', offre)
        if prix_match:
            prix_str = prix_match.group(1).replace(' ', '')
            try:
                prix = int(prix_str) * 1000
                df.at[index, 'prix_pack_fcfa'] = prix
            except:
                pass
    
    print("✅ Packs standardisés avec extraction des prix")
    
    # Afficher le résumé
    print("\n📊 Distribution des types de packs:")
    print(df['type_pack'].value_counts())
    
    print("\n💰 Distribution des prix:")
    print(df['prix_pack_fcfa'].value_counts().sort_index())
    
    return df

def standardiser_paiements(df):
    """
    Standardise les méthodes de paiement
    """
    print("\n💳 Standardisation des méthodes de paiement...")
    
    if 'comment_souhaites-tu_payer' not in df.columns:
        return df
    
    df['methode_paiement_std'] = ''
    
    for index, row in df.iterrows():
        paiement = str(row['comment_souhaites-tu_payer']).lower().strip()
        
        if any(mot in paiement for mot in ['mobile money', 'orange money', 'mtn money', 'wave', 'airtel money', 'moov', 'flooz', 'tmoney', 'lumicash', 'mpesa']):
            df.at[index, 'methode_paiement_std'] = 'Mobile Money'
        elif 'carte bancaire' in paiement:
            df.at[index, 'methode_paiement_std'] = 'Carte Bancaire'
        elif any(mot in paiement for mot in ['western union', 'money gram', 'werstern union']):
            df.at[index, 'methode_paiement_std'] = 'Transfert International'
        elif 'crypto' in paiement:
            df.at[index, 'methode_paiement_std'] = 'Cryptomonnaie'
        elif any(mot in paiement for mot in ["n'ai pas", "n'es pas"]):
            df.at[index, 'methode_paiement_std'] = 'Pas de moyen'
        else:
            df.at[index, 'methode_paiement_std'] = 'Autre'
    
    print("✅ Méthodes de paiement standardisées")
    
    print("\n📊 Distribution des méthodes standardisées:")
    print(df['methode_paiement_std'].value_counts())
    
    return df

def creer_colonnes_demographiques(df):
    """
    Crée des colonnes démographiques utiles
    """
    print("\n👥 Création de colonnes démographiques...")
    
    if 'date_de_naissance' in df.columns:
        # Calculer l'âge
        from datetime import datetime
        
        dates_naissance = pd.to_datetime(df['date_de_naissance'], errors='coerce', dayfirst=True)
        ages = (datetime.now() - dates_naissance).dt.days // 365
        df['age'] = ages
        
        # Créer des tranches d'âge
        df['tranche_age'] = pd.cut(ages, 
                                  bins=[0, 18, 25, 30, 35, 40, 100], 
                                  labels=['<18', '18-25', '25-30', '30-35', '35-40', '40+'],
                                  right=False)
        
        # Créer une colonne génération
        df['generation'] = pd.cut(ages,
                                 bins=[0, 18, 25, 35, 50, 100],
                                 labels=['Très jeune', 'Gen Z', 'Millennial', 'Gen X', 'Boomer+'],
                                 right=False)
        
        print("✅ Colonnes d'âge créées")
    
    # Analyser les domaines d'email
    if 'adresse_e-mail' in df.columns:
        df['domaine_email'] = df['adresse_e-mail'].str.extract(r'@(.+)')
        
        # Catégoriser les domaines
        df['type_email'] = df['domaine_email'].apply(lambda x: 
            'Gmail' if 'gmail' in str(x).lower() else
            'Yahoo' if 'yahoo' in str(x).lower() else
            'Outlook' if any(d in str(x).lower() for d in ['outlook', 'hotmail', 'live']) else
            'Professionnel' if any(d in str(x).lower() for d in ['.com', '.org', '.net']) and not any(d in str(x).lower() for d in ['gmail', 'yahoo', 'hotmail', 'outlook']) else
            'Autre'
        )
        
        print("✅ Analyse des domaines email effectuée")
    
    return df

def nettoyer_donnees_finales(df):
    """
    Nettoyage final des données
    """
    print("\n🧹 Nettoyage final des données...")
    
    # Nettoyer les noms et prénoms
    for col in ['nom', 'prenom']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)  # Espaces multiples
    
    # Nettoyer les pays
    if 'pays' in df.columns:
        df['pays'] = df['pays'].astype(str).str.strip().str.title()
        
        # Corrections spécifiques
        df['pays'] = df['pays'].replace({
            'Rdc': 'République Démocratique du Congo',
            'République Démocratique Du Congo': 'République Démocratique du Congo',
            "Côte D'Ivoire": "Côte d'Ivoire",
            "Côte D'Ivoire": "Côte d'Ivoire"
        })
    
    # Supprimer les âges aberrants
    if 'age' in df.columns:
        # Marquer les âges suspects comme NaN
        df.loc[(df['age'] < 10) | (df['age'] > 70), 'age'] = np.nan
        df.loc[df['age'].isna(), 'tranche_age'] = np.nan
        df.loc[df['age'].isna(), 'generation'] = np.nan
    
    print("✅ Nettoyage final terminé")
    
    return df

def creer_rapport_final(df, chemin_rapport):
    """
    Crée un rapport détaillé du nettoyage
    """
    print(f"\n📊 Création du rapport final...")
    
    rapport = []
    rapport.append("="*80)
    rapport.append("RAPPORT DE NETTOYAGE DU FORMULAIRE")
    rapport.append("="*80)
    rapport.append(f"Date de traitement: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")
    rapport.append(f"Nombre total de réponses: {len(df)}")
    rapport.append(f"Nombre de colonnes finales: {len(df.columns)}")
    
    rapport.append("\n" + "="*50)
    rapport.append("COLONNES DISPONIBLES")
    rapport.append("="*50)
    
    for i, col in enumerate(df.columns, 1):
        taux_remplissage = (df[col].notna().sum() / len(df)) * 100
        rapport.append(f"{i:2d}. {col:<40} (remplissage: {taux_remplissage:5.1f}%)")
    
    # Statistiques par section
    rapport.append("\n" + "="*50)
    rapport.append("STATISTIQUES DÉTAILLÉES")
    rapport.append("="*50)
    
    # Types de packs
    if 'type_pack' in df.columns:
        rapport.append("\n📦 DISTRIBUTION DES PACKS:")
        for pack, count in df['type_pack'].value_counts().items():
            pourcentage = (count / len(df)) * 100
            rapport.append(f"  {pack:<15}: {count:3d} ({pourcentage:5.1f}%)")
    
    # Prix des packs
    if 'prix_pack_fcfa' in df.columns:
        rapport.append("\n💰 PRIX DES PACKS (FCFA):")
        for prix, count in df['prix_pack_fcfa'].value_counts().sort_index().items():
            pourcentage = (count / len(df)) * 100
            rapport.append(f"  {prix:>8,.0f} FCFA: {count:3d} ({pourcentage:5.1f}%)")
    
    # Pays
    if 'pays' in df.columns:
        rapport.append("\n🌍 TOP 10 DES PAYS:")
        top_pays = df['pays'].value_counts().head(10)
        for pays, count in top_pays.items():
            pourcentage = (count / len(df)) * 100
            rapport.append(f"  {pays:<35}: {count:3d} ({pourcentage:5.1f}%)")
    
    # Tranches d'âge
    if 'tranche_age' in df.columns:
        rapport.append("\n👥 DISTRIBUTION PAR ÂGE:")
        for tranche, count in df['tranche_age'].value_counts().sort_index().items():
            pourcentage = (count / df['tranche_age'].notna().sum()) * 100
            rapport.append(f"  {tranche:<10}: {count:3d} ({pourcentage:5.1f}%)")
    
    # Méthodes de paiement
    if 'methode_paiement_std' in df.columns:
        rapport.append("\n💳 MÉTHODES DE PAIEMENT:")
        for methode, count in df['methode_paiement_std'].value_counts().items():
            pourcentage = (count / len(df)) * 100
            rapport.append(f"  {methode:<25}: {count:3d} ({pourcentage:5.1f}%)")
    
    # Types d'email
    if 'type_email' in df.columns:
        rapport.append("\n📧 TYPES D'EMAIL:")
        for type_email, count in df['type_email'].value_counts().items():
            pourcentage = (count / len(df)) * 100
            rapport.append(f"  {type_email:<15}: {count:3d} ({pourcentage:5.1f}%)")
    
    rapport.append("\n" + "="*80)
    rapport.append("FIN DU RAPPORT")
    rapport.append("="*80)
    
    # Sauvegarder le rapport
    with open(chemin_rapport, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rapport))
    
    print(f"✅ Rapport sauvegardé: {chemin_rapport}")
    
    # Afficher un résumé
    print("\n📋 RÉSUMÉ FINAL:")
    print(f"  • {len(df)} réponses au formulaire")
    print(f"  • {len(df.columns)} colonnes exploitables")
    print(f"  • {df['pays'].nunique()} pays représentés")
    if 'age' in df.columns:
        print(f"  • Âge moyen: {df['age'].mean():.1f} ans")
    if 'type_pack' in df.columns:
        pack_principal = df['type_pack'].mode()[0] if len(df['type_pack'].mode()) > 0 else 'N/A'
        print(f"  • Pack le plus populaire: {pack_principal}")

def main():
    """
    Fonction principale de finalisation
    """
    print("🚀 FINALISATION DU NETTOYAGE DU FORMULAIRE")
    print("="*60)
    
    # Charger le fichier nettoyé
    chemin_fichier = "Formulaire_nettoye_final.xlsx"
    
    try:
        df = pd.read_excel(chemin_fichier)
        print(f"✅ Fichier chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return
    
    # Appliquer les améliorations
    df = standardiser_packs_avance(df)
    df = standardiser_paiements(df)
    df = creer_colonnes_demographiques(df)
    df = nettoyer_donnees_finales(df)
    
    # Réorganiser les colonnes dans un ordre logique
    colonnes_ordre = [
        'horodateur',
        'nom', 'prenom', 'age', 'tranche_age', 'generation',
        'date_de_naissance', 'pays',
        'adresse_e-mail', 'domaine_email', 'type_email',
        'numero_de_telephone',
        'type_pack', 'prix_pack_fcfa', 'quelle_offre_choisis_-tu',
        'methode_paiement_std', 'comment_souhaites-tu_payer',
        'si_tu_as_des_questions_ou_un_truc_a_dire_cest...'
    ]
    
    # Garder seulement les colonnes qui existent
    colonnes_finales = [col for col in colonnes_ordre if col in df.columns]
    df_final = df[colonnes_finales].copy()
    
    # Sauvegarder le fichier final optimisé
    chemin_final = "Formulaire_FINAL_OPTIMISE.xlsx"
    try:
        df_final.to_excel(chemin_final, index=False)
        print(f"\n💾 Fichier final sauvegardé: {chemin_final}")
        print(f"📏 Dimensions: {df_final.shape[0]} lignes, {df_final.shape[1]} colonnes")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return
    
    # Créer le rapport final
    chemin_rapport = "Rapport_Nettoyage_Formulaire.txt"
    creer_rapport_final(df_final, chemin_rapport)
    
    print(f"\n🎉 NETTOYAGE COMPLET TERMINÉ!")
    print(f"📁 Fichier final: {chemin_final}")
    print(f"📊 Rapport détaillé: {chemin_rapport}")

if __name__ == "__main__":
    main()
