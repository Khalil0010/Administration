import requests

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    # 1. Tester l'inscription
    reg_data = {"email": "test_auto@savewise.com", "password": "password123"}
    response = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"Registration: {response.status_code}")

    # 2. Tester le login et récupérer le JWT
    login_response = requests.post(f"{BASE_URL}/login", json=reg_data)
    token = login_response.json().get("access_token")
    print(f"Login (JWT Generated): {'Success' if token else 'Failed'}")

    # 3. Tester la vérification du token
    verify_response = requests.get(f"{BASE_URL}/verify-token", params={"token": token})
    print(f"Token Verification: {verify_response.json()}")

if __name__ == "__main__":
    test_auth_flow()