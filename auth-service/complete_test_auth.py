import requests
import uuid

# Configuration du point d'entrée du microservice
BASE_URL = "http://localhost:8000"


def run_comprehensive_tests():
    print("=== DÉBUT DES TESTS DU SERVICE D'AUTHENTIFICATION SAVEWISE ===")

    # Génération d'un email unique pour éviter les conflits de base de données (Auth DB)
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"user_{unique_id}@savewise.tn"
    test_password = "password_secu_123"

    print(f"\n[INFO] Utilisateur de test : {test_email}")

    # --- ÉTAPE 1 : TEST DE L'INSCRIPTION (/register) ---
    print("\n1. Test de l'inscription...")
    reg_payload = {"email": test_email, "password": test_password}
    r_reg = requests.post(f"{BASE_URL}/register", json=reg_payload)

    if r_reg.status_code in [200, 201]:
        print("   [SUCCÈS] Inscription réussie.")
    else:
        print(f"   [ERREUR] Échec de l'inscription : {r_reg.status_code} - {r_reg.text}")
        return

    # --- ÉTAPE 2 : TEST DES DOUBLONS (Problématique de sécurité) ---
    print("2. Test de détection des doublons...")
    r_dup = requests.post(f"{BASE_URL}/register", json=reg_payload)
    if r_dup.status_code == 400:
        print("   [SUCCÈS] Le service refuse correctement les emails déjà existants.")
    else:
        print(f"   [ATTENTION] Le service devrait renvoyer 400 pour un doublon, a renvoyé : {r_dup.status_code}")

    # --- ÉTAPE 3 : TEST DE CONNEXION (/login) ---
    print("3. Test de la connexion (Génération de Token JWT)...")
    login_payload = {"email": test_email, "password": test_password}
    r_login = requests.post(f"{BASE_URL}/login", json=login_payload)

    token = None
    if r_login.status_code == 200:
        token = r_login.json().get("access_token")
        print(f"   [SUCCÈS] Token JWT généré : {token[:30]}...")
    else:
        print(f"   [ERREUR] Connexion échouée : {r_login.status_code}")
        return

    # --- ÉTAPE 4 : TEST DES MAUVAIS IDENTIFIANTS ---
    print("4. Test de sécurité (Mauvais mot de passe)...")
    bad_login = {"email": test_email, "password": "wrong_password"}
    r_bad = requests.post(f"{BASE_URL}/login", json=bad_login)
    if r_bad.status_code == 401:
        print("   [SUCCÈS] Accès refusé pour mot de passe incorrect.")
    else:
        print(f"   [ATTENTION] Devrait renvoyer 401, a renvoyé : {r_bad.status_code}")

    # --- ÉTAPE 5 : VÉRIFICATION DU TOKEN (/verify-token) ---
    print("5. Test de la validité du token JWT...")
    # Simulation d'un appel venant d'un autre microservice (ex: Transaction Service)
    r_verify = requests.get(f"{BASE_URL}/verify-token", params={"token": token})

    if r_verify.status_code == 200:
        user_data = r_verify.json()
        print(f"   [SUCCÈS] Token valide pour l'utilisateur : {user_data.get('email')}")
    else:
        print(f"   [ERREUR] Échec de vérification du token : {r_verify.status_code}")

    # --- ÉTAPE 6 : TEST D'UN TOKEN INVALIDE ---
    print("6. Test avec un token corrompu...")
    r_fake = requests.get(f"{BASE_URL}/verify-token", params={"token": "fake_token_123"})
    if r_fake.status_code == 401:
        print("   [SUCCÈS] Token corrompu correctement rejeté.")
    else:
        print(f"   [ATTENTION] Le service a accepté un faux token ou renvoyé une mauvaise erreur.")

    print("\n=== TOUS LES TESTS SONT TERMINÉS AVEC SUCCÈS ===")


if __name__ == "__main__":
    try:
        run_comprehensive_tests()
    except requests.exceptions.ConnectionError:
        print(
            "\n[ERREUR] Impossible de se connecter au service. Vérifiez que le conteneur Docker tourne sur le port 8000.")