#!/bin/bash

# Script de gerenciamento Docker para Arca Bot

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se .env existe
check_env() {
    if [ ! -f ".env" ]; then
        error ".env file not found!"
        warning "Copy .env.example to .env and configure it:"
        echo "cp .env.example .env"
        exit 1
    fi
    
    # Verificar BOT_TOKEN
    if ! grep -q "^BOT_TOKEN=..*" .env; then
        error "BOT_TOKEN not configured in .env"
        exit 1
    fi
}

# Build da imagem
build() {
    log "Building Docker image..."
    docker build -t arca-bot:latest .
    success "Docker image built successfully!"
}

# Build para produção
build_prod() {
    log "Building production Docker image..."
    docker build -f Dockerfile.production -t arca-bot:production .
    success "Production Docker image built successfully!"
}

# Executar em desenvolvimento
dev() {
    check_env
    log "Starting Arca Bot in development mode..."
    docker-compose up --build
}

# Executar em background
start() {
    check_env
    log "Starting Arca Bot in background..."
    docker-compose up -d --build
    success "Arca Bot started in background!"
    log "Use 'docker-compose logs -f' to see logs"
}

# Parar containers
stop() {
    log "Stopping Arca Bot..."
    docker-compose down
    success "Arca Bot stopped!"
}

# Restart
restart() {
    log "Restarting Arca Bot..."
    docker-compose down
    docker-compose up -d --build
    success "Arca Bot restarted!"
}

# Ver logs
logs() {
    docker-compose logs -f
}

# Limpar containers e imagens
clean() {
    log "Cleaning up Docker resources..."
    docker-compose down -v
    docker image prune -f
    docker system prune -f
    success "Docker cleanup completed!"
}

# Status
status() {
    log "Docker containers status:"
    docker-compose ps
    
    echo ""
    log "Recent logs:"
    docker-compose logs --tail=20
}

# Help
show_help() {
    echo "Arca Bot Docker Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build      - Build Docker image"
    echo "  build-prod - Build production Docker image"
    echo "  dev        - Run in development mode (foreground)"
    echo "  start      - Start in background"
    echo "  stop       - Stop containers"
    echo "  restart    - Restart containers"
    echo "  logs       - Show logs"
    echo "  status     - Show container status and recent logs"
    echo "  clean      - Clean up Docker resources"
    echo "  help       - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start bot in background"
    echo "  $0 logs     # Follow logs"
    echo "  $0 restart  # Restart bot"
}

# Main
case "$1" in
    build)
        build
        ;;
    build-prod)
        build_prod
        ;;
    dev)
        dev
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
