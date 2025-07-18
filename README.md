# ⚡ Energy Futures Tracker

**Applicazione per il monitoraggio dei prezzi forward dei prodotti energetici**

Recupera e visualizza i prezzi di futures per: ULSD 10ppm CIF MED, Benzina RBOB, Gas Naturale, Petrolio Brent/WTI e Emissioni CO2.

## 🌟 Caratteristiche

- **Dati in tempo reale** da Yahoo Finance con API alternative di backup
- **Conversioni automatiche** da varie unità a $/tonnellata e €/litro
- **Tasso di cambio live** EUR/USD con fallback automatico
- **Interfaccia doppia**: Console e GUI moderna
- **Auto-aggiornamento** programmabile
- **Esportazione CSV** con timestamp
- **Proxy intelligenti** per dati non disponibili

## 📦 Installazione

### 1. Clona o scarica i file
```bash
# Assicurati di avere questi file nella stessa cartella:
- gasoil_futures.py          # Motore principale
- energy_futures_gui.py      # Interfaccia grafica
- start_energy_tracker.py    # Launcher
- requirements.txt           # Dipendenze
```

### 2. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 3. Verifica Python
```bash
# Richiede Python 3.7+
python --version
```

## 🚀 Utilizzo

### Avvio rapido
```bash
python start_energy_tracker.py
```

### Modalità Console
```bash
python gasoil_futures.py
```

### Modalità GUI
```bash
python energy_futures_gui.py
```

## 📊 Prodotti Supportati

| Prodotto | Simbolo | Mercato | Unità |
|----------|---------|---------|-------|
| 🛢️ ULSD 10ppm CIF MED | HO=F | NY Harbor | $/gallon |
| ⛽ Benzina RBOB | RB=F | NYMEX | $/gallon |
| 🔥 Gas Naturale | NG=F | Henry Hub | $/MMBtu |
| 🛢️ Petrolio Brent | BZ=F | ICE London | $/barrel |
| 🛢️ Petrolio WTI | CL=F | NYMEX | $/barrel |
| 🌱 Emissioni CO2 | CER=F | EU ETS | €/ton |

## 🔄 Conversioni

### Fattori di conversione utilizzati:
- **Gasolio**: 1 tonnellata = 1,192 litri
- **Heating Oil**: 1 gallone = 3.78 litri (317.5 galloni/ton)
- **Crude Oil**: 1 barile = 159 litri (7.33 barili/ton)
- **Natural Gas**: 1 MMBtu ≈ 28.3 m³

### Formule:
```
$/ton → €/litro = (Prezzo_USD * Tasso_EUR_USD) / 1192
$/gallon → $/ton = Prezzo * 317.5 (per heating oil)
$/barrel → $/ton = Prezzo * 7.33 (per crude oil)
```

## 💻 Interfaccia GUI

### Funzionalità principali:
- **📊 Tabella dati** con colori per variazioni positive/negative
- **🔄 Auto-refresh** configurabile (30-300 secondi)
- **💾 Esportazione CSV** con dialog di salvataggio
- **📈 Monitoraggio in tempo reale** con threading
- **💱 Tasso di cambio live** EUR/USD
- **📍 Info mercati** e conversioni

### Controlli:
- `🔄 Aggiorna Dati`: Recupera prezzi aggiornati
- `Auto-aggiornamento`: Refresh automatico programmato
- `💾 Esporta CSV`: Salva dati con timestamp

## 📁 Output

### Console
```
📊 PREZZI FORWARD PRODOTTI ENERGETICI
╭─────────────┬────────────────┬───────────┬──────────────┬───────────────┬─────────────┬─────────┬─────────────────╮
│ Simbolo     │ Contratto      │ Scadenza  │ Prezzo $/ton │ Prezzo €/litro│ Variazione %│ Volume  │ Data Ultimo Prezzo│
├─────────────┼────────────────┼───────────┼──────────────┼───────────────┼─────────────┼─────────┼─────────────────┤
│ HO=F        │ 🛢️ ULSD 10ppm│ Front Mth │ $792.59      │ €0.5580       │ +2.68%      │ 45,123  │ 2025-01-15      │
╰─────────────┴────────────────┴───────────┴──────────────┴───────────────┴─────────────┴─────────┴─────────────────╯
```

### File CSV
```
Simbolo,Contratto,Scadenza,Prezzo_USD_ton,Prezzo_EUR_litro,Variazione_pct,Volume,Data_Ultimo_Prezzo
HO=F,🛢️ ULSD 10ppm CIF MED,Front Month,$792.59,€0.5580,+2.68%,45123,2025-01-15
```

## 🌐 API e Fonti Dati

### Primarie:
- **Yahoo Finance**: Dati futures principali
- **ExchangeRate-API**: Tassi di cambio EUR/USD

### Backup:
- **forex-python**: Tasso di cambio di fallback
- **Twelve Data API**: Futures alternativi (gratuita)
- **CommodityPriceAPI**: Prezzi commodity (gratuita)

## ⚙️ Configurazione

### Proxy ULSD 10ppm CIF MED
Il sistema usa **Heating Oil (HO=F)** come proxy per ULSD 10ppm CIF MED perché:
- Heating Oil È Ultra Low Sulfur Diesel 10ppm
- NY Harbor è il mercato di riferimento più liquido
- Correlazione molto alta con prezzi ICE Gasoil

### Timeouts API
- **Yahoo Finance**: 3 secondi
- **Exchange Rate**: 3 secondi  
- **Backup APIs**: 5 secondi

## 🔧 Troubleshooting

### Errori comuni:

**"Nessun dato recuperato"**
```bash
# Verifica connessione internet
ping yahoo.com

# Prova modalità console per debug
python gasoil_futures.py
```

**"ModuleNotFoundError"**
```bash
# Reinstalla dipendenze
pip install -r requirements.txt --upgrade
```

**"GUI non si avvia"**
```bash
# Verifica tkinter (Linux)
sudo apt-get install python3-tk

# macOS - dovrebbe essere incluso
# Windows - incluso in Python standard
```

### Debug mode:
Modifica in `gasoil_futures.py`:
```python
warnings.filterwarnings('ignore')  # Rimuovi questa riga per vedere i warning
```

## 📝 Limitazioni

- **Yahoo Finance**: A volte simboli ICE non disponibili (usa proxy)
- **Mercati chiusi**: Dati potrebbero essere del giorno precedente
- **API gratuite**: Rate limiting possibile con uso intensivo
- **CO2 Futures**: Non sempre disponibili su Yahoo Finance

## 🤝 Contributi

Per miglioramenti o bug:
1. Testa con modalità console per isolare problemi
2. Verifica connessione internet
3. Controlla log errori nella console

## 📄 Licenza

Script open source per uso educativo e di ricerca.

---

**⚡ Energy Futures Tracker** - Monitoraggio prezzi energetici in tempo reale 