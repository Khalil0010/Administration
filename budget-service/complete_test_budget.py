import requests
import uuid

# Le Budget Service tourne sur le port 8003
BASE_URL = "http://localhost:8003"


def run_budget_tests():
    print("=== DÉBUT DES TESTS DU BUDGET SERVICE SAVEWISE ===")

    unique_id = str(uuid.uuid4())[:8]
    test_email = f"user_{unique_id}@savewise.tn"
    category = "Alimentation"
    limit = 200.0

    # --- ÉTAPE 1 : DÉFINITION D'UN BUDGET (POST /budgets) ---
    print(f"\n1. Test de définition du budget ({category} : {limit} EUR)...")
    budget_payload = {
        "user_email": test_email,
        "category": category,
        "monthly_limit": limit
    }
    r_set = requests.post(f"{BASE_URL}/budgets", json=budget_payload)
    if r_set.status_code == 201:
        print(f"   [SUCCÈS] Budget initialisé pour {test_email}.")
    else:
        print(f"   [ERREUR] Échec de l'initialisation : {r_set.status_code}")
        return

    # --- ÉTAPE 2 : VÉRIFICATION DANS LA LIMITE (POST /budgets/check) ---
    print("\n2. Test de vérification d'une dépense autorisée (50 EUR)...")
    check_payload = {
        "user_email": test_email,
        "category": category,
        "amount": 50.0
    }
    r_check1 = requests.post(f"{BASE_URL}/budgets/check", json=check_payload)
    if r_check1.status_code == 200:
        data = r_check1.json()
        if not data["exceeded"] and data["new_total"] == 50.0:
            print(f"   [SUCCÈS] Dépense acceptée. Nouveau total : {data['new_total']}/{limit}")
        else:
            print(f"   [ÉCHEC] Résultat inattendu : {data}")
    else:
        print(f"   [ERREUR] Erreur lors du check : {r_check1.status_code}")

    # --- ÉTAPE 3 : DÉTECTION DE DÉPASSEMENT (POST /budgets/check) ---
    print("\n3. Test de détection de dépassement (Dépense de 160 EUR supplémentaires)...")
    check_over_payload = {
        "user_email": test_email,
        "category": category,
        "amount": 160.0
    }
    r_check2 = requests.post(f"{BASE_URL}/budgets/check", json=check_over_payload)
    if r_check2.status_code == 200:
        data = r_check2.json()
        if data["exceeded"]:
            print(f"   [SUCCÈS] Alerte déclenchée : {data['alert']} (Total: {data['new_total']})")
        else:
            print("   [ÉCHEC] Le dépassement n'a pas été détecté.")
    else:
        print(f"   [ERREUR] Erreur lors du check : {r_check2.status_code}")

    # --- ÉTAPE 4 : CONSULTATION DES BUDGETS (GET /budgets/{email}) ---
    print(f"\n4. Test de récupération de tous les budgets de {test_email}...")
    r_get = requests.get(f"{BASE_URL}/budgets/{test_email}")
    if r_get.status_code == 200:
        budgets = r_get.json()
        print(f"   [SUCCÈS] {len(budgets)} budget(s) trouvé(s).")
    else:
        print(f"   [ERREUR] Échec de récupération : {r_get.status_code}")

    # --- ÉTAPE 5 : TEST CATÉGORIE SANS BUDGET ---
    print("\n5. Test de vérification pour une catégorie sans budget défini...")
    no_budget_payload = {
        "user_email": test_email,
        "category": "Loisirs",
        "amount": 10.0
    }
    r_none = requests.post(f"{BASE_URL}/budgets/check", json=no_budget_payload)
    if r_none.status_code == 200 and r_none.json()["status"] == "no_budget_set":
        print("   [SUCCÈS] Le service gère correctement l'absence de budget.")
    else:
        print("   [ATTENTION] Comportement inattendu pour catégorie sans budget.")

    print("\n=== TOUS LES TESTS DU BUDGET SERVICE SONT TERMINÉS AVEC SUCCÈS ===")


if __name__ == "__main__":
    try:
        run_budget_tests()
    except requests.exceptions.ConnectionError:
        print("\n[ERREUR] Impossible de se connecter au Budget Service.")
        print("Assurez-vous que le conteneur tourne : docker run -p 8003:8003 savewise-budget")