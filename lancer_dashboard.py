#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement du dashboard Streamlit
"""

import subprocess
import sys
import os

def lancer_dashboard():
    """
    Lance l'application Streamlit
    """
    print("🚀 Lancement du Dashboard d'Analyse du Formulaire...")
    print("📊 Interface web disponible dans votre navigateur")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*60)
    
    try:
        # Changer vers le répertoire du script
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Lancer Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard_streamlit.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Assurez-vous que Streamlit est installé: pip install streamlit")

if __name__ == "__main__":
    lancer_dashboard()
