#!/bin/bash
# Script de démarrage - Projet CTAMS
# Usage: ./dev.sh [commande]

set -e

# Path
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${PROJECT_ROOT}/venv"
SRC="${PROJECT_ROOT}/src"
PYTHON="${VENV}/Scripts/python.exe"
MANAGE="${SRC}/manage.py"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  CTAMS - Outil Gestion Atelier Auto${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_venv() {
    if [ ! -d "$VENV" ]; then
        print_error "Venv not found!"
        echo "Creating venv..."
        python -m venv "$VENV"
        print_success "Venv créé"
    fi
}

install_deps() {
    print_info "Installation des dépendances..."
    "$PYTHON" -m pip install -q --upgrade pip setuptools wheel
    "$PYTHON" -m pip install -q -r "$PROJECT_ROOT/requirements.txt"
    print_success "Dépendances installées"
}

makemigrations() {
    print_info "Génération des migrations..."
    cd "$SRC"
    "$PYTHON" manage.py makemigrations "$@"
    print_success "Migrations générées"
}

migrate() {
    print_info "Application des migrations..."
    cd "$SRC"
    "$PYTHON" manage.py migrate "$@"
    print_success "Migrations appliquées"
}

run_server() {
    print_info "Démarrage du serveur de développement..."
    cd "$SRC"
    "$PYTHON" manage.py runserver 0.0.0.0:8000
}

create_admin() {
    print_info "Création d'un utilisateur admin..."
    cd "$SRC"
    "$PYTHON" manage.py createsuperuser
}

run_tests() {
    print_info "Exécution des tests..."
    cd "$SRC"
    "$PYTHON" -m pytest "$@"
}

show_help() {
    cat << EOF
${BLUE}Usage: ./dev.sh [commande]${NC}

${GREEN}Commandes disponibles:${NC}
  setup           Initialise l'environnement (venv + dépendances)
  migrate         Applique les migrations
  makemigrations  Génère les migrations
  runserver       Démarre le serveur de développement
  admin           Crée un utilisateur admin
  check           Vérife la configuration Django
  shell           Lance le shell Django
  test            Exécute les tests
  help            Affiche cette aide

${YELLOW}Exemples:${NC}
  ./dev.sh setup
  ./dev.sh migrate
  ./dev.sh runserver
  ./dev.sh makemigrations customers
  ./dev.sh test --verbose
EOF
}

# Main
print_header
check_venv

case "${1:-help}" in
    setup)
        install_deps
        migrate
        print_success "Environnement prêt!"
        echo -e "${YELLOW}Prochaines étapes:${NC}"
        echo "  1. Créer admin: ./dev.sh admin"
        echo "  2. Démarrer serveur: ./dev.sh runserver"
        ;;
    migrate)
        cd "$SRC"
        "$PYTHON" manage.py migrate "${@:2}"
        print_success "Migrations appliquées"
        ;;
    makemigrations)
        makemigrations "${@:2}"
        ;;
    runserver)
        run_server
        ;;
    admin)
        create_admin
        ;;
    check)
        print_info "Vérification Django..."
        cd "$SRC"
        "$PYTHON" manage.py check
        print_success "Configuration OK"
        ;;
    shell)
        print_info "Lancement du shell Django..."
        cd "$SRC"
        "$PYTHON" manage.py shell
        ;;
    test)
        run_tests "${@:2}"
        ;;
    install)
        install_deps
        print_success "Dépendances installées"
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Commande inconnue: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
