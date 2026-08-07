import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import shap
import os

from utils.auth import check_authentication, display_user_info
from utils.data_loader import load_gold_data
from utils.ui_style import apply_custom_theme

# -----------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & THÈME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CLV Predictor & Explainability",
    page_icon="🔮",
    layout="wide"
)
check_authentication()

is_dark, plotly_template, default_text_color = apply_custom_theme()
display_user_info()


# Couleurs dynamiques strictes selon le thème (Clair vs Sombre)
if is_dark:
    select_text_color = "#F8FAFC"
    bg_select = "#1E293B"
    border_select = "#334155"
    card_bg = "#1E293B"
    card_border = "#334155"
    graph_text_color = "#F8FAFC"
    grid_color = "rgba(255,255,255,0.1)"
else:
    select_text_color = "#0F172A"
    bg_select = "#FFFFFF"
    border_select = "#CBD5E1"
    card_bg = "#F8FAFC"
    card_border = "#E2E8F0"
    graph_text_color = "#0F172A"
    grid_color = "rgba(0,0,0,0.08)"

# Injecter le CSS dynamique pour forcer la visibilité du texte dans le Selectbox
st.markdown(f"""
    <style>
        /* Texte du selectbox principal */
        div[data-baseweb="select"] > div {{
            background-color: {bg_select} !important;
            color: {select_text_color} !important;
            border: 1px solid {border_select} !important;
        }}
        /* Texte à l'intérieur du champ de saisie */
        div[data-baseweb="select"] * {{
            color: {select_text_color} !important;
        }}
        /* Menu déroulant des options */
        div[data-baseweb="popover"] ul {{
            background-color: {bg_select} !important;
        }}
        div[data-baseweb="popover"] ul li {{
            color: {select_text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("🔮 CLV Predictor & Explainability (CatBoost & SHAP)")
st.markdown(
    "Plateforme d'aide à la décision basée sur un modèle de régression **CatBoost** et l'explicabilité **SHAP**.")
st.markdown("---")


# -----------------------------------------------------------------------------
# CHARGEMENT DU MODÈLE ET DU SCALER
# -----------------------------------------------------------------------------
@st.cache_resource
def load_ml_pipeline():
    """Charge le modèle CatBoost et le Scaler depuis le dossier models/."""
    model_path = os.path.join("models", "model_catboost_clv.pkl")
    scaler_path = os.path.join("models", "scaler_clv.pkl")

    model = None
    scaler = None

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
        except Exception as e:
            st.error(f"Erreur lors du chargement du modèle `{model_path}` : {e}")
    else:
        st.error(f"⚠️ Fichier introuvable : `{model_path}`")

    if os.path.exists(scaler_path):
        try:
            scaler = joblib.load(scaler_path)
        except Exception as e:
            st.error(f"Erreur lors du chargement du scaler `{scaler_path}` : {e}")
    else:
        st.warning(f"⚠️ Fichier introuvable : `{scaler_path}`")

    return model, scaler


with st.spinner("Chargement des données, du modèle CatBoost et du Scaler..."):
    df_gold = load_gold_data()
    model, scaler = load_ml_pipeline()

if df_gold is not None and not df_gold.empty and model is not None:

    # =========================================================================
    # ÉTAPE 1 : SÉLECTION DU CLIENT ET PRÉPARATION DES FEATURES
    # =========================================================================
    st.subheader("1️⃣ Sélection du Foyer Client")

    customer_list = sorted(df_gold['household_key'].unique())
    selected_household = st.selectbox(
        "🎯 Choisir un Foyer (Household ID) pour exécuter la prédiction :",
        customer_list
    )

    client_row = df_gold[df_gold['household_key'] == selected_household].copy()

    if hasattr(scaler, "feature_names_in_"):
        expected_features = list(scaler.feature_names_in_)
    elif hasattr(model, "feature_names_"):
        expected_features = list(model.feature_names_)
    else:
        expected_features = [
            'recency', 'frequency', 'monetary_total', 'basket_average',
            'retail_disc_total', 'coupon_disc_total', 'promo_ratio', 'unique_departments'
        ]

    if 'promo_ratio' not in client_row.columns:
        if 'retail_disc_total' in client_row.columns and 'monetary_total' in client_row.columns:
            client_row['promo_ratio'] = np.where(
                client_row['monetary_total'] > 0,
                abs(client_row['retail_disc_total']) / client_row['monetary_total'],
                0.0
            )
        else:
            client_row['promo_ratio'] = 0.0

    if 'unique_departments' not in client_row.columns:
        client_row['unique_departments'] = 1.0

    for col in expected_features:
        if col not in client_row.columns:
            client_row[col] = 0.0

    X_client_raw = client_row[expected_features]

    if scaler is not None:
        X_client_scaled = pd.DataFrame(
            scaler.transform(X_client_raw),
            columns=expected_features
        )
    else:
        X_client_scaled = X_client_raw

    # =========================================================================
    # ÉTAPE 2 : PRÉDICTION ET POSITIONNEMENT
    # =========================================================================
    predicted_clv = float(model.predict(X_client_scaled)[0])

    if 'target_clv' in df_gold.columns:
        percentile = (df_gold['target_clv'] < predicted_clv).mean() * 100
    else:
        percentile = (df_gold['monetary_total'] < predicted_clv).mean() * 100

    if percentile >= 85:
        segment_name = "🏆 VIP / Ultra High Value"
        badge_color = "#10B981"
        rec_title = "Programme Rétention VIP & Engagement Dédié"
        rec_action = "Inscrire le foyer au programme VIP prioritaire avec offres exclusives et support dédié."
    elif percentile >= 50:
        segment_name = "💎 Premium / Potentiel Élevé"
        badge_color = "#3B82F6"
        rec_title = "Incentive Panier Moyen & Cross-Selling"
        rec_action = "Envoyer une campagne personnalisée orientée vers les catégories secondaires fréquentes."
    elif client_row['recency'].values[0] > 120:
        segment_name = "🔴 À Risque d'Attrition (Churn)"
        badge_color = "#EF4444"
        rec_title = "Campagne Win-Back d'Urgence"
        rec_action = "Déclencher un coupon de relance ciblé de -20% valable 14 jours pour réactiver l'achat."
    else:
        segment_name = "🟡 Standard / Développement"
        badge_color = "#F59E0B"
        rec_title = "Stratégie d'Activation Régulière"
        rec_action = "Intégrer le client aux communications promotionnelles hebdomadaires standard."

    # =========================================================================
    # RÉSULTATS DU MODÈLE
    # CSS local pour éviter la tronquature du texte sous la métrique k3
    st.markdown("""
        <style>
            [data-testid="stMetricDelta"] {
                font-size: 0.78rem !important;
                white-space: nowrap !important;
            }
        </style>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(label="🔮 CLV Prédite", value=f"{predicted_clv:,.2f} $")

    with k2:
        st.markdown("**🏷️ Segment Client**")
        st.markdown(
            f"<div style='padding:8px; border-radius:6px; background-color:{badge_color}22; border:1px solid {badge_color}; color:{badge_color}; font-weight:bold; text-align:center;'>"
            f"{segment_name}</div>",
            unsafe_allow_html=True
        )

    with k3:
        st.metric(
            label="⚙️ Modèle & Métrique",
            value="CatBoost Regressor",
            delta="RMSE: 277.50$ | R²: 0.522",
            delta_color="normal"
        )

    with k4:
        st.metric(
            label="📊 Positionnement",
            value=f"Top {(100 - percentile):.1f}%",
            help=f"Supérieur à {percentile:.1f}% des clients de la base"
        )

    st.write("")
    st.progress(int(percentile) / 100)

    st.write("")
    st.info(
        f"💡 **Prediction Summary :** Le modèle CatBoost estime une valeur client (CLV) de **{predicted_clv:,.2f} $** pour le foyer **#{selected_household}** "
        f"(positionné dans le **Top {(100 - percentile):.1f}%** du portefeuille). Ce foyer appartient au segment **{segment_name}**. "
        f"Consultez les contributions SHAP ci-dessous pour identifier les drivers de cette prédiction."
    )

    st.markdown("---")

    # =========================================================================
    # SHAP VALUES (TITRE DYNAMIQUE CLAIR/SOMBRE)
    # =========================================================================
    st.subheader("3️⃣ Explicabilité SHAP (Calcul Réel)")
    st.markdown("Analyse des contributions exactes des variables au score via **`shap.TreeExplainer`**.")

    col_shap_graph, col_shap_desc = st.columns([1.4, 1])

    try:
        explainer = shap.TreeExplainer(model)
        shap_values_raw = explainer.shap_values(X_client_scaled)

        if isinstance(shap_values_raw, list):
            shap_vals = shap_values_raw[0][0]
        elif len(shap_values_raw.shape) == 2:
            shap_vals = shap_values_raw[0]
        else:
            shap_vals = shap_values_raw

        if isinstance(explainer.expected_value, (list, np.ndarray)):
            expected_val = float(explainer.expected_value[0])
        else:
            expected_val = float(explainer.expected_value)

        df_shap = pd.DataFrame({
            'Feature': expected_features,
            'Impact': shap_vals
        }).sort_values(by='Impact', key=abs, ascending=False)

        with col_shap_graph:
            waterfall_x = ['Base Value'] + list(df_shap['Feature']) + ['CLV Prédite']
            waterfall_y = [expected_val] + list(df_shap['Impact']) + [predicted_clv]
            measures = ['relative'] + ['relative'] * len(df_shap) + ['total']

            fig_waterfall = go.Figure(go.Waterfall(
                name="SHAP Contributions",
                orientation="v",
                measure=measures,
                x=waterfall_x,
                textposition="outside",
                text=[f"{v:+.1f}$" if i not in [0, len(waterfall_x) - 1] else f"{v:.1f}$" for i, v in
                      enumerate(waterfall_y)],
                textfont=dict(color=graph_text_color, size=12, family="sans-serif"),
                y=waterfall_y,
                connector={"line": {"color": graph_text_color, "dash": "dot", "width": 1}},
                increasing={"marker": {"color": "#10B981"}},
                decreasing={"marker": {"color": "#EF4444"}},
                totals={"marker": {"color": "#3B82F6"}}
            ))

            fig_waterfall.update_layout(
                title=dict(
                    text=f"Waterfall SHAP (Réel) - Foyer {selected_household}",
                    font=dict(color=graph_text_color, size=16)
                ),
                template=plotly_template,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=graph_text_color),
                showlegend=False,
                height=420,
                xaxis=dict(tickangle=-35, showgrid=False, tickfont=dict(color=graph_text_color)),
                yaxis=dict(gridcolor=grid_color, tickfont=dict(color=graph_text_color))
            )
            st.plotly_chart(fig_waterfall, use_container_width=True)

        with col_shap_desc:
            st.markdown("#### 🔍 Principaux Drivers (SHAP)")
            st.write("")

            pos_drivers = df_shap[df_shap['Impact'] > 0]
            neg_drivers = df_shap[df_shap['Impact'] < 0]

            # 🟩 Facteurs Positifs
            st.markdown("**🟩 Facteurs à impact positif :**")
            if not pos_drivers.empty:
                for _, r in pos_drivers.head(3).iterrows():
                    st.write(f"• **{r['Feature']}** : +{r['Impact']:.2f} $")
            else:
                st.write("• Aucun facteur positif majeur.")

            st.write("")

            # 🟥 Facteurs Négatifs
            st.markdown("**🟥 Facteurs à impact négatif :**")
            if not neg_drivers.empty:
                for _, r in neg_drivers.head(3).iterrows():
                    st.write(f"• **{r['Feature']}** : {r['Impact']:.2f} $")
            else:
                st.write("• Aucun facteur négatif majeur.")

            st.write("")

            # 🟦 Score Final / CLV Prédite (Ajouté)
            st.markdown("**🟦 Résultat / CLV Prédite :**")
            st.write(f"• **Score Final (Base + Impacts)** : **{predicted_clv:,.2f} $**")

    except Exception as e:
        st.error(f"Erreur lors du calcul SHAP réel : {e}")

    st.markdown("---")

    # =========================================================================
    # RECOMMANDATION & SYNTHÈSE CRM (CARTES ALIGNÉES HAUTEUR IDENTIQUE)
    # =========================================================================
    col_interp, col_action = st.columns(2)

    recency_val = int(client_row['recency'].values[0])
    freq_val = int(client_row['frequency'].values[0])
    top_feature = df_shap.iloc[0]['Feature'] if 'df_shap' in locals() else 'monetary_total'

    # Carte 4 : Synthèse Décisionnelle
    with col_interp:
        st.subheader("4️⃣ Synthèse Décisionnelle")
        st.markdown(f"""
        <div style="padding: 22px 18px; border-radius: 8px; border-left: 5px solid #6366F1; border-top: 1px solid {card_border}; border-right: 1px solid {card_border}; border-bottom: 1px solid {card_border}; background-color: {card_bg}; min-height: 185px; box-sizing: border-box;">
            <h4 style="margin:0 0 10px 0; color: #6366F1; font-size: 16px;">📊 Diagnostic Client</h4>
            <p style="margin:0 0 6px 0; font-size:14px; color:{select_text_color};"><strong>• Foyer :</strong> Household #{selected_household}</p>
            <p style="margin:0 0 6px 0; font-size:14px; color:{select_text_color};"><strong>• Segment :</strong> {segment_name}</p>
            <p style="margin:0 0 6px 0; font-size:14px; color:{select_text_color};"><strong>• Driver Majeur :</strong> Variabilité portée par <code style='color:{badge_color};'>{top_feature}</code></p>
            <p style="margin:0; font-size:14px; color:{select_text_color};"><strong>• Activité :</strong> {freq_val} achats | Récence : {recency_val} jours</p>
        </div>
        """, unsafe_allow_html=True)

    # Carte 5 : Recommandation CRM (Ajustement du padding pour égaliser la hauteur)
    with col_action:
        st.subheader("5️⃣ Recommandation CRM")
        st.markdown(f"""
        <div style="padding: 22px 18px; border-radius: 8px; border-left: 5px solid {badge_color}; border-top: 1px solid {card_border}; border-right: 1px solid {card_border}; border-bottom: 1px solid {card_border}; background-color: {card_bg}; min-height: 185px; box-sizing: border-box;">
            <h4 style="margin:0 0 10px 0; color: {badge_color}; font-size: 16px;">🎯 {rec_title}</h4>
            <p style="margin:0; font-size: 14px; color: {select_text_color}; line-height:1.6;">{rec_action}</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    if st.button("📋 Exporter la recommandation vers le CRM", use_container_width=True):
        st.success(f"✅ Recommandation générée et prête pour l'export CRM (Foyer #{selected_household}).")

else:
    st.error(
        "Impossible d'exécuter la page : vérifiez que le fichier `models/model_catboost_clv.pkl` est bien présent et valide.")