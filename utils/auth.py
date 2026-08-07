import hashlib
import json
import os
import time
import streamlit as st

# Constantes
USER_CREDENTIALS_FILE = "users_credentials.json"


def initialize_auth():
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = False
    if "name" not in st.session_state:
        st.session_state.name = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "logout" not in st.session_state:
        st.session_state.logout = False

    if "users" not in st.session_state:
        if os.path.exists(USER_CREDENTIALS_FILE):
            try:
                with open(USER_CREDENTIALS_FILE, "r") as f:
                    st.session_state.users = json.load(f)
            except Exception:
                create_default_users()
        else:
            create_default_users()


def create_default_users():
    st.session_state.users = {
        "admin": {
            "password": hash_password("admin123"),
            "name": "Administrateur",
            "email": "admin@clv-analytics.com",
        },
    }
    save_users()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def save_users():
    try:
        with open(USER_CREDENTIALS_FILE, "w") as f:
            json.dump(st.session_state.users, f, indent=4)
    except Exception:
        pass


def verify_password(username, password):
    if username in st.session_state.users:
        stored_hash = st.session_state.users[username]["password"]
        return stored_hash == hash_password(password)
    return False


def login(username, password):
    if verify_password(username, password):
        st.session_state.authentication_status = True
        st.session_state.username = username
        st.session_state.name = st.session_state.users[username]["name"]
        return True
    return False


def logout():
    st.session_state.authentication_status = False
    st.session_state.name = None
    st.session_state.username = None
    st.session_state.logout = True


def register(username, password, confirm_password, email):
    if username in st.session_state.users:
        return False, "Ce nom d'utilisateur existe déjà"
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères"
    if password != confirm_password:
        return False, "Les mots de passe ne correspondent pas"

    st.session_state.users[username] = {
        "password": hash_password(password),
        "name": username,
        "email": email,
    }
    save_users()
    return True, "Compte créé avec succès"


def check_authentication():
    """Vérification globale"""
    initialize_auth()

    if st.session_state.get("logout", False):
        logout()
        st.session_state.logout = False
        st.rerun()

    if st.session_state.get("authentication_status", False):
        return True

    # Si pas connecté, on affiche le formulaire
    show_login_form()
    return False


def show_login_form():
    """Formulaire de connexion héritant 100% du style du thème global"""
    # Import local pour éviter toute exécution précoce
    from utils.ui_style import apply_custom_theme

    # 1. On applique le thème graphique personnalisé (Navigation, Mode Sombre/Clair, etc.)
    apply_custom_theme()

    # 2. CSS ajusté : hérite directement des couleurs du thème Streamlit / ui_style
    st.markdown(
        """
    <style>
    /* Centrage du formulaire */
    .stAppViewBlockContainer {
        max-width: 650px !important;
        padding-top: 2rem !important;
    }

    /* Boutons principaux : héritent de la couleur primaire de l'application sans forcer le bleu */
    div.stButton > button[kind="primary"], div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.8rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button:hover {
        opacity: 0.85 !important;
        transform: translateY(-1px);
    }

    /* Onglets Connexion / Inscription alignés sur le thème */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        justify-content: center;
    }

    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid var(--primary-color) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Entête CLV
    st.markdown(
        "<h1 style='text-align: center; font-size: 3.2rem; margin-bottom: 0;'>🔮</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align: center; font-size: 1.8rem;"
        " margin-bottom: 0.3rem;'>CLV Prediction Dashboard</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #64748B; margin-bottom:"
        " 2.2rem; font-size: 0.95rem;'>Customer Analytics • Prédiction ML •"
        " Segmentation Stratégique</p>",
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🔑 Se connecter", "📝 S'inscrire"])

    with tab1:
        st.markdown("### Connexion")
        username = st.text_input("Nom d'utilisateur", key="login_username")
        password = st.text_input(
            "Mot de passe", type="password", key="login_password"
        )

        st.write("")
        if st.button("Se connecter", key="login_btn", use_container_width=True):
            if not username or not password:
                st.error("Veuillez remplir tous les champs")
            elif login(username, password):
                st.success(f"✅ Bienvenue {st.session_state.name} !")
                time.sleep(0.4)
                st.switch_page("app.py")
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

    with tab2:
        st.markdown("### Créer un compte")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Nom d'utilisateur", key="reg_username")
        with col2:
            new_email = st.text_input("Email", key="reg_email")

        col3, col4 = st.columns(2)
        with col3:
            new_password = st.text_input(
                "Mot de passe", type="password", key="reg_password"
            )
        with col4:
            confirm_password = st.text_input(
                "Confirmer", type="password", key="reg_confirm_password"
            )

        st.write("")
        if st.button(
            "S'inscrire", key="register_btn", use_container_width=True
        ):
            if not all(
                [new_username, new_password, confirm_password, new_email]
            ):
                st.error("Veuillez remplir tous les champs")
            else:
                success, message = register(
                    new_username, new_password, confirm_password, new_email
                )
                if success:
                    st.success(
                        "✅ Compte créé avec succès ! Vous pouvez maintenant"
                        " vous connecter."
                    )
                else:
                    st.error(f"❌ {message}")

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #94A3B8; font-size: 0.85rem;'>CLV"
        " Prediction Dashboard © 2026 - Solution Décisionnelle & Machine"
        " Learning</p>",
        unsafe_allow_html=True,
    )

    st.stop()


def display_user_info():
    if st.session_state.get("authentication_status", False):
        st.sidebar.markdown(f"👤 **{st.session_state.name}**")
        if st.sidebar.button("🚪 Déconnexion", key="logout_sidebar_btn"):
            logout()
            st.rerun()