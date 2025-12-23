import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration de l'interface professionnelle
st.set_page_config(page_title="SaveWise - Pilotage Financier", layout="wide", page_icon="💰")

# --- RÉSEAU DES MICROSERVICES (DNS Docker) ---
SERVICES = {
    "auth": "http://auth-service.savewise:8000",
    "user": "http://user-service.savewise:8001",
    "tx": "http://transaction-service.savewise:8002",
    "budget": "http://budget-service.savewise:8003",
    "savings": "http://saving-goals-service.savewise:8004",
    "analytics": "http://analytics-service.savewise:8005",
    "notifications": "http://notification-service.savewise:8006"
}

# --- GESTION DE LA SESSION ---
if "token" not in st.session_state: st.session_state.token = None
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_name" not in st.session_state: st.session_state.user_name = "Utilisateur"


# --- FONCTIONS UTILES ---
def fetch_user_name(email):
    """Récupère le prénom depuis le User Service pour l'affichage personnalisé."""
    try:
        res = requests.get(f"{SERVICES['user']}/profiles/{email}")
        if res.status_code == 200:
            st.session_state.user_name = res.json().get("first_name", "Ami")
    except:
        pass


# --- BARRE LATÉRALE : AUTHENTIFICATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1611/1611154.png", width=100)
    st.title("SaveWise Hub")

    if not st.session_state.token:
        auth_mode = st.tabs(["Connexion", "Inscription"])

        with auth_mode[0]:
            l_email = st.text_input("Email", key="login_email")
            l_pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            if st.button("Se connecter", use_container_width=True):
                res = requests.post(f"{SERVICES['auth']}/login", json={"email": l_email, "password": l_pwd})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.user_email = l_email
                    fetch_user_name(l_email)
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")

        with auth_mode[1]:
            r_email = st.text_input("Email", key="reg_email")
            r_pwd = st.text_input("Mot de passe", type="password", key="reg_pwd")
            r_name = st.text_input("Votre Prénom")
            if st.button("Créer un compte", use_container_width=True):
                # Inscription Auth + Création Profil User
                if requests.post(f"{SERVICES['auth']}/register",
                                 json={"email": r_email, "password": r_pwd}).status_code in [200, 201]:
                    requests.post(f"{SERVICES['user']}/profiles",
                                  json={"email": r_email, "first_name": r_name, "last_name": "",
                                        "occupation": "Étudiant", "monthly_income": 0})
                    st.success("Compte créé ! Connectez-vous.")
    else:
        st.write(f"Utilisateur : **{st.session_state.user_name}**")
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.token = None
            st.rerun()

# --- TABLEAU DE BORD PRINCIPAL ---
if st.session_state.token:
    st.title(f"Bonjour, {st.session_state.user_name} 👋")

    tabs = st.tabs(["📊 Synthèse", "💸 Transactions & Budgets", "🎯 Épargne", "🔔 Alertes"])

    # --- TAB 1 : ANALYTICS (SYNTHÈSE) ---
    with tabs[0]:
        st.subheader("Analyse Financière Globale")
        try:
            res_an = requests.get(f"{SERVICES['analytics']}/analytics/report/{st.session_state.user_email}")
            if res_an.status_code == 200:
                data = res_an.json()
                c1, c2, c3 = st.columns(3)
                c1.metric("Dépenses Totales", f"{data.get('total_spent', 0)} €", delta_color="inverse")
                c2.metric("Revenus Totaux", f"{data.get('total_income', 0)} €")
                c3.metric("Taux d'Épargne", f"{data.get('savings_rate_percent', 0)} %")

                # Formule pédagogique
                st.write(f"Calcul : $$Taux = \\frac{{Revenus - Dépenses}}{{Revenus}} \\times 100$$")

                # Graphique de répartition
                res_tx = requests.get(f"{SERVICES['tx']}/transactions/{st.session_state.user_email}")
                if res_tx.status_code == 200 and res_tx.json():
                    df = pd.DataFrame(res_tx.json())
                    if not df.empty and "EXPENSE" in df['type'].values:
                        fig = px.pie(df[df['type'] == 'EXPENSE'], values='amount', names='category',
                                     title="Répartition des dépenses")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée disponible. Ajoutez un revenu pour commencer !")
        except:
            st.error("Service d'analyse indisponible.")

    # --- TAB 2 : TRANSACTIONS & BUDGETS (LOGIQUE INCOME/EXPENSE) ---
    with tabs[1]:
        col_form, col_budget = st.columns(2)

        with col_form:
            st.subheader("Enregistrer un mouvement")
            with st.form("tx_form", clear_on_submit=True):
                desc = st.text_input("Description (ex: Salaire, Loyer)")
                amt = st.number_input("Montant", min_value=0.1)
                t_type = st.selectbox("Type", ["EXPENSE", "INCOME"])

                # Logique Spécification : Pas de catégorie pour les revenus
                category = "Revenu Général"
                if t_type == "EXPENSE":
                    category = st.selectbox("Catégorie de dépense", ["Alimentation", "Loisirs", "Transport", "Santé"])

                if st.form_submit_button("Valider"):
                    # 1. Ajout de la transaction
                    requests.post(f"{SERVICES['tx']}/transactions", json={
                        "user_email": st.session_state.user_email, "amount": amt,
                        "description": desc, "type": t_type, "category": category
                    })

                    # 2. Logique d'alerte intelligente (si dépense)
                    if t_type == "EXPENSE":
                        chk = requests.post(f"{SERVICES['budget']}/budgets/check", json={
                            "user_email": st.session_state.user_email, "category": category, "amount": amt
                        }).json()

                        if chk.get("exceeded"):
                            # On envoie une notification réelle au Notification Service
                            requests.post(f"{SERVICES['notifications']}/notifications", json={
                                "user_email": st.session_state.user_email,
                                "message": f"Dépassement de budget détecté en {category} ! Total: {chk['new_total']}€",
                                "alert_type": "BUDGET_OVERFLOW"
                            })
                    st.success("Mouvement enregistré !")
                    st.rerun()

        with col_budget:
            st.subheader("Mes Limites Budgétaires")
            with st.expander("➕ Définir un nouveau budget"):
                b_cat = st.selectbox("Catégorie", ["Alimentation", "Loisirs", "Transport", "Santé"])
                b_lim = st.number_input("Limite mensuelle", min_value=1.0)
                if st.button("Fixer la limite"):
                    requests.post(f"{SERVICES['budget']}/budgets",
                                  json={"user_email": st.session_state.user_email, "category": b_cat,
                                        "monthly_limit": b_lim})
                    st.rerun()

            res_b = requests.get(f"{SERVICES['budget']}/budgets/{st.session_state.user_email}")
            if res_b.status_code == 200 and res_b.json():
                st.dataframe(pd.DataFrame(res_b.json())[['category', 'monthly_limit', 'current_spent']],
                             use_container_width=True)

    # --- TAB 3 : ÉPARGNE INTERACTIVE (PROGRESSION) ---
    with tabs[2]:
        st.subheader("Gestion de vos Objectifs")
        with st.expander("➕ Créer un projet"):
            g_name = st.text_input("Nom de l'objectif (ex: Voyage, PC)")
            g_target = st.number_input("Cible à atteindre (€)", min_value=10.0)
            if st.button("Lancer le projet"):
                requests.post(f"{SERVICES['savings']}/goals",
                              json={"user_email": st.session_state.user_email, "name": g_name,
                                    "target_amount": g_target})
                st.rerun()

        res_g = requests.get(f"{SERVICES['savings']}/goals/{st.session_state.user_email}")
        if res_g.status_code == 200 and res_g.json():
            for goal in res_g.json():
                c_info, c_act = st.columns([4, 1])
                with c_info:
                    st.write(f"**{goal['name']}**")
                    st.progress(min(goal['progress_percentage'] / 100, 1.0))
                    st.caption(
                        f"Progression : {goal['current_amount']}€ / {goal['target_amount']}€ ({goal['progress_percentage']}%)")
                with c_act:
                    # Spécification : Avancer dans l'objectif
                    add_amt = st.number_input("Verser", min_value=1.0, key=f"add_{goal['id']}")
                    if st.button("Épargner", key=f"btn_{goal['id']}"):
                        requests.patch(f"{SERVICES['savings']}/goals/{goal['id']}/add-savings",
                                       json={"amount_to_add": add_amt})
                        st.rerun()
                st.divider()

    # --- TAB 4 : NOTIFICATIONS (ALERTES) ---
    with tabs[3]:
        st.subheader("Historique des Notifications")
        res_n = requests.get(f"{SERVICES['notifications']}/notifications/{st.session_state.user_email}")
        if res_n.status_code == 200 and res_n.json():
            for notif in reversed(res_n.json()):
                st.info(f"📅 {notif['timestamp'][:16]} — {notif['message']}")
        else:
            st.write("Tout est en ordre, aucune alerte pour le moment.")

else:
    st.warning("Veuillez vous authentifier pour accéder à vos finances SaveWise.")