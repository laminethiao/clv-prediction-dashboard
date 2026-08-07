import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.auth import check_authentication, display_user_info
from utils.data_loader import load_gold_data
from utils.ui_style import apply_custom_theme

# -----------------------------------------------------------------------------
# CONFIGURATION & THÈME DYNAMIQUE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Segmentation & Strategic Insights",
    page_icon="📊",
    layout="wide"
)
check_authentication()

# Applique le thème centralisé
is_dark, plotly_template, default_text_color = apply_custom_theme()
display_user_info()

# Styles dynamiques selon le thème actif
# Styles dynamiques selon le thème actif
if is_dark:
    # Couleurs du thème sombre
    bg_main = "#0E1117"
    bg_card = "#262730"
    card_border = "#31333F"
    text_color = "#FAFAFA"

    insight_bg = "rgba(99, 102, 241, 0.15)"
    insight_border = "#6366F1"
    action_bg = "rgba(16, 185, 129, 0.15)"
    action_border = "#10B981"

    # Tableau Plotly (Mode Sombre)
    tbl_header_bg = "#1E293B"      # Entête sombre élégante
    tbl_row_bg = bg_main
    tbl_header_text = "#FAFAFA"    # Texte entête blanc
    tbl_text_color = text_color
    tbl_border_color = card_border
    bg_select = bg_card
    border_select = card_border
else:
    bg_main = "#FFFFFF"
    bg_card = "#F0F2F6"
    card_border = "#E2E8F0"
    text_color = "#1E293B"

    insight_bg = "#EEF2FF"
    insight_border = "#6366F1"
    action_bg = "#ECFDF5"
    action_border = "#10B981"

    # Tableau Plotly (Mode Clair) 👇
    tbl_header_bg = "#F8FAFC"      # Blanc très clair / Blanc cassé
    tbl_row_bg = "#FFFFFF"         # Fond des cellules blanc pur
    tbl_header_text = "#0F172A"    # Texte entête sombre (lisible sur fond blanc)
    tbl_text_color = "#0F172A"     # Texte des cellules sombre
    tbl_border_color = "#E2E8F0"   # Bordures légères
    bg_select = "#FFFFFF"
    border_select = "#CBD5E1"

# -----------------------------------------------------------------------------
# INJECTION CSS DYNAMIQUE (DÉROULANTS / SELECTBOX)
# -----------------------------------------------------------------------------
st.markdown(f"""
    <style>
        /* Menus déroulants (st.selectbox) */
        div[data-baseweb="select"] > div {{
            background-color: {bg_select} !important;
            color: {tbl_text_color} !important;
            border: 1px solid {border_select} !important;
        }}
        div[data-baseweb="select"] * {{
            color: {tbl_text_color} !important;
        }}
        div[data-baseweb="popover"] ul {{
            background-color: {bg_select} !important;
        }}
        div[data-baseweb="popover"] ul li {{
            color: {tbl_text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FONCTION HELPER : RENDU DE TABLEAU COMPATIBLE THÈME
# -----------------------------------------------------------------------------
def render_styled_table(df, headers=None, height=300):
    """Génère un tableau Plotly parfaitement aligné sur le thème actif."""
    if headers is None:
        headers = list(df.columns)

    columns_data = [df[col].tolist() for col in df.columns]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in headers],
            fill_color=tbl_header_bg,             # Fond blanc / très proche du blanc en mode clair
            align='left',
            font=dict(color=tbl_header_text, size=13), # Couleur du texte d'entête adaptée
            line_color=tbl_border_color,
            height=36
        ),
        cells=dict(
            values=columns_data,
            fill_color=tbl_row_bg,
            align='left',
            font=dict(color=tbl_text_color, size=12),
            line_color=tbl_border_color,
            height=30
        )
    )])

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height
    )
    return fig

st.title("📊 Segmentation Clients & Insights Stratégiques")
st.markdown("Analyse prescriptive du portefeuille client, profilage RFM et leviers de croissance CRM.")
st.markdown("---")

df_gold = load_gold_data()

if df_gold is not None and not df_gold.empty:

    # -------------------------------------------------------------------------
    # SEGMENTATION
    # -------------------------------------------------------------------------
    def assign_segment(row):
        monetary = row.get('monetary_total', 0)
        recency = row.get('recency', 0)
        if monetary >= 3000:
            return "🏆 VIP / Ultra High Value"
        elif monetary >= 1200:
            return "💎 Premium / Potentiel"
        elif recency > 120:
            return "🔴 À Risque (Churn)"
        else:
            return "🟡 Standard / Régulier"


    if 'segment' not in df_gold.columns:
        df_gold['segment'] = df_gold.apply(assign_segment, axis=1)

    unique_segments = sorted(list(df_gold['segment'].unique()))
    set2_palette = px.colors.qualitative.Set2
    segment_colors = {seg: set2_palette[i % len(set2_palette)] for i, seg in enumerate(unique_segments)}

    # -------------------------------------------------------------------------
    # 1️⃣ VUE GLOBALE
    # -------------------------------------------------------------------------
    st.subheader("1️⃣ Vue Globale du Portefeuille Client")

    total_customers = len(df_gold)
    total_revenue = df_gold['monetary_total'].sum() if 'monetary_total' in df_gold else 0

    c1, c2 = st.columns(2)

    with c1:
        segment_counts = df_gold['segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Foyers']

        fig_donut = px.pie(
            segment_counts,
            values='Foyers',
            names='Segment',
            hole=0.45,
            title="Répartition du Volume de Clients (%)",
            template=plotly_template,
            color='Segment',
            color_discrete_map=segment_colors
        )
        fig_donut.update_traces(
            textinfo='percent+label',
            insidetextfont=dict(color="#FFFFFF", size=12),
            outsidetextfont=dict(color=text_color, size=12)
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=16)),

            legend=dict(
                font=dict(color=text_color, size=12)
            )
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        segment_metrics = df_gold.groupby('segment').agg(
            total_revenue=('monetary_total', 'sum'),
            customer_count=('household_key', 'count')
        ).reset_index()
        segment_metrics['revenue_share'] = (segment_metrics['total_revenue'] / max(total_revenue, 1)) * 100
        segment_metrics = segment_metrics.sort_values(by='total_revenue', ascending=False)

        fig_revenue = px.bar(
            segment_metrics,
            x='segment',
            y='total_revenue',
            orientation='v',
            color='segment',
            color_discrete_map=segment_colors,
            text=segment_metrics['total_revenue'].apply(lambda x: f"{x:,.0f} $"),
            title="Chiffre d'Affaires Généré par Segment ($) ",
            labels={'total_revenue': 'CA Total ($)', 'segment': 'Segment'},
            template=plotly_template
        )
        fig_revenue.update_traces(
            textposition='outside',
            textfont=dict(color=text_color, size=12, family="Arial Black, sans-serif"),
            hovertemplate="<b>%{x}</b><br>CA Total : %{y:,.2f} $<br>Part du CA : %{customdata[0]:.1f}%<extra></extra>",
            customdata=segment_metrics[['revenue_share']]
        )
        fig_revenue.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=16)),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                tickfont=dict(color=text_color),
                title=dict(font=dict(color=text_color))
            ),
            xaxis=dict(
                title="",
                tickfont=dict(color=text_color)
            )
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2️⃣ DRILL-DOWN PAR SEGMENT
    # -------------------------------------------------------------------------
    st.subheader("2️⃣ Zoom & Profilage Dynamique par Segment")

    selected_segment = st.selectbox(
        "🔍 Choisissez un segment à analyser :",
        options=["Tous les segments"] + unique_segments
    )

    if selected_segment == "Tous les segments":
        df_filtered = df_gold.copy()
    else:
        df_filtered = df_gold[df_gold['segment'] == selected_segment]

    seg_customers = len(df_filtered)
    seg_revenue = df_filtered['monetary_total'].sum() if 'monetary_total' in df_filtered else 0
    seg_basket = df_filtered['basket_average'].mean() if 'basket_average' in df_filtered else 0
    seg_recency = df_filtered['recency'].mean() if 'recency' in df_filtered else 0
    seg_frequency = df_filtered['frequency'].mean() if 'frequency' in df_filtered else 0
    seg_promo = (df_filtered['promo_ratio'].mean() * 100) if 'promo_ratio' in df_filtered else 0

    pct_customers = (seg_customers / max(total_customers, 1)) * 100
    pct_revenue = (seg_revenue / max(total_revenue, 1)) * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Foyers Ciblés", f"{seg_customers:,}", delta=f"{pct_customers:.1f}% de la base")
    k2.metric("💰 CA Généré", f"{seg_revenue:,.2f} $", delta=f"{pct_revenue:.1f}% du CA global")
    k3.metric("🧺 Panier Moyen", f"{seg_basket:,.2f} $")
    k4.metric("⏱️ Récence Moyenne", f"{seg_recency:.0f} jours")

    st.write("")

    col_profile, col_cards = st.columns([1, 1.5])

    with col_profile:
        st.markdown("##### 📌 Profil Moyen du Segment")
        profile_data = pd.DataFrame({
            "Métrique RFM": [
                "Valeur Totale Moy. (Monetary)",
                "Fréquence D'achat (Achats)",
                "Récence D'achat (Jours)",
                "Panier Moyen ($)",
                "Sensibilité Promo (%)"
            ],
            "Valeur Moyenne": [
                f"{seg_revenue / max(seg_customers, 1):,.2f} $",
                f"{seg_frequency:.1f} visites",
                f"{seg_recency:.0f} jours",
                f"{seg_basket:,.2f} $",
                f"{seg_promo:.1f} %"
            ]
        })

        # Rendu du tableau dynamiquement adapté au thème
        fig_profile_tbl = render_styled_table(profile_data, height=220)
        st.plotly_chart(fig_profile_tbl, use_container_width=True)

    with col_cards:

        if selected_segment == "🏆 VIP / Ultra High Value":
            dynamic_insight = (
                f"Les clients **VIP** représentent seulement **{pct_customers:.1f}%** de votre portefeuille "
                f"mais génèrent **{pct_revenue:.1f}%** du chiffre d'affaires. "
                "Ils constituent le principal moteur de rentabilité de l'entreprise et leur fidélisation "
                "a un impact direct sur les revenus."
            )

            dynamic_action = (
                "Déployer un **programme de fidélisation Premium** (conciergerie, avantages exclusifs, "
                "livraison prioritaire, invitations privées et offres personnalisées) afin de maximiser "
                "la rétention et d'augmenter leur Customer Lifetime Value (CLV)."
            )

        elif selected_segment == "💎 Premium / Potentiel":
            dynamic_insight = (
                f"Ce segment regroupe **{seg_customers} foyers** présentant un fort potentiel de croissance "
                f"avec un panier moyen de **{seg_basket:,.2f} $**. "
                "Ces clients disposent d'une valeur élevée mais peuvent encore augmenter leur fréquence d'achat."
            )

            dynamic_action = (
                "Mettre en place des campagnes de **Cross-Selling** et **Up-Selling**, "
                "des programmes de fidélité progressifs et des recommandations personnalisées "
                "pour accélérer leur montée vers le segment VIP."
            )

        elif selected_segment == "🔴 À Risque (Churn)":
            dynamic_insight = (
                f"**{seg_customers} clients** présentent une récence moyenne de **{seg_recency:.0f} jours**, "
                f"ce qui expose un chiffre d'affaires historique de **{seg_revenue:,.2f} $** à un risque de perte. "
                "Ce segment nécessite une intervention rapide afin de limiter l'attrition."
            )

            dynamic_action = (
                "Déclencher automatiquement une **campagne de réactivation (Win-Back)** "
                "avec des offres personnalisées, des coupons temporaires et un suivi CRM "
                "pour encourager un nouvel achat."
            )

        elif selected_segment == "🟡 Standard / Régulier":
            dynamic_insight = (
                f"Les clients Standard représentent **{pct_customers:.1f}%** de la base client. "
                "Ils constituent le principal volume d'activité et assurent une part importante des ventes récurrentes."
            )

            dynamic_action = (
                "Développer des campagnes d'**Up-Selling**, des offres packagées et des récompenses "
                "de fidélité afin d'augmenter progressivement leur panier moyen et leur fréquence d'achat."
            )

        else:
            dynamic_insight = (
                f"Le portefeuille est composé de **{total_customers:,} foyers** générant "
                f"un chiffre d'affaires total de **{total_revenue:,.2f} $**. "
                "Chaque segment présente un comportement d'achat différent nécessitant une stratégie CRM adaptée."
            )

            dynamic_action = (
                "Sélectionnez un segment spécifique afin d'obtenir un diagnostic métier détaillé "
                "ainsi que des recommandations opérationnelles personnalisées."
            )

        st.markdown(f"""
            <div style="padding:14px; border-radius:8px; background-color:{insight_bg}; border-left:5px solid {insight_border}; border:1px solid {card_border}; margin-bottom:12px;">
                <h5 style="margin:0 0 6px 0; color:{insight_border}; font-size:14px;">💡 Diagnostic Métier</h5>
                <p style="margin:0; font-size:13px; color:{text_color}; line-height:1.4;">{dynamic_insight}</p>
            </div>
            <div style="padding:14px; border-radius:8px; background-color:{action_bg}; border-left:5px solid {action_border}; border:1px solid {card_border};">
                <h5 style="margin:0 0 6px 0; color:{action_border}; font-size:14px;">🎯 Plan d'Action Recommandé</h5>
                <p style="margin:0; font-size:13px; color:{text_color}; line-height:1.4;">{dynamic_action}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # -------------------------------------------------------------------------
    # TOP 20 & EXPORTATION DÉDIÉE
    # -------------------------------------------------------------------------
    st.markdown("#### 🏆 Top 20 Clients du Segment — *Triés par Valeur Dépensée*")

    rfm_cols = [c for c in ['household_key', 'monetary_total', 'recency', 'frequency', 'basket_average', 'promo_ratio']
                if c in df_filtered.columns]

    if rfm_cols:
        df_top20 = df_filtered.sort_values(by='monetary_total', ascending=False).head(20).copy()

        # Préparation du dataframe formaté pour affichage
        df_display = pd.DataFrame()
        if 'household_key' in df_top20:
            df_display['ID Foyer / Client'] = df_top20['household_key'].astype(str)
        if 'monetary_total' in df_top20:
            df_display['Valeur Totale ($)'] = df_top20['monetary_total'].apply(lambda x: f"$ {x:,.2f}")
        if 'recency' in df_top20:
            df_display['Récence (Jours)'] = df_top20['recency'].apply(lambda x: f"{x:.0f} j")
        if 'frequency' in df_top20:
            df_display['Fréquence (Achats)'] = df_top20['frequency'].apply(lambda x: f"{x:.0f}")
        if 'basket_average' in df_top20:
            df_display['Panier Moyen ($)'] = df_top20['basket_average'].apply(lambda x: f"$ {x:,.2f}")
        if 'promo_ratio' in df_top20:
            df_display['Part Promo (%)'] = df_top20['promo_ratio'].apply(lambda x: f"{x * 100:.1f} %")

        # Rendu du tableau Plotly
        fig_top20_tbl = render_styled_table(df_display, height=350)
        st.plotly_chart(fig_top20_tbl, use_container_width=True)

        btn_col1, _ = st.columns([1, 1])
        with btn_col1:
            top20_csv = df_top20[rfm_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le Top 20 (CSV)",
                data=top20_csv,
                file_name=f"top20_clients_{selected_segment.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Accordéon pour la liste complète
    with st.expander(f"👁️ Voir la liste complète des {len(df_filtered)} clients de ce segment"):
        df_full = df_filtered.sort_values(by='monetary_total', ascending=False).copy()

        df_full_display = pd.DataFrame()
        if 'household_key' in df_full:
            df_full_display['ID Foyer / Client'] = df_full['household_key'].astype(str)
        if 'monetary_total' in df_full:
            df_full_display['Valeur Totale ($)'] = df_full['monetary_total'].apply(lambda x: f"$ {x:,.2f}")
        if 'recency' in df_full:
            df_full_display['Récence (Jours)'] = df_full['recency'].apply(lambda x: f"{x:.0f} j")
        if 'frequency' in df_full:
            df_full_display['Fréquence (Achats)'] = df_full['frequency'].apply(lambda x: f"{x:.0f}")
        if 'basket_average' in df_full:
            df_full_display['Panier Moyen ($)'] = df_full['basket_average'].apply(lambda x: f"$ {x:,.2f}")
        if 'promo_ratio' in df_full:
            df_full_display['Part Promo (%)'] = df_full['promo_ratio'].apply(lambda x: f"{x * 100:.1f} %")

        fig_full_tbl = render_styled_table(df_full_display, height=400)
        st.plotly_chart(fig_full_tbl, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 3️⃣ EXPORTATION GLOBAL CRM
    # -------------------------------------------------------------------------
    st.subheader("3️⃣ Exporter l'intégralité du segment pour Campagnes CRM")

    col_exp1, col_exp2 = st.columns([1, 1])

    with col_exp1:
        st.write(
            f"📥 Exporter les **{len(df_filtered)} clients** du segment sélectionné vers vos outils d'activation (Klaviyo, Salesforce, Braze)."
        )

    with col_exp2:
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        export_filename = f"export_crm_global_{selected_segment.replace(' ', '_')}.csv"

        st.download_button(
            label="📥 Télécharger TOUS les clients du segment (CSV)",
            data=csv_data,
            file_name=export_filename,
            mime="text/csv",
            use_container_width=True
        )

else:
    st.error("Aucune donnée disponible dans la couche Gold.")