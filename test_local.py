#!/usr/bin/env python3
"""
Test local rapide avant de pousser sur GitHub
"""

import subprocess
import sys
from pathlib import Path


def run_test(command, description):
    print(f"\n🔧 {description}")
    print(f"   Commande: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"   ✅ Succès")
        if result.stdout.strip():
            print(f"   Sortie: {result.stdout[:200]}...")
    else:
        print(f"   ❌ Échec")
        print(f"   Erreur: {result.stderr[:200]}")

    return result.returncode == 0


def main():
    print("🧪 TESTS LOCAUX - ZENITH ANALYSER")
    print("=" * 60)

    tests = [
        # Vérifier Python
        ("python --version", "Vérifier Python"),
        # Installer en mode développement
        ("pip install -e .", "Installer en mode développement"),
        # Exécuter les tests
        ("python -m pytest tests/ -v", "Exécuter les tests"),
        # Vérifier la syntaxe
        (
            "python -c \"from zenith_analyser import ZenithAnalyser; print('Import OK')\"",
            "Vérifier l'import",
        ),
        # Tester un exemple
        (
            'python -c "import json; from zenith_analyser import ZenithAnalyser; '
            "code = 'law test: start_date:2024-01-01 at 10:00 period:1.0 Event: A:\\\"Test\\\" GROUP:(A 1.0^0) end_law'; "
            "a = ZenithAnalyser(code); print('ZenithAnalyser fonctionne')\"",
            "Tester ZenithAnalyser",
        ),
        # Vérifier la structure du package
        (
            'python -c "import zenith_analyser; '
            "print(f'Version: {zenith_analyser.__version__}'); "
            "print(f'Auteur: {zenith_analyser.__author__}')\"",
            "Vérifier les métadonnées",
        ),
    ]

    successes = 0
    for command, description in tests:
        if run_test(command, description):
            successes += 1

    print(f"\n" + "=" * 60)
    print(f"📊 RÉSULTAT: {successes}/{len(tests)} tests réussis")

    if successes == len(tests):
        print("🎉 Tous les tests ont réussi! Prêt pour GitHub.")
    else:
        print("⚠️  Certains tests ont échoué. Corrigez avant de pousser sur GitHub.")


if __name__ == "__main__":
    main()
