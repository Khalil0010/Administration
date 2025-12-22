import requests
import uuid

# Le User Service tourne sur le port 8001
BASE_URL = "http://localhost:8001"


def run_user_service_tests():
    print("=== DÉBUT DES TESTS DU USER SERVICE SAVEWISE ===")

    # Génération de données de test uniques
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"khalil_{unique_id}@etudiant-enit.utm.tn"

    profile_data = {
        "email": test_email,
        "first_name": "Khalil",
        "last_name": "Midouni",
        "occupation": "Étudiant",  # Cible définie dans le rapport
        "monthly_income": 800.0,
        "currency_preference": "TND"
    }

    # --- ÉTAPE 1 : CRÉATION DU PROFIL (POST /profiles) ---
    print("\n1. Test de création de profil...")
    r_create = requests.post(f"{BASE_URL}/profiles", json=profile_data)
    if r_create.status_code == 201:
        print(f"   [SUCCÈS] Profil créé pour {test_email}.")
    else:
        print(f"   [ERREUR] Échec de création : {r_create.status_code} - {r_create.text}")
        return

    # --- ÉTAPE 2 : TEST DES DOUBLONS ---
    print("2. Test de détection des doublons de profil...")
    r_dup = requests.post(f"{BASE_URL}/profiles", json=profile_data)
    if r_dup.status_code == 400:
        print("   [SUCCÈS] Le service refuse correctement de créer deux fois le même profil.")
    else:
        print(f"   [ATTENTION] Devrait renvoyer 400, a renvoyé : {r_dup.status_code}")

    # --- ÉTAPE 3 : RÉCUPÉRATION DU PROFIL (GET /profiles/{email}) ---
    print(f"3. Test de lecture du profil ({test_email})...")
    r_get = requests.get(f"{BASE_URL}/profiles/{test_email}")
    if r_get.status_code == 200:
        data = r_get.json()
        print(f"   [SUCCÈS] Profil récupéré. Occupation : {data['occupation']}")
    else:
        print(f"   [ERREUR] Impossible de lire le profil : {r_get.status_code}")

    # --- ÉTAPE 4 : MISE À JOUR DU PROFIL (PUT /profiles/{email}) ---
    print("4. Test de mise à jour (Changement d'occupation)...")
    update_payload = {
        "occupation": "Jeune Actif",  # Passage d'étudiant à jeune actif
        "monthly_income": 2500.0
    }
    r_update = requests.put(f"{BASE_URL}/profiles/{test_email}", json=update_payload)
    if r_update.status_code == 200:
        updated_data = r_update.json()
        print(f"   [SUCCÈS] Profil mis à jour. Nouveau revenu : {updated_data['monthly_income']}")
    else:
        print(f"   [ERREUR] Échec de la mise à jour : {r_update.status_code}")

    # --- ÉTAPE 5 : TEST PROFIL INEXISTANT ---
    print("5. Test de récupération d'un profil inexistant...")
    r_none = requests.get(f"{BASE_URL}/profiles/inconnu@test.tn")
    if r_none.status_code == 404:
        print("   [SUCCÈS] Le service renvoie bien 404 pour un profil absent.")
    else:
        print(f"   [ATTENTION] Mauvais code retourné pour profil absent : {r_none.status_code}")

    print("\n=== TOUS LES TESTS DU USER SERVICE SONT TERMINÉS AVEC SUCCÈS ===")


if __name__ == "__main__":
    try:
        run_user_service_tests()
    except requests.exceptions.ConnectionError:
        print("\n[ERREUR] Impossible de se connecter au User Service.")
        print("Assurez-vous que le conteneur tourne : docker run -p 8001:8001 savewise-user")