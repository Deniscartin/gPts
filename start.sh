#!/bin/bash

# Script di avvio rapido per Gasolio Docker
echo "🚀 Avvio Gasolio Docker..."

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    print_error "Docker non è installato. Installa Docker prima di continuare."
    exit 1
fi

# Controlla se Docker Compose è installato
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose non è installato. Installa Docker Compose prima di continuare."
    exit 1
fi

# Controlla se serviceAccount.json esiste
if [ ! -f "serviceAccount.json" ]; then
    print_warning "File serviceAccount.json non trovato!"
    print_warning "L'applicazione userà dati mock per il testing."
    print_warning "Per la produzione, aggiungi il file serviceAccount.json di Firebase."
fi

# Crea directory logs se non esiste
mkdir -p logs

print_status "Fermando eventuali container in esecuzione..."
docker-compose down

print_status "Building dell'immagine Docker..."
if docker-compose build; then
    print_success "Build completata con successo!"
else
    print_error "Errore durante il build!"
    exit 1
fi

print_status "Avvio dell'applicazione..."
if docker-compose up -d; then
    print_success "Applicazione avviata con successo!"
else
    print_error "Errore durante l'avvio!"
    exit 1
fi

# Attendi qualche secondo per l'avvio
print_status "Attendendo l'avvio del container..."
sleep 10

# Controlla stato del container
if docker-compose ps | grep -q "Up"; then
    print_success "Container in esecuzione!"
    
    # Ottieni l'IP del server
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "🎉 Gasolio è ora in esecuzione!"
    echo ""
    echo "📱 Accedi all'applicazione:"
    echo "   • Locale: http://localhost:5001"
    echo "   • Rete:   http://${SERVER_IP}:5001"
    echo ""
    echo "📊 Comandi utili:"
    echo "   • Logs in tempo reale: docker-compose logs -f"
    echo "   • Stato container:     docker-compose ps"
    echo "   • Riavvia:            docker-compose restart"
    echo "   • Ferma:              docker-compose down"
    echo ""
    
    # Test di connettività
    print_status "Test di connettività..."
    if curl -f http://localhost:5001/ > /dev/null 2>&1; then
        print_success "Server risponde correttamente!"
    else
        print_warning "Server non risponde al test. Controlla i logs con: docker-compose logs"
    fi
    
else
    print_error "Container non in esecuzione! Controlla i logs:"
    docker-compose logs
    exit 1
fi 