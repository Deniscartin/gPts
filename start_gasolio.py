import os
import sys
import subprocess
import webbrowser
import time
import requests
from threading import Thread

def run_server():
    """Run the Flask server"""
    import data_server
    data_server.app.run(host='127.0.0.1', port=5001)

def check_server():
    """Check if server is running"""
    try:
        response = requests.get('http://127.0.0.1:5001/')
        return response.status_code == 200
    except:
        return False

def main():
    # Get the directory of the executable
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Change to the application directory
    os.chdir(application_path)

    # Start the server in a separate thread
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    print("🚀 Avvio Gasolio Tracker...")
    print("⌛ Attendere mentre il server si avvia...")

    # Wait for server to start (max 30 seconds)
    for _ in range(30):
        if check_server():
            print("✅ Server avviato con successo!")
            print("\n📱 Apertura applicazione nel browser...")
            webbrowser.open('http://127.0.0.1:5001')
            
            print("\n🎉 Gasolio Tracker è pronto!")
            print("\nℹ️  Per chiudere l'applicazione, chiudi questa finestra.")
            print("ℹ️  Per riaprire l'interfaccia, vai a http://127.0.0.1:5001")
            
            # Keep the window open
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Chiusura Gasolio Tracker...")
                sys.exit(0)
            
            return
        time.sleep(1)
        print(".", end="", flush=True)

    print("\n❌ Errore: Impossibile avviare il server!")
    input("Premi INVIO per chiudere...")
    sys.exit(1)

if __name__ == '__main__':
    main() 