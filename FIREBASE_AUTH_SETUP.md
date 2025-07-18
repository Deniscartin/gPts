# Configurazione Firebase Authentication per Gasolio

Questa guida ti aiuterà a configurare Firebase Authentication per proteggere l'accesso alla tua applicazione Gasolio.

## Passo 1: Creare un Progetto Firebase

1. Vai alla [Console Firebase](https://console.firebase.google.com/)
2. Clicca su "Crea un progetto" o "Aggiungi progetto"
3. Scegli un nome per il progetto (es. "gasolio-tracker")
4. Abilita Google Analytics se desideri (opzionale)
5. Clicca su "Crea progetto"

## Passo 2: Configurare Authentication

1. Nel tuo progetto Firebase, vai a **Authentication** nel menu laterale
2. Clicca su **Inizia**
3. Vai alla scheda **Sign-in method**
4. Abilita **Email/Password**:
   - Clicca su "Email/Password"
   - Abilita la prima opzione "Email/Password"
   - Salva

## Passo 3: Ottenere le Credenziali Web

1. Vai alle **Impostazioni progetto** (icona ingranaggio)
2. Scorri verso il basso e clicca su **Aggiungi app** → **Web**
3. Dai un nome alla tua app (es. "Gasolio Web")
4. Copia la configurazione Firebase che appare

## Passo 4: Configurare l'Applicazione Web

1. Apri il file `platts/platts_viewer.html`
2. Trova la sezione con `firebaseConfig`
3. Sostituisci i valori placeholder con quelli del tuo progetto:

```javascript
const firebaseConfig = {
    apiKey: "la-tua-api-key",
    authDomain: "il-tuo-progetto.firebaseapp.com",
    projectId: "il-tuo-project-id",
    storageBucket: "il-tuo-progetto.appspot.com",
    messagingSenderId: "123456789",
    appId: "il-tuo-app-id"
};
```

## Passo 5: Configurare il Server (Firebase Admin)

1. Nella Console Firebase, vai a **Impostazioni progetto** → **Account di servizio**
2. Clicca su **Genera nuova chiave privata**
3. Scarica il file JSON
4. Rinomina il file in `serviceAccount.json`
5. Copia il file nella directory principale del progetto (dove si trova `data_server.py`)

## Passo 6: Creare il Primo Utente

Una volta configurato tutto:

1. Avvia il server: `python data_server.py`
2. Apri il browser su `http://127.0.0.1:5001`
3. Clicca su "Registrati"
4. Inserisci email e password
5. Clicca su "Registrati"

## Gestione Utenti

### Dalla Console Firebase
1. Vai alla sezione **Authentication** → **Users**
2. Qui puoi vedere tutti gli utenti registrati
3. Puoi disabilitare/eliminare utenti se necessario

### Aggiungere Utenti Manualmente
1. Nella Console Firebase, vai ad **Authentication** → **Users**
2. Clicca su **Aggiungi utente**
3. Inserisci email e password
4. Clicca su **Aggiungi utente**

## Sicurezza

- Le password devono essere di almeno 6 caratteri
- Gli utenti possono registrarsi autonomamente (puoi disabilitare questa funzione nelle impostazioni di Authentication)
- I token di autenticazione scadono automaticamente dopo 1 ora
- Il server verifica ogni richiesta API con il token Firebase

## File di Configurazione di Esempio

Se il file `serviceAccount.json` non viene trovato, il sistema userà dati mock per il testing. Assicurati che il file sia presente per la produzione.

## Risoluzione Problemi

### Errore "Firebase configuration not found"
- Verifica che i valori in `firebaseConfig` siano corretti
- Controlla che il progetto Firebase sia attivo

### Errore "Token verification failed"
- Verifica che il file `serviceAccount.json` sia presente
- Controlla che il Project ID nel file JSON corrisponda a quello nella configurazione web

### Utenti non possono registrarsi
- Verifica che Email/Password sia abilitato in Firebase Console
- Controlla che non ci siano restrizioni di dominio configurate

## Test della Configurazione

Per testare che tutto funzioni:

1. Avvia il server
2. Prova a registrare un nuovo utente
3. Fai login con le credenziali
4. Verifica che i dati Gasolio vengano caricati correttamente
5. Prova il logout e verifica che l'accesso sia negato

## Configurazioni Avanzate (Opzionali)

### Limitare le Registrazioni
Per impedire registrazioni pubbliche:
1. Authentication → Settings → User actions
2. Disabilita "Create (sign-up)"

### Aggiungere Domini Autorizzati
1. Authentication → Settings → Authorized domains
2. Aggiungi solo i tuoi domini

### Configurare Regole di Sicurezza
Nelle regole Firestore, puoi limitare l'accesso solo agli utenti autenticati:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
``` 