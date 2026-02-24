from flask import Flask, jsonify
import sqlite3
import random
import time
from datetime import datetime
import threading
import uuid
from faker import Faker

# --- Configuration ---
DB_NAME = "bank.db"
TRANSACTION_INTERVAL_SECONDS = 5
TRANSACTIONS_PER_INTERVAL = 10 
fake = Faker('fr_FR')

# Liste pour stocker les transactions simulées enrichies
transaction_queue = []

# --- Initialisation Flask ---
app = Flask(__name__)

# --- Fonctions de Simulation ---

def get_account_and_client_details(account_id):
    """Récupère les informations du compte et du client pour une transaction."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permet d'accéder aux colonnes par leur nom
    cursor = conn.cursor()
    
    # Requête SQL pour joindre les tables CLIENT et COMPTE
    cursor.execute("""
        SELECT 
            c.nom, c.prénom, c.profession, c.revenu_mensuel, c.situation_familiale, 
            c.date_adhesion, c.localisation, c.date_naissance,
            a.solde
        FROM client c
        JOIN compte a ON c.client_id = a.client_id
        WHERE a.compte_id = ?
    """, (account_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Convertir la ligne en dictionnaire pour l'enrichissement de la transaction
        return dict(row)
    return None


def get_random_account_id():
    """Récupère un ID de compte aléatoire pour simuler la transaction."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Récupérer tous les compte_id actifs
    cursor.execute("SELECT compte_id FROM compte WHERE statut = 'Actif'")
    accounts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return random.choice(accounts) if accounts else None


def simulate_transaction():
    """Génère une transaction aléatoire, l'enrichit avec les données client/compte et l'ajoute à la queue."""
    global transaction_queue
    
    account_id = get_random_account_id()
    if not account_id:
        print("Aucun compte actif trouvé pour simuler.")
        return

    # 1. Obtenir les détails client/compte
    client_data = get_account_and_client_details(account_id)
    if not client_data:
        print(f"Détails client/compte non trouvés pour l'ID {account_id}.")
        return

    # 2. Simuler la transaction
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "compte_id": account_id,
        "date_transaction": datetime.now().isoformat(),
        "montant": round(random.uniform(5, 2000), 2), 
        "type_transaction": random.choice(['Dépôt', 'Retrait', 'Virement', 'Paiement']),
        "categorie": random.choice(['Alimentation', 'Voyages', 'Factures', 'Loisirs', 'Santé', 'Salaire', 'Transfert']),
        "canal": random.choice(['En ligne', 'Agence', 'Mobile', 'ATM'])
    }
    
    # 3. Mettre à jour le solde (simplifié)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if transaction["type_transaction"] in ['Retrait', 'Paiement', 'Virement']:
        amount = -abs(transaction["montant"])
    else: 
        amount = abs(transaction["montant"])

    # Mettre à jour le solde dans la DB
    cursor.execute("UPDATE compte SET solde = solde + ? WHERE compte_id = ?", (amount, account_id))
    conn.commit()
    conn.close()
    
    # Mettre à jour le solde du snapshot (pour la prochaine transaction)
    client_data['solde'] = client_data['solde'] + amount 
    
    # 4. Combiner la transaction et les données client/compte
    enriched_transaction = {**transaction, **client_data}
    
    transaction_queue.append(enriched_transaction)
    print(f"Transaction simulée enrichie pour compte {account_id}: {transaction['type_transaction']} {transaction['montant']}")


def data_simulator_thread():
    """Thread qui simule de nouvelles transactions toutes les 5 secondes."""
    while True:
        time.sleep(TRANSACTION_INTERVAL_SECONDS)
        for _ in range(TRANSACTIONS_PER_INTERVAL):
             simulate_transaction()

# --- API Endpoint ---

@app.route('/api/transactions/stream', methods=['GET'])
def get_transactions_stream():
    """Expose les transactions enrichies générées depuis le dernier appel."""
    global transaction_queue
    
    transactions_snapshot = list(transaction_queue)
    transaction_queue = [] # Vider la queue
    
    return jsonify(transactions_snapshot), 200

# --- Lancement du Serveur ---

if __name__ == '__main__':
    # Démarrer le thread de simulation de données en arrière-plan
    simulator_thread = threading.Thread(target=data_simulator_thread, daemon=True)
    simulator_thread.start()

    # Démarrer le serveur Flask
    print(f"Serveur Flask démarré sur http://0.0.0.0:5000. Intervalle de transaction: {TRANSACTION_INTERVAL_SECONDS}s")
    app.run(host='0.0.0.0', port=5000)