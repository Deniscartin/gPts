# Guida Deploy Gasolio su VM con Docker

Questa guida ti accompagnerà passo-passo nel deploy dell'applicazione Gasolio su una VM utilizzando Docker.

## Prerequisiti VM

### Specifiche minime consigliate:
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Storage**: 20 GB
- **OS**: Ubuntu 20.04 LTS o superiore

## Passo 1: Preparazione VM

### 1.1 Aggiorna il sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Installa Docker
```bash
# Rimuovi eventuali installazioni precedenti
sudo apt-get remove docker docker-engine docker.io containerd runc

# Installa dipendenze
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Aggiungi chiave GPG Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Aggiungi repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installa Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verifica installazione
sudo docker run hello-world
```

### 1.3 Installa Docker Compose (se non incluso)
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifica installazione
docker-compose --version
```

### 1.4 Configura utente Docker (opzionale)
```bash
# Aggiungi utente al gruppo docker per evitare sudo
sudo usermod -aG docker $USER

# Riavvia la sessione o esegui:
newgrp docker
```

## Passo 2: Trasferimento Files

### 2.1 Crea directory progetto
```bash
mkdir -p ~/gasolio-app
cd ~/gasolio-app
```

### 2.2 Trasferisci i file del progetto
Puoi usare diversi metodi:

#### Metodo A: SCP (da locale a VM)
```bash
# Dal tuo computer locale
scp -r /path/to/platts/* username@vm-ip:~/gasolio-app/
```

#### Metodo B: Git Clone
```bash
# Se hai un repository Git
git clone https://github.com/tuousername/gasolio-app.git
cd gasolio-app
```

#### Metodo C: Upload manuale
Carica i file tramite SFTP o interfaccia web del provider VM.

### 2.3 Verifica struttura files
```bash
ls -la ~/gasolio-app/
```

Dovresti vedere:
```
data_server.py
requirements.txt
platts/platts_viewer.html
Dockerfile
docker-compose.yml
serviceAccount.json
FIREBASE_AUTH_SETUP.md
```

## Passo 3: Configurazione Firebase

### 3.1 Carica serviceAccount.json
Assicurati che il file `serviceAccount.json` sia presente nella directory del progetto:

```bash
# Verifica presenza
ls -la serviceAccount.json

# Se manca, crealo o caricalo
nano serviceAccount.json
# Incolla il contenuto del file JSON di Firebase
```

### 3.2 Crea directory logs
```bash
mkdir -p logs
```

## Passo 4: Build e Deploy

### 4.1 Build dell'immagine Docker
```bash
cd ~/gasolio-app
docker-compose build
```

### 4.2 Avvia l'applicazione
```bash
docker-compose up -d
```

### 4.3 Verifica stato
```bash
# Controlla container in esecuzione
docker-compose ps

# Controlla logs
docker-compose logs -f gasolio-app

# Verifica health check
docker-compose exec gasolio-app curl -f http://localhost:5001/
```

## Passo 5: Configurazione Firewall

### 5.1 Configura UFW (Ubuntu Firewall)
```bash
# Abilita UFW
sudo ufw enable

# Permetti SSH
sudo ufw allow ssh

# Permetti porta applicazione
sudo ufw allow 5001

# Verifica regole
sudo ufw status
```

### 5.2 Configura Security Groups (Cloud Provider)
Se usi AWS, Azure, GCP, ecc., configura i Security Groups per permettere:
- Porta 22 (SSH) dal tuo IP
- Porta 5001 (applicazione) da internet o IPs specifici

## Passo 6: Test dell'Applicazione

### 6.1 Test locale sulla VM
```bash
curl http://localhost:5001/
```

### 6.2 Test da browser esterno
Apri browser e vai a: `http://VM-IP:5001`

### 6.3 Test autenticazione
1. Registra un nuovo utente
2. Fai login
3. Verifica caricamento dati

## Passo 7: Monitoraggio e Manutenzione

### 7.1 Comandi utili Docker
```bash
# Visualizza logs in tempo reale
docker-compose logs -f

# Riavvia applicazione
docker-compose restart

# Ferma applicazione
docker-compose down

# Aggiorna e riavvia
docker-compose down
docker-compose build
docker-compose up -d

# Pulisci risorse Docker
docker system prune -f
```

### 7.2 Backup automatico
Crea script per backup:

```bash
# Crea script backup
nano ~/backup-gasolio.sh
```

Contenuto script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR

# Backup files applicazione
tar -czf $BACKUP_DIR/gasolio-app-$DATE.tar.gz -C /home/$USER gasolio-app

# Mantieni solo ultimi 7 backup
find $BACKUP_DIR -name "gasolio-app-*.tar.gz" -mtime +7 -delete

echo "Backup completato: gasolio-app-$DATE.tar.gz"
```

```bash
# Rendi eseguibile
chmod +x ~/backup-gasolio.sh

# Aggiungi a crontab per backup automatico
crontab -e

# Aggiungi riga per backup giornaliero alle 2:00
0 2 * * * /home/username/backup-gasolio.sh
```

## Passo 8: SSL/HTTPS (Opzionale ma Consigliato)

### 8.1 Installa Nginx
```bash
sudo apt install nginx
```

### 8.2 Configura reverse proxy
```bash
sudo nano /etc/nginx/sites-available/gasolio
```

Contenuto:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Abilita sito
sudo ln -s /etc/nginx/sites-available/gasolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8.3 Installa SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

### Problema: Container non si avvia
```bash
# Controlla logs dettagliati
docker-compose logs gasolio-app

# Controlla risorse sistema
free -h
df -h
```

### Problema: Chrome/Selenium errori
```bash
# Verifica installazione Chrome nel container
docker-compose exec gasolio-app google-chrome --version

# Riavvia con più memoria
docker-compose down
# Modifica docker-compose.yml aggiungendo:
# deploy:
#   resources:
#     limits:
#       memory: 2G
docker-compose up -d
```

### Problema: Firebase errori
```bash
# Verifica file serviceAccount.json
docker-compose exec gasolio-app cat serviceAccount.json

# Controlla permessi
docker-compose exec gasolio-app ls -la serviceAccount.json
```

## Comandi Rapidi di Gestione

```bash
# Stato applicazione
docker-compose ps

# Logs in tempo reale
docker-compose logs -f

# Riavvio rapido
docker-compose restart

# Update completo
docker-compose down && docker-compose build && docker-compose up -d

# Accesso shell container
docker-compose exec gasolio-app bash

# Backup rapido
tar -czf gasolio-backup-$(date +%Y%m%d).tar.gz gasolio-app/
```

L'applicazione sarà ora accessibile da `http://VM-IP:5001` e completamente containerizzata con Docker! 