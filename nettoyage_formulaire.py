#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage du formulaire Excel
Objectifs :
- Renommer les colonnes (supprimer \n, accents, phrases longues)
- Uniformiser les dates
- Nettoyer les numéros de téléphone
- Standardiser les réponses des packs
- Harmoniser les noms de pays
- Supprimer les colonnes vides
"""

import pandas as pd
import re
from unidecode import unidecode
import phonenumbers
from phonenumbers import geocoder, carrier
import numpy as np
from datetime import datetime

def nettoyer_nom_colonne(nom):
    """
    Nettoie le nom d'une colonne en supprimant les caractères spéciaux,
    les accents et en raccourcissant les phrases longues
    """
    if pd.isna(nom):
        return "colonne_vide"
    
    # Convertir en string
    nom = str(nom)
    
    # Supprimer les \n et remplacer par des espaces
    nom = nom.replace('\n', ' ').replace('\r', ' ')
    
    # Supprimer les accents
    nom = unidecode(nom)
    
    # Supprimer les caractères spéciaux sauf espaces et tirets
    nom = re.sub(r'[^\w\s-]', '', nom)
    
    # Remplacer les espaces multiples par un seul
    nom = re.sub(r'\s+', '_', nom)
    
    # Raccourcir si trop long (garder les 50 premiers caractères)
    if len(nom) > 50:
        # Essayer de couper au dernier mot complet
        nom_court = nom[:47]
        dernier_underscore = nom_court.rfind('_')
        if dernier_underscore > 20:  # S'assurer qu'on garde au moins 20 caractères
            nom = nom_court[:dernier_underscore] + "..."
        else:
            nom = nom[:47] + "..."
    
    # Supprimer les underscores en début et fin
    nom = nom.strip('_')
    
    return nom.lower() if nom else "colonne_vide"

def detecter_colonnes_vides(df):
    """
    Détecte les colonnes complètement vides ou avec que des valeurs nulles
    """
    colonnes_vides = []
    for col in df.columns:
        # Vérifier si la colonne est complètement vide
        if df[col].isna().all() or (df[col].astype(str).str.strip() == '').all():
            colonnes_vides.append(col)
    return colonnes_vides

def nettoyer_telephone(numero, pays_defaut='FR'):
    """
    Nettoie et formate un numéro de téléphone au format international
    """
    if pd.isna(numero):
        return np.nan
    
    numero_str = str(numero).strip()
    if not numero_str or numero_str.lower() in ['nan', 'none', '']:
        return np.nan
    
    try:
        # Essayer de parser le numéro
        numero_parse = phonenumbers.parse(numero_str, pays_defaut)
        
        # Vérifier si le numéro est valide
        if phonenumbers.is_valid_number(numero_parse):
            return phonenumbers.format_number(numero_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        else:
            return numero_str  # Retourner le numéro original si pas valide
    except:
        return numero_str  # En cas d'erreur, retourner le numéro original

def uniformiser_date(date_str):
    """
    Uniformise les formats de date
    """
    if pd.isna(date_str):
        return np.nan
    
    # Si c'est déjà un objet datetime
    if isinstance(date_str, (pd.Timestamp, datetime)):
        return date_str.strftime('%d/%m/%Y %H:%M:%S')
    
    date_str = str(date_str).strip()
    
    # Formats de date courants à essayer
    formats = [
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%m/%d/%Y',
        '%d.%m.%Y',
        '%Y/%m/%d'
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%d/%m/%Y %H:%M:%S')
        except:
            continue
    
    return date_str  # Retourner la valeur originale si aucun format ne marche

def standardiser_pays(pays):
    """
    Standardise les noms de pays
    """
    if pd.isna(pays):
        return np.nan
    
    pays_str = str(pays).strip().lower()
    
    # Dictionnaire de correspondance pour les pays courants
    correspondances_pays = {
        'france': 'France',
        'cameroun': 'Cameroun',
        'cameroon': 'Cameroun',
        'cote d\'ivoire': 'Côte d\'Ivoire',
        'ivory coast': 'Côte d\'Ivoire',
        'senegal': 'Sénégal',
        'burkina faso': 'Burkina Faso',
        'burkina': 'Burkina Faso',
        'mali': 'Mali',
        'niger': 'Niger',
        'tchad': 'Tchad',
        'chad': 'Tchad',
        'benin': 'Bénin',
        'togo': 'Togo',
        'ghana': 'Ghana',
        'nigeria': 'Nigeria',
        'maroc': 'Maroc',
        'morocco': 'Maroc',
        'algerie': 'Algérie',
        'algeria': 'Algérie',
        'tunisie': 'Tunisie',
        'tunisia': 'Tunisie'
    }
    
    for cle, valeur in correspondances_pays.items():
        if cle in pays_str:
            return valeur
    
    # Capitaliser la première lettre si pas trouvé
    return pays_str.title()

def analyser_fichier(chemin_fichier):
    """
    Analyse le fichier Excel et affiche des informations sur sa structure
    """
    print("📊 Analyse du fichier Excel...")
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(chemin_fichier)
        
        print(f"✅ Fichier lu avec succès!")
        print(f"📏 Dimensions: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        print(f"\n📋 Colonnes actuelles:")
        
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {repr(col)}")
        
        # Analyser les colonnes vides
        colonnes_vides = detecter_colonnes_vides(df)
        if colonnes_vides:
            print(f"\n🗑️ Colonnes vides détectées ({len(colonnes_vides)}):")
            for col in colonnes_vides:
                print(f"  - {repr(col)}")
        
        # Afficher un aperçu des données
        print(f"\n👀 Aperçu des premières lignes:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return None

def nettoyer_fichier(chemin_fichier, chemin_sortie=None):
    """
    Fonction principale de nettoyage du fichier
    """
    print("🧹 Début du nettoyage du fichier...")
    
    # Analyser le fichier
    df = analyser_fichier(chemin_fichier)
    if df is None:
        return None
    
    # 1. Renommer les colonnes
    print("\n📝 Nettoyage des noms de colonnes...")
    anciens_noms = df.columns.tolist()
    nouveaux_noms = [nettoyer_nom_colonne(col) for col in df.columns]
    
    # Gérer les doublons dans les noms de colonnes
    noms_uniques = []
    compteur = {}
    for nom in nouveaux_noms:
        if nom in compteur:
            compteur[nom] += 1
            nom_unique = f"{nom}_{compteur[nom]}"
        else:
            compteur[nom] = 0
            nom_unique = nom
        noms_uniques.append(nom_unique)
    
    df.columns = noms_uniques
    
    print("✅ Colonnes renommées:")
    for ancien, nouveau in zip(anciens_noms, noms_uniques):
        if ancien != nouveau:
            print(f"  '{ancien}' → '{nouveau}'")
    
    # 2. Supprimer les colonnes vides
    print(f"\n🗑️ Suppression des colonnes vides...")
    colonnes_vides = detecter_colonnes_vides(df)
    if colonnes_vides:
        # Mapper les anciens noms aux nouveaux noms
        colonnes_vides_nouvelles = []
        for i, ancien_nom in enumerate(anciens_noms):
            if ancien_nom in colonnes_vides:
                colonnes_vides_nouvelles.append(noms_uniques[i])
        
        df = df.drop(columns=colonnes_vides_nouvelles)
        print(f"✅ {len(colonnes_vides_nouvelles)} colonnes vides supprimées")
    else:
        print("✅ Aucune colonne vide trouvée")
    
    # 3. Traitement des dates
    print(f"\n📅 Uniformisation des dates...")
    colonnes_dates = [col for col in df.columns if any(mot in col.lower() for mot in ['date', 'horodateur', 'timestamp', 'naissance'])]
    
    for col in colonnes_dates:
        print(f"  Traitement de la colonne: {col}")
        df[col] = df[col].apply(uniformiser_date)
    
    if colonnes_dates:
        print(f"✅ {len(colonnes_dates)} colonnes de dates traitées")
    else:
        print("✅ Aucune colonne de date détectée")
    
    # 4. Nettoyage des numéros de téléphone
    print(f"\n📱 Nettoyage des numéros de téléphone...")
    colonnes_tel = [col for col in df.columns if any(mot in col.lower() for mot in ['telephone', 'phone', 'tel', 'numero', 'contact'])]
    
    for col in colonnes_tel:
        print(f"  Traitement de la colonne: {col}")
        df[col] = df[col].apply(nettoyer_telephone)
    
    if colonnes_tel:
        print(f"✅ {len(colonnes_tel)} colonnes de téléphone traitées")
    else:
        print("✅ Aucune colonne de téléphone détectée")
    
    # 5. Harmonisation des pays
    print(f"\n🌍 Harmonisation des noms de pays...")
    colonnes_pays = [col for col in df.columns if any(mot in col.lower() for mot in ['pays', 'country', 'nation', 'origine'])]
    
    for col in colonnes_pays:
        print(f"  Traitement de la colonne: {col}")
        df[col] = df[col].apply(standardiser_pays)
    
    if colonnes_pays:
        print(f"✅ {len(colonnes_pays)} colonnes de pays traitées")
    else:
        print("✅ Aucune colonne de pays détectée")
    
    # 6. Standardisation des packs (si applicable)
    print(f"\n📦 Standardisation des réponses de packs...")
    colonnes_pack = [col for col in df.columns if any(mot in col.lower() for mot in ['pack', 'package', 'formule', 'option'])]
    
    for col in colonnes_pack:
        print(f"  Traitement de la colonne: {col}")
        # Nettoyer et standardiser les valeurs
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace('Nan', np.nan)
    
    if colonnes_pack:
        print(f"✅ {len(colonnes_pack)} colonnes de packs traitées")
    else:
        print("✅ Aucune colonne de pack détectée")
    
    # Sauvegarder le fichier nettoyé
    if chemin_sortie is None:
        chemin_sortie = chemin_fichier.replace('.xlsx', '_nettoye.xlsx')
    
    try:
        df.to_excel(chemin_sortie, index=False)
        print(f"\n💾 Fichier nettoyé sauvegardé: {chemin_sortie}")
        print(f"📏 Dimensions finales: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        # Afficher un résumé
        print(f"\n📋 Colonnes finales:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return df

if __name__ == "__main__":
    # Chemin vers le fichier Excel
    chemin_fichier = "Formulaire sans titre (réponses).xlsx"
    
    # Nettoyer le fichier
    df_nettoye = nettoyer_fichier(chemin_fichier)
    
    if df_nettoye is not None:
        print(f"\n🎉 Nettoyage terminé avec succès!")
    else:
        print(f"\n❌ Échec du nettoyage")
