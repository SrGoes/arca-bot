# Script de gerenciamento Docker para Arca Bot (PowerShell)

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Cores para output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Log($Message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "${Blue}[$timestamp]${Reset} $Message"
}

function Write-Error($Message) {
    Write-Host "${Red}[ERROR]${Reset} $Message"
}

function Write-Success($Message) {
    Write-Host "${Green}[SUCCESS]${Reset} $Message"
}

function Write-Warning($Message) {
    Write-Host "${Yellow}[WARNING]${Reset} $Message"
}

# Verificar se .env existe
function Test-Environment {
    if (-not (Test-Path ".env")) {
        Write-Error ".env file not found!"
        Write-Warning "Copy .env.example to .env and configure it:"
        Write-Host "Copy-Item .env.example .env"
        exit 1
    }
    
    # Verificar BOT_TOKEN
    $envContent = Get-Content ".env" -Raw
    if ($envContent -notmatch "BOT_TOKEN=.+") {
        Write-Error "BOT_TOKEN not configured in .env"
        exit 1
    }
}

# Build da imagem
function Build-Image {
    Write-Log "Building Docker image..."
    docker build -t arca-bot:latest .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully!"
    } else {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

# Build para produção
function Build-ProductionImage {
    Write-Log "Building production Docker image..."
    docker build -f Dockerfile.production -t arca-bot:production .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production Docker image built successfully!"
    } else {
        Write-Error "Failed to build production Docker image"
        exit 1
    }
}

# Executar em desenvolvimento
function Start-Development {
    Test-Environment
    Write-Log "Starting Arca Bot in development mode..."
    docker-compose up --build
}

# Executar em background
function Start-Background {
    Test-Environment
    Write-Log "Starting Arca Bot in background..."
    docker-compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Arca Bot started in background!"
        Write-Log "Use 'docker-compose logs -f' to see logs"
    } else {
        Write-Error "Failed to start Arca Bot"
        exit 1
    }
}

# Parar containers
function Stop-Containers {
    Write-Log "Stopping Arca Bot..."
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Arca Bot stopped!"
    }
}

# Restart
function Restart-Bot {
    Write-Log "Restarting Arca Bot..."
    docker-compose down
    docker-compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Arca Bot restarted!"
    } else {
        Write-Error "Failed to restart Arca Bot"
        exit 1
    }
}

# Ver logs
function Show-Logs {
    docker-compose logs -f
}

# Limpar containers e imagens
function Clear-Docker {
    Write-Log "Cleaning up Docker resources..."
    docker-compose down -v
    docker image prune -f
    docker system prune -f
    Write-Success "Docker cleanup completed!"
}

# Status
function Show-Status {
    Write-Log "Docker containers status:"
    docker-compose ps
    
    Write-Host ""
    Write-Log "Recent logs:"
    docker-compose logs --tail=20
}

# Help
function Show-Help {
    Write-Host "Arca Bot Docker Management Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\docker-manage.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build      - Build Docker image"
    Write-Host "  build-prod - Build production Docker image"
    Write-Host "  dev        - Run in development mode (foreground)"
    Write-Host "  start      - Start in background"
    Write-Host "  stop       - Stop containers"
    Write-Host "  restart    - Restart containers"
    Write-Host "  logs       - Show logs"
    Write-Host "  status     - Show container status and recent logs"
    Write-Host "  clean      - Clean up Docker resources"
    Write-Host "  help       - Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\docker-manage.ps1 start    # Start bot in background"
    Write-Host "  .\docker-manage.ps1 logs     # Follow logs"
    Write-Host "  .\docker-manage.ps1 restart  # Restart bot"
}

# Main
switch ($Command.ToLower()) {
    "build" { Build-Image }
    "build-prod" { Build-ProductionImage }
    "dev" { Start-Development }
    "start" { Start-Background }
    "stop" { Stop-Containers }
    "restart" { Restart-Bot }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "clean" { Clear-Docker }
    "help" { Show-Help }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
