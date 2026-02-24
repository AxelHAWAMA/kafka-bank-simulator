import sqlite_utils
from faker import Faker
import random
from datetime import date, timedelta

# Initialisation de Faker pour les données en français
fake = Faker('fr_FR')
DB_NAME = "bank.db"
NUM_CLIENTS = 100

def generate_clients(db):
    clients = []
    accounts = []
    for i in range(1, NUM_CLIENTS + 1):
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
        # Informations Client
        clients.append({
            "client_id": i,
            "nom": fake.last_name(),
            "prénom": fake.first_name(),
            "date_naissance": birth_date.isoformat(),
            "sexe": random.choice(['M', 'F']),
            "profession": fake.job(),
            # Revenu entre 1500 et 10000
            "revenu_mensuel": round(random.uniform(1500, 10000), 2),
            "situation_familiale": random.choice(['Célibataire', 'Marié', 'Divorcé']),
            "localisation": fake.city(),
            "date_adhesion": (date.today() - timedelta(days=random.randint(365, 3650))).isoformat()
        })
        
        # Simplification : 1 compte courant par client
        accounts.append({
            "compte_id": i * 10,
            "client_id": i,
            "type_compte": "Courant",
            "solde": round(random.uniform(500, 50000), 2),
            "date_ouverture": clients[-1]["date_adhesion"],
            "statut": "Actif"
        })
        
    db["client"].insert_all(clients, pk="client_id", alter=True)
    db["compte"].insert_all(accounts, pk="compte_id", alter=True)
    print(f"Base de données '{DB_NAME}' créée avec {NUM_CLIENTS} clients et comptes.")

if __name__ == "__main__":
    db = sqlite_utils.Database(DB_NAME)
    # Créer les tables basées sur les sources pour garantir la structure
    db["client"].create({
        "client_id": int,
        "nom": str,
        "prénom": str,
        "date_naissance": str,
        "sexe": str,
        "profession": str,
        "revenu_mensuel": float,
        "situation_familiale": str,
        "localisation": str,
        "date_adhesion": str
    }, pk="client_id")
    
    db["compte"].create({
        "compte_id": int,
        "client_id": int,
        "type_compte": str,
        "solde": float,
        "date_ouverture": str,
        "statut": str
    }, pk="compte_id")

    generate_clients(db)