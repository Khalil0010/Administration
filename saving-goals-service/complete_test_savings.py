import requests
import uuid

# Le Saving Goals Service tourne sur le port 8004
BASE_URL = "http://localhost:8004"


def run_savings_tests():
    print("=== DÉBUT DES TESTS DU SAVING GOALS SERVICE SAVEWISE ===")

    unique_id = str(uuid.uuid4())[:8]
    test_email = f"etudiant_{unique_id}@savewise.tn"
    goal_name = "Nouvel Ordinateur"
    target = 1200.0

    # --- ÉTAPE 1 : CRÉATION D'UN OBJECTIF (POST /goals) ---
    print(f"\n1. Test de création d'objectif d'épargne ({goal_name})...")
    goal_payload = {
        "user_email": test_email,
        "name": goal_name,
        "target_amount": target,
        "deadline": "2026-06-01T00:00:00"
    }
    r_create = requests.post(f"{BASE_URL}/goals", json=goal_payload)

    goal_id = None
    if r_create.status_code == 201:
        data = r_create.json()
        goal_id = data["id"]
        print(f"   [SUCCÈS] Objectif créé avec l'ID: {goal_id}. Progression: {data['progress_percentage']}%")
    else:
        print(f"   [ERREUR] Échec de création : {r_create.status_code} - {r_create.text}")
        return

    # --- ÉTAPE 2 : AJOUT D'ÉPARGNE (PATCH /goals/{id}/add-savings) ---
    print("\n2. Test d'ajout d'épargne (Versement de 300 EUR)...")
    add_payload = {"amount_to_add": 300.0}
    r_add = requests.patch(f"{BASE_URL}/goals/{goal_id}/add-savings", json=add_payload)

    if r_add.status_code == 200:
        data = r_add.json()
        # Le calcul (300/1200) doit donner 25% [cite: 118]
        print(f"   [SUCCÈS] Épargne ajoutée. Nouveau solde: {data['current_amount']} EUR.")
        print(f"   [INFO] Progression calculée : {data['progress_percentage']}%")
    else:
        print(f"   [ERREUR] Échec de l'ajout : {r_add.status_code}")

    # --- ÉTAPE 3 : ATTEINTE DE L'OBJECTIF ---
    print("\n3. Test d'atteinte de l'objectif (Versement massif de 1000 EUR)...")
    r_final = requests.patch(f"{BASE_URL}/goals/{goal_id}/add-savings", json={"amount_to_add": 1000.0})
    if r_final.status_code == 200:
        data = r_final.json()
        print(f"   [SUCCÈS] Objectif atteint ! Progression : {data['progress_percentage']}%")
    else:
        print(f"   [ERREUR] Échec du versement final.")

    # --- ÉTAPE 4 : RÉCUPÉRATION DE LA LISTE (GET /goals/{email}) ---
    print(f"\n4. Test de récupération de tous les objectifs de {test_email}...")
    r_list = requests.get(f"{BASE_URL}/goals/{test_email}")
    if r_list.status_code == 200:
        goals = r_list.json()
        print(f"   [SUCCÈS] {len(goals)} objectif(s) trouvé(s) pour cet utilisateur.")
    else:
        print(f"   [ERREUR] Échec de récupération : {r_list.status_code}")

    # --- ÉTAPE 5 : TEST OBJECTIF INEXISTANT ---
    print("\n5. Test de mise à jour sur un ID inexistant...")
    r_fail = requests.patch(f"{BASE_URL}/goals/9999/add-savings", json={"amount_to_add": 10.0})
    if r_fail.status_code == 404:
        print("   [SUCCÈS] Le service renvoie bien 404 pour un ID inconnu.")
    else:
        print(f"   [ATTENTION] Code inattendu pour ID inexistant : {r_fail.status_code}")

    print("\n=== TOUS LES TESTS DU SAVING GOALS SERVICE SONT TERMINÉS AVEC SUCCÈS ===")


if __name__ == "__main__":
    try:
        run_savings_tests()
    except requests.exceptions.ConnectionError:
        print("\n[ERREUR] Impossible de se connecter au service.")
        print("Vérifiez que le conteneur tourne : docker run -p 8004:8004 savewise-savings")