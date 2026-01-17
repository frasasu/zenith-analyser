#!/usr/bin/env python3
"""
Script pour pousser sur GitHub avec gestion des conflits
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, show_error=True):
    """Exécute une commande shell avec meilleure gestion d'erreurs."""
    print(f"▶️  Commande: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True
        )
        if result.returncode != 0 and show_error:
            if result.stderr:
                print(
                    f"❌ Erreur: {result.stderr[:200]}"
                )  # Afficher seulement les 200 premiers caractères
            else:
                print(f"❌ Code erreur: {result.returncode}")
            return False, result.stderr
        if result.stdout:
            print(
                f"✅ Sortie: {result.stdout[:100]}"
                if len(result.stdout) > 100
                else f"✅ Sortie: {result.stdout}"
            )
        return True, result.stdout
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)


def check_github_repo_exists():
    """Vérifie si le repository GitHub existe déjà."""
    print("\n🔍 Vérification du repository GitHub...")

    # Méthode 1: Vérifier avec curl
    cmd = 'curl -s -o /dev/null -w "%{http_code}" https://github.com/frasasu/zenith-analyser'
    success, output = run_command(cmd, show_error=False)

    if success and output.strip() == "200":
        print("✅ Repository GitHub existe déjà")
        return True

    # Méthode 2: Vérifier avec git ls-remote
    cmd = "git ls-remote https://github.com/frasasu/zenith-analyser.git 2>&1"
    success, output = run_command(cmd, show_error=False)

    if success and "fatal" not in output:
        print("✅ Repository GitHub existe déjà (git ls-remote)")
        return True

    print("❌ Repository GitHub n'existe pas ou est inaccessible")
    return False


def initialize_git_force():
    """Initialise Git même si .git existe déjà."""
    print("\n📁 Initialisation Git...")

    # Supprimer .git s'il existe et a des problèmes
    if Path(".git").exists():
        print("⚠️  .git existe déjà")

        # Vérifier l'état
        run_command("git status", show_error=False)

        # Demander confirmation
        response = input("Voulez-vous réinitialiser Git? (o/n): ")
        if response.lower() in ["o", "oui", "y", "yes"]:
            # Sauvegarder les infos remote
            run_command("git remote -v", show_error=False)

            # Supprimer .git
            if os.name == "nt":  # Windows
                run_command("rmdir /s /q .git")
            else:  # Linux/Mac
                run_command("rm -rf .git")

            # Réinitialiser
            run_command("git init")
        else:
            print("Utilisation du .git existant")
    else:
        run_command("git init")

    # Configurer Git
    run_command('git config user.name "Francois TUMUSAVYEYESU"')
    run_command('git config user.email "frasasudev@gmail.com"')

    return True


def add_and_commit():
    """Ajoute et commit les fichiers."""
    print("\n💾 Ajout des fichiers...")

    # Ajouter tous les fichiers
    success, output = run_command("git add .")
    if not success:
        print("⚠️  Problème avec git add, essayons fichier par fichier")

        # Ajouter les fichiers importants d'abord
        important_files = [
            "src/zenith_analyser/__init__.py",
            "src/zenith_analyser/lexer.py",
            "src/zenith_analyser/parser.py",
            "README.md",
            "LICENSE",
            "setup.py",
        ]

        for file in important_files:
            if Path(file).exists():
                run_command(f'git add "{file}"')

    print("\n📝 Commit...")
    commit_message = """Initial commit: Zenith Analyser v1.0.0

A comprehensive library for analyzing structured temporal laws
- Zenith language lexer and parser
- Temporal law analysis with chronocoherence/chronodispersal
- Hierarchical target structure analysis
- AST unparser and validation system
- Apache 2.0 license"""

    run_command(f'git commit -m "{commit_message}"')

    return True


def push_to_github_force():
    """Pousse sur GitHub avec force si nécessaire."""
    print("\n🚀 Poussée vers GitHub...")

    repo_url = "https://github.com/frasasu/zenith-analyser.git"

    # 1. Vérifier/set remote
    success, output = run_command("git remote -v", show_error=False)
    if "origin" not in output:
        run_command(f"git remote add origin {repo_url}")
    else:
        # Mettre à jour l'URL si nécessaire
        run_command(f"git remote set-url origin {repo_url}")

    # 2. Renommer la branche
    run_command("git branch -M main")

    # 3. Essayer push normal d'abord
    print("\n📤 Tentative de push normal...")
    success, error = run_command("git push -u origin main", show_error=False)

    if not success:
        if "failed to push some refs" in error or "non-fast-forward" in error:
            print("\n⚠️  Conflit détecté, utilisation de --force")

            # Option 1: Force push (écrase tout sur GitHub)
            response = input(
                "Voulez-vous forcer le push? (écrasera tout sur GitHub) (o/n): "
            )
            if response.lower() in ["o", "oui", "y", "yes"]:
                run_command("git push -u origin main --force")
            else:
                # Option 2: Pull d'abord, puis merge
                print("\n🔄 Pull d'abord, puis merge...")
                run_command("git pull origin main --allow-unrelated-histories")
                run_command("git push -u origin main")
        else:
            print(f"\n❌ Erreur inattendue: {error}")
            return False

    return True


def create_github_repo_instructions():
    """Instructions pour créer le repository GitHub."""
    print("\n" + "=" * 70)
    print("🌐 CRÉATION DU REPOSITORY GITHUB")
    print("=" * 70)
    print("\nSI LE REPOSITORY N'EXISTE PAS:")
    print("1. Allez sur: https://github.com/new")
    print("2. Remplissez:")
    print("   - Owner: frasasu")
    print("   - Repository name: zenith-analyser")
    print("   - Description: A library for analyzing structured temporal laws")
    print("   - Public: ✓")
    print("   - Initialize with README: ✗ (décochez!)")
    print("   - Add .gitignore: Python")
    print("   - License: Apache License 2.0")
    print("3. Cliquez sur 'Create repository'")
    print("\nSI LE REPOSITORY EXISTE DÉJÀ:")
    print("Continuez avec les étapes ci-dessous")
    print("=" * 70)

    input("\nAppuyez sur Entrée pour continuer...")
    return True


def main():
    """Fonction principale."""
    print("🚀 PUSH GITHUB - ZENITH ANALYSER")
    print("=" * 70)

    # Vérifier Git
    print("\n🔧 Vérification de Git...")
    success, _ = run_command("git --version")
    if not success:
        print("❌ Git n'est pas installé")
        print("Téléchargez: https://git-scm.com/downloads")
        return

    # Vérifier la structure
    print("\n📁 Vérification de la structure...")
    required_files = [
        "src/zenith_analyser/__init__.py",
        "README.md",
        "LICENSE",
        "setup.py",
    ]

    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (MANQUANT)")
            missing.append(file)

    if missing:
        print(f"\n❌ Fichiers manquants: {len(missing)}")
        print("Créez ces fichiers d'abord")
        return

    # Instructions pour GitHub
    create_github_repo_instructions()

    # Vérifier si le repo existe
    repo_exists = check_github_repo_exists()

    if not repo_exists:
        print("\n⚠️  Le repository n'existe pas encore sur GitHub")
        print("Créez-le d'abord sur https://github.com/new")
        print("Puis relancez ce script")
        return

    # Initialiser Git
    initialize_git_force()

    # Ajouter et commit
    add_and_commit()

    # Pousser sur GitHub
    if push_to_github_force():
        print("\n" + "=" * 70)
        print("🎉 SUCCÈS!")
        print("=" * 70)
        print("\n✅ Projet sur GitHub!")
        print("📂 https://github.com/frasasu/zenith-analyser")

        # Créer un tag
        print("\n🏷️  Création du tag v1.0.0...")
        run_command("git tag v1.0.0")
        run_command("git push --tags")

        print("\n📋 Prochaines étapes:")
        print("1. Vérifiez: https://github.com/frasasu/zenith-analyser")
        print("2. Vérifiez Actions: https://github.com/frasasu/zenith-analyser/actions")
        print("3. Attendez que le CI passe (peut prendre 2-3 minutes)")
        print("4. Ajoutez un badge dans README.md si le CI passe")

    print("\n" + "=" * 70)
    print("🆘 SI VOUS AVEZ ENCORE DES ERREURS:")
    print("=" * 70)
    print(
        """
Option 1: Créez un NOUVEAU repository:
   git remote rename origin old-origin
   Créez un nouveau repo sur GitHub avec un nom différent
   git remote add origin https://github.com/frasasu/zenith-analyser-NEW.git
   git push -u origin main

Option 2: Force push propre:
   git fetch origin
   git reset --hard origin/main
   git push -u origin main --force

Option 3: Commencez depuis zéro:
   rm -rf .git
   git init
   [recréez le repo sur GitHub vide]
   Suivez les instructions de GitHub
"""
    )


if __name__ == "__main__":
    main()
