import requests

# Le Transaction Service tourne sur le port 8002
BASE_URL = "http://localhost:8002"


def run_transaction_tests():
    print("=== DÉBUT DES TESTS DU TRANSACTION SERVICE SAVEWISE ===")

    test_email = "khalil.test@etudiant-enit.utm.tn"

    # Scénarios de test pour la catégorisation automatique
    test_cases = [
        {
            "description": "Courses à Carrefour Market",
            "amount": 45.50,
            "type": "EXPENSE",
            "expected_category": "Alimentation"
        },
        {
            "description": "Paiement du Loyer Janvier",
            "amount": 500.0,
            "type": "EXPENSE",
            "expected_category": "Logement"
        },
        {
            "description": "Abonnement Netflix",
            "amount": 12.99,
            "type": "EXPENSE",
            "expected_category": "Divertissement"
        },
        {
            "description": "Virement Salaire",
            "amount": 1200.0,
            "type": "INCOME",
            "expected_category": "Revenus"
        },
        {
            "description": "Achat imprévu",
            "amount": 10.0,
            "type": "EXPENSE",
            "expected_category": "Alimentation"
        }
    ]

    # --- ÉTAPE 1 : TEST DE CRÉATION ET CATÉGORISATION ---
    print("\n1. Test d'ajout de transactions et catégorisation automatique...")
    for case in test_cases:
        payload = {
            "user_email": test_email,
            "amount": case["amount"],
            "description": case["description"],
            "type": case["type"]
        }

        r = requests.post(f"{BASE_URL}/transactions", json=payload)

        if r.status_code == 201:
            data = r.json()
            cat = data["category"]
            status = "SUCCÈS" if cat == case["expected_category"] else "ÉCHEC"
            print(f"   [{status}] Description: '{case['description']}' -> Catégorie: {cat}")
        else:
            print(f"   [ERREUR] Impossible d'ajouter la transaction : {r.status_code}")

    # --- ÉTAPE 2 : TEST DE RÉCUPÉRATION DE L'HISTORIQUE ---
    print(f"\n2. Test de récupération de l'historique pour {test_email}...")
    r_history = requests.get(f"{BASE_URL}/transactions/{test_email}")

    if r_history.status_code == 200:
        history = r_history.json()
        print(f"   [SUCCÈS] {len(history)} transactions récupérées dans l'historique.")

        # Vérification rapide de l'intégrité des données
        if len(history) > 0:
            print(
                f"   [INFO] Dernière transaction enregistrée : {history[-1]['description']} ({history[-1]['amount']} EUR)")
    else:
        print(f"   [ERREUR] Échec de récupération : {r_history.status_code}")

    # --- ÉTAPE 3 : TEST D'HISTORIQUE VIDE ---
    print("\n3. Test avec un utilisateur sans transactions...")
    r_empty = requests.get(f"{BASE_URL}/transactions/nouveau@user.tn")
    if r_empty.status_code == 200 and len(r_empty.json()) == 0:
        print("   [SUCCÈS] Le service gère correctement les historiques vides.")
    else:
        print("   [ATTENTION] Comportement inattendu pour un historique vide.")

    print("\n=== TOUS LES TESTS DU TRANSACTION SERVICE SONT TERMINÉS ===")


if __name__ == "__main__":
    try:
        run_transaction_tests()
    except requests.exceptions.ConnectionError:
        print("\n[ERREUR] Impossible de se connecter au Transaction Service.")
        print("Vérifiez que le conteneur tourne : docker run -p 8002:8002 savewise-transaction")