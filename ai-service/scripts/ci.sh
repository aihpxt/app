#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing dependencies..."

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    pip install pytest pytest-cov pytest-asyncio black flake8 bandit safety

    log_info "Dependencies installed"
}

run_tests() {
    log_info "Running tests..."

    pytest tests/ -v --cov=. --cov-report=term-missing

    log_info "Tests completed"
}

run_lint() {
    log_info "Running linters..."

    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    black --check .

    log_info "Linting completed"
}

build_docker() {
    log_info "Building Docker image..."

    docker build -t ai-service:latest .

    log_info "Docker image built successfully"
}

deploy() {
    log_info "Deploying to server..."

    if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
        log_error "DEPLOY_HOST and DEPLOY_USER must be set"
        exit 1
    fi

    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "cd /opt/ai-service && git pull && docker-compose up -d --build"

    log_info "Deployment completed"
}

case "$1" in
    install)
        install_dependencies
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    build)
        build_docker
        ;;
    deploy)
        deploy
        ;;
    ci)
        install_dependencies
        run_lint
        run_tests
        ;;
    *)
        echo "Usage: $0 {install|test|lint|build|deploy|ci}"
        exit 1
        ;;
esac
