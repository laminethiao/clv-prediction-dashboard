import streamlit as st
from utils.auth import check_authentication, display_user_info
from utils.ui_style import apply_custom_theme

# 1. Configuration de la page (Strictement la première commande Streamlit)
st.set_page_config(
    page_title="CLV Prediction Dashboard",
    page_icon="🏠",
    layout="wide"
)

# 2. Vérification de l'authentification (Bloque l'accès si non connecté)
check_authentication()

# 3. Application du style centralisé
is_dark, plotly_template, text_color = apply_custom_theme()

# 4. Affichage des infos utilisateur et déconnexion dans la sidebar
with st.sidebar:
    st.markdown("---")
    display_user_info()

# --- CONTENU DE LA PAGE D'ACCUEIL ---

# En-tête
st.title("🔮 Plateforme Décisionnelle de Prédiction de la Customer Lifetime Value (CLV)")
st.markdown("Solution de prédiction financière et de segmentation stratégique basée sur le Machine Learning.")
st.markdown("---")

# -----------------------------------------------------------------------------
# BLOC 1 : PERFORMANCES DU MODÈLE CATBOOST (NOUVEAUTÉ)
# -----------------------------------------------------------------------------
st.markdown("### ⚡ Performance du Modèle Prédictif")

# Cartes de métriques
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        label="Algorithme Déployé",
        value="CatBoost",
        delta="Gradient Boosting",
        delta_color="normal"
    )

with m2:
    st.metric(
        label="Précision R² (Score)",
        value="0.522",
        delta="52.2% de variance expliquée",
        delta_color="normal"
    )

with m3:
    st.metric(
        label="Erreur Moyenne (RMSE)",
        value="277.50 $",
        delta="Écart moyen par client",
        delta_color="inverse"
    )

with m4:
    st.metric(
        label="Statut du Modèle",
        value="En Production",
        delta="Validé sur Silver/Gold",
        delta_color="normal"
    )

# Petite note d'explication métier sous les métriques
st.info(
    "💡 **Interprétation Métier :** Le modèle **CatBoost Regressor** a été retenu pour sa capacité à gérer la non-linéarité des comportements d'achat. "
    "Avec un score **$R^2$ de 0.522**, le modèle capture plus de **52% de la variabilité** de la valeur future des clients, "
    "offrant une marge d'erreur moyenne d'environ **277.50 $** sur la période cible."
)

st.markdown("---")

# -----------------------------------------------------------------------------
# BLOC 2 : CONTEXTE ET VALEUR AJOUTÉE
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("### 🚀 Contexte & Objectif Business")
    st.markdown("""
    La **Customer Lifetime Value (CLV)** représente la valeur financière nette estimée qu'un client génère tout au long de sa relation avec la marque.

    Cette plateforme permet à la direction marketing et commerciale de :
    * **Anticiper la rentabilité** future de chaque foyer client.
    * **Détecter préventivement le Churn** (clients inactifs à fort potentiel).
    * **Optimiser les budgets marketing** en ciblant prioritairement les profils *High Value*.
    """)

with col_right:
    st.markdown("### 🗺️ Navigation dans la Plateforme")

    st.markdown("""
    <div style="padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px;">
        <strong>📊 1. Customer Analytics</strong><br>
        <span style="font-size: 0.85em; color: #94A3B8;">Vue d'ensemble commerciale, KPIs macro et comportement des foyers.</span>
    </div>
    <div style="padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px;">
        <strong>🔮 2. CLV Predictor</strong><br>
        <span style="font-size: 0.85em; color: #94A3B8;">Interface de scoring en direct pour estimer la valeur future d'un client.</span>
    </div>
    <div style="padding: 12px; border-radius: 8px; border: 1px solid #334155;">
        <strong>🎯 3. Segmentation & Insights</strong><br>
        <span style="font-size: 0.85em; color: #94A3B8;">Typologie client (RFM) et recommandations d'actions CRM.</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")