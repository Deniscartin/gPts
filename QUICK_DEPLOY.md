# Deploy Rapido Gasolio - Comandi Essenziali

## 🚀 Setup Iniziale VM

```bash
# 1. Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# 2. Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 3. Installa Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Verifica installazione
docker --version
docker-compose --version
```

## 📁 Trasferimento Files

```bash
# Crea directory
mkdir -p ~/gasolio-app
cd ~/gasolio-app

# Trasferisci files (scegli un metodo):
# Metodo 1: SCP
scp -r /local/path/* username@vm-ip:~/gasolio-app/

# Metodo 2: Git
git clone https://github.com/username/gasolio-app.git .

# Metodo 3: Upload manuale via SFTP
```

## 🔧 Configurazione

```bash
# 1. Aggiungi file Firebase (IMPORTANTE!)
nano serviceAccount.json
# Incolla contenuto JSON di Firebase

# 2. Crea directory logs
mkdir -p logs

# 3. Verifica files necessari
ls -la
# Devi vedere: Dockerfile, docker-compose.yml, data_server.py, platts/, serviceAccount.json
```

## ⚡ Avvio Rapido

```bash
# Metodo 1: Script automatico (CONSIGLIATO)
./start.sh

# Metodo 2: Comandi manuali
docker-compose build
docker-compose up -d
```

## 🌐 Configurazione Firewall

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 5001

# Verifica
sudo ufw status
```

## 📊 Comandi di Gestione

```bash
# Stato applicazione
docker-compose ps

# Logs in tempo reale
docker-compose logs -f gasolio-app

# Riavvia
docker-compose restart

# Ferma
docker-compose down

# Update completo
docker-compose down && docker-compose build && docker-compose up -d

# Accesso shell container
docker-compose exec gasolio-app bash

# Pulizia Docker
docker system prune -f
```

## 🔍 Test e Verifica

```bash
# Test locale
curl http://localhost:5001/

# Test da browser
# Vai a: http://VM-IP:5001

# Controlla health
docker-compose exec gasolio-app curl -f http://localhost:5001/
```

## 🚨 Troubleshooting Rapido

```bash
# Container non parte
docker-compose logs gasolio-app

# Problemi memoria
free -h
df -h

# Riavvio completo
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

# Verifica Chrome nel container
docker-compose exec gasolio-app google-chrome --version

# Verifica Firebase
docker-compose exec gasolio-app ls -la serviceAccount.json
```

## 📱 Accesso Applicazione

Dopo il deploy, l'applicazione sarà disponibile su:
- **Locale**: `http://localhost:5001`
- **Rete**: `http://VM-IP:5001`

### Prima volta:
1. Vai all'URL
2. Clicca "Registrati"
3. Crea account con email/password
4. Fai login
5. Verifica caricamento dati

## 🔒 SSL/HTTPS (Opzionale)

```bash
# Installa Nginx
sudo apt install nginx

# Configura reverse proxy
sudo nano /etc/nginx/sites-available/gasolio

# Contenuto file:
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Abilita sito
sudo ln -s /etc/nginx/sites-available/gasolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 💾 Backup

```bash
# Backup rapido
tar -czf gasolio-backup-$(date +%Y%m%d).tar.gz gasolio-app/

# Backup automatico (crontab)
crontab -e
# Aggiungi: 0 2 * * * tar -czf /home/$USER/backups/gasolio-$(date +\%Y\%m\%d).tar.gz -C /home/$USER gasolio-app
```

## 📋 Checklist Deploy

- [ ] VM con Ubuntu 20.04+, 2 vCPU, 4GB RAM
- [ ] Docker e Docker Compose installati
- [ ] Files applicazione trasferiti
- [ ] File `serviceAccount.json` presente
- [ ] Firewall configurato (porta 5001)
- [ ] Applicazione buildada: `docker-compose build`
- [ ] Applicazione avviata: `docker-compose up -d`
- [ ] Test accesso: `curl http://localhost:5001/`
- [ ] Test browser: `http://VM-IP:5001`
- [ ] Autenticazione testata
- [ ] Dati caricati correttamente

## ⚡ Comandi One-Liner

```bash
# Setup completo Docker
curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker $USER

# Deploy rapido
git clone REPO && cd gasolio-app && ./start.sh

# Monitoraggio
watch 'docker-compose ps && echo "---" && docker-compose logs --tail=5 gasolio-app'

# Restart completo
docker-compose down && docker-compose build && docker-compose up -d && docker-compose logs -f
```

🎉 **L'applicazione sarà accessibile su `http://VM-IP:5001` con autenticazione Firebase!** 