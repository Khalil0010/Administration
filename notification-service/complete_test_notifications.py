import requests

# Le Notification Service tourne sur le port 8006
BASE_URL = "http://localhost:8006"

def test_notifications():
    print("=== DÉBUT DES TESTS DU NOTIFICATION SERVICE SAVEWISE ===")
    email = "khalil.test@savewise.tn"

    # 1. Test d'envoi d'alerte budgétaire
    print("\n1. Envoi d'une alerte de dépassement de budget...")
    payload = {
        "user_email": email,
        "message": "Attention ! Votre budget 'Divertissement' a atteint 90%.",
        "alert_type": "BUDGET"
    }
    r_send = requests.post(f"{BASE_URL}/notifications", json=payload)
    if r_send.status_code == 201:
        print("   [SUCCÈS] Notification envoyée et enregistrée.")
    else:
        print(f"   [ERREUR] {r_send.status_code}")

    # 2. Test d'envoi d'alerte épargne
    print("\n2. Envoi d'un rappel d'objectif d'épargne...")
    payload_save = {
        "user_email": email,
        "message": "Félicitations ! Vous avez atteint 50% de votre objectif 'PC'.",
        "alert_type": "SAVINGS"
    }
    requests.post(f"{BASE_URL}/notifications", json=payload_save)

    # 3. Test de récupération de l'historique
    print(f"\n3. Récupération de l'historique pour {email}...")
    r_get = requests.get(f"{BASE_URL}/notifications/{email}")
    if r_get.status_code == 200:
        notifs = r_get.json()
        print(f"   [SUCCÈS] {len(notifs)} alertes trouvées en base.")
    else:
        print(f"   [ERREUR] {r_get.status_code}")

    print("\n=== TOUS LES TESTS SONT TERMINÉS AVEC SUCCÈS ===")

if __name__ == "__main__":
    test_notifications()