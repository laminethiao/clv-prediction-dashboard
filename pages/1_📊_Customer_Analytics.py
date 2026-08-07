import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg

from utils.auth import check_authentication, display_user_info
from utils.data_loader import load_parquet_data, load_gold_data
from utils.ui_style import apply_custom_theme

# Configuration de la page
st.set_page_config(
    page_title="Customer Analytics & CRM",
    page_icon="📊",
    layout="wide"
)
check_authentication()

# Application du thème global
is_dark, plotly_template, text_color = apply_custom_theme()

# Affichage des infos utilisateur et déconnexion dans la sidebar
with st.sidebar:
    st.markdown("---")
    display_user_info()

# -----------------------------------------------------------------------------
# DÉFINITION STRICTE DES COULEURSselon le THÈME (CLAIR VS SOMBRE)
# -----------------------------------------------------------------------------
if is_dark:
    select_text_color = "#F8FAFC"
    bg_select = "#1E293B"
    border_select = "#334155"
    graph_text_color = "#F8FAFC"
    # Thème Dark propre pour les cartes et tableaux
    table_bg = "#161B22"
    table_text = "#FAFAFA"
    table_border = "#30363D"
else:
    select_text_color = "#0F172A"
    bg_select = "#FFFFFF"
    border_select = "#CBD5E1"
    graph_text_color = "#0F172A"
    # Thème Clair propre pour les cartes et tableaux
    table_bg = "#FFFFFF"
    table_text = "#0F172A"
    table_border = "#E2E8F0"

# Injection CSS dynamique pour le Selectbox (Recherche de Foyer)
st.markdown(f"""
    <style>
        /* Selectbox principal */
        div[data-baseweb="select"] > div {{
            background-color: {bg_select} !important;
            color: {select_text_color} !important;
            border: 1px solid {border_select} !important;
        }}
        div[data-baseweb="select"] * {{
            color: {select_text_color} !important;
        }}
        /* Menu déroulant */
        div[data-baseweb="popover"] ul {{
            background-color: {bg_select} !important;
        }}
        div[data-baseweb="popover"] ul li {{
            color: {select_text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("📊 CRM & Customer Analytics 360°")
st.markdown("Plateforme décisionnelle d'analyse comportementale des foyers et de pilotage CRM.")
st.markdown("---")

with st.spinner("Chargement de la base de données CRM..."):
    df_silver = load_parquet_data()
    df_gold = load_gold_data()

if df_silver is not None and df_gold is not None:

    tab_overview, tab_explorer = st.tabs(["🏢 Vue Macro & Ventes", "🔍 Customer Explorer 360°"])

    # =========================================================================
    # ONGLET 1 : VUE MACRO & ANALYSE COMMERCIALE (BUSINESS OVERVIEW)
    # =========================================================================
    with tab_overview:
        st.markdown("### 📈 Executive KPIs")

        total_revenue = df_silver['sales_value'].sum() if 'sales_value' in df_silver.columns else df_silver['SALES_VALUE'].sum() if 'SALES_VALUE' in df_silver.columns else 0
        total_transactions = df_silver['basket_id'].nunique() if 'basket_id' in df_silver.columns else len(df_silver)
        unique_customers = df_gold['household_key'].nunique()
        basket_avg = total_revenue / total_transactions if total_transactions > 0 else 0

        avg_clv = df_gold['target_clv'].mean() if 'target_clv' in df_gold.columns else df_gold['monetary_total'].mean()
        high_value_cust = (df_gold['monetary_total'] > df_gold['monetary_total'].quantile(0.80)).sum()
        avg_recency = df_gold['recency'].mean()

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1:
            st.metric("Chiffre d'Affaires", f"{total_revenue:,.0f} $")
        with k2:
            st.metric("Clients Uniques", f"{unique_customers:,}")
        with k3:
            st.metric("Clients High Value", f"{high_value_cust:,}")
        with k4:
            st.metric("Panier Moyen", f"{basket_avg:.2f} $")
        with k5:
            st.metric("CLV Moyenne Prédite", f"{avg_clv:,.2f} $")
        with k6:
            st.metric("Récence Moyenne", f"{int(avg_recency)} jours")

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("### 🛒 Top 8 Départements les plus Rentables")
            dept_col = 'department' if 'department' in df_silver.columns else 'DEPARTMENT' if 'DEPARTMENT' in df_silver.columns else None
            val_col = 'sales_value' if 'sales_value' in df_silver.columns else 'SALES_VALUE'

            if dept_col:
                top_depts = df_silver.groupby(dept_col)[val_col].sum().reset_index().sort_values(by=val_col, ascending=False).head(8)
                fig_depts = px.bar(
                    top_depts, x=val_col, y=dept_col, orientation='h',
                    color=val_col, color_continuous_scale="Blues" if not is_dark else "Viridis",
                    template=plotly_template
                )
                fig_depts.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=graph_text_color),
                    xaxis=dict(tickfont=dict(color=graph_text_color), title=dict(font=dict(color=graph_text_color))),
                    yaxis=dict(categoryorder='total ascending', tickfont=dict(color=graph_text_color), title=dict(font=dict(color=graph_text_color))),
                    showlegend=False
                )
                st.plotly_chart(fig_depts, use_container_width=True)
            else:
                st.info("Données de départements indisponibles dans Silver.")

        with col_right:
            st.markdown("### 💰 Répartition de la Valeur Client (Segmentation CA)")
            df_gold['Segment_CA'] = pd.qcut(df_gold['monetary_total'], q=4, labels=['1. Faible', '2. Moyen-', '3. Moyen+', '4. Élevé'])
            ca_split = df_gold.groupby('Segment_CA', observed=False)['monetary_total'].sum().reset_index()

            fig_pie = px.pie(
                ca_split, values='monetary_total', names='Segment_CA',
                color_discrete_sequence=px.colors.sequential.Darkmint if is_dark else px.colors.sequential.Blues,
                template=plotly_template, hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=graph_text_color),
                legend=dict(font=dict(color=graph_text_color))
            )
            fig_pie.update_traces(textfont=dict(color=graph_text_color))
            st.plotly_chart(fig_pie, use_container_width=True)

    # =========================================================================
    # ONGLET 2 : CUSTOMER EXPLORER 360° (FICHE INDIVIDUELLE CRM)
    # =========================================================================
    with tab_explorer:
        st.markdown("### 🔍 Customer Explorer & Profiling CRM")

        customer_list = sorted(df_gold['household_key'].unique())
        selected_household = st.selectbox("🎯 Rechercher un Foyer (Household ID) :", customer_list)

        client_data = df_gold[df_gold['household_key'] == selected_household].iloc[0]

        c_monetary = client_data.get('monetary_total', 0)
        c_freq = client_data.get('frequency', 0)
        c_recency = client_data.get('recency', 0)
        c_basket = client_data.get('basket_average', 0)
        c_promo = client_data.get('promo_ratio', 0) * 100

        avg_monetary = df_gold['monetary_total'].mean()
        avg_freq = df_gold['frequency'].mean()
        avg_basket = df_gold['basket_average'].mean()
        avg_recency_global = df_gold['recency'].mean()
        avg_promo = df_gold['promo_ratio'].mean() * 100

        delta_monetary = ((c_monetary - avg_monetary) / avg_monetary) * 100 if avg_monetary > 0 else 0
        delta_freq = ((c_freq - avg_freq) / avg_freq) * 100 if avg_freq > 0 else 0
        delta_basket = ((c_basket - avg_basket) / avg_basket) * 100 if avg_basket > 0 else 0
        delta_recency = c_recency - avg_recency_global

        pct_monetary = (df_gold['monetary_total'] < c_monetary).mean() * 100

        if pct_monetary >= 80:
            badge_label = "🏆 CLIENT VIP PREMIUM"
            badge_color = "#10B981"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            priority_label = "HAUTE (Rétention VIP)"
            action_list = ["✓ Programme de fidélité dédié", "✓ Service client prioritaire", "✓ Offres exclusives sur-mesure"]
        elif c_recency > 180:
            badge_label = "🔴 CLIENT A RISQUE (INACTIF)"
            badge_color = "#EF4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
            priority_label = "HAUTE (Réactivation URGENTE)"
            action_list = ["✓ Envoi d'un coupon de relance (-20%)", "✓ Enquête de satisfaction client", "✓ Campagne d'emailing ciblée"]
        elif pct_monetary >= 40:
            badge_label = "🔵 CLIENT REGULIER ETABLI"
            badge_color = "#3B82F6"
            badge_bg = "rgba(59, 130, 246, 0.15)"
            priority_label = "MOYENNE (Cross-selling)"
            action_list = ["✓ Recommandation de nouveaux départements", "✓ Programme d'incentive panier moyen"]
        else:
            badge_label = "🟡 CLIENT OCCASIONNEL / POTENTIEL"
            badge_color = "#F59E0B"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            priority_label = "BASSE (Activation)"
            action_list = ["✓ Offres découvertes sur catégories phares", "✓ Relances sur promotions hebdomadaires"]

        st.markdown("---")

        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; border: 2px solid {badge_color}; background-color: {badge_bg}; margin-bottom: 20px;">
            <h3 style="margin: 0; color: {badge_color};">Foyer N° {selected_household} — <span style="font-weight: bold;">{badge_label}</span></h3>
        </div>
        """, unsafe_allow_html=True)

        b1, b2, b3, b4, b5 = st.columns(5)
        with b1:
            st.metric("Dépense Totale", f"{c_monetary:,.2f} $", delta=f"{delta_monetary:+.1f}% vs Cohorte")
        with b2:
            st.metric("Nb de Visites", f"{int(c_freq)}", delta=f"{delta_freq:+.1f}% vs Cohorte")
        with b3:
            st.metric("Panier Moyen", f"{c_basket:.2f} $", delta=f"{delta_basket:+.1f}% vs Cohorte")
        with b4:
            st.metric("Dernier Achat", f"{int(c_recency)} jours", delta=f"{delta_recency:+.0f} j vs Cohorte", delta_color="inverse")
        with b5:
            st.metric("Part Promotion", f"{c_promo:.1f} %", delta=f"Moy: {avg_promo:.1f}%")

        st.markdown("---")

        col_hist, col_radar = st.columns([1.2, 1])

        # Récupération sécurisée du sous-ensemble client
        hk_col = next((c for c in df_silver.columns if c.lower() == 'household_key'), None)
        time_col = next((c for c in df_silver.columns if c.lower() in ['day', 'transaction_date', 'week_no', 'date']), None)
        val_col_tx = next((c for c in df_silver.columns if c.lower() in ['sales_value', 'amount', 'price']), None)

        df_client_tx = df_silver[df_silver[hk_col] == selected_household] if hk_col else pd.DataFrame()

        with col_hist:
            st.markdown("#### 📅 Historique Temporel des Achats")
            if hk_col and time_col and val_col_tx and not df_client_tx.empty:
                tx_timeline = df_client_tx.groupby(time_col)[val_col_tx].sum().reset_index().sort_values(by=time_col)

                fig_line = px.line(
                    tx_timeline, x=time_col, y=val_col_tx,
                    labels={time_col: 'Chronologie (Jours)', val_col_tx: 'Montant Dépensé ($)'},
                    title=f"Évolution des dépenses ({len(df_client_tx)} transactions)",
                    template=plotly_template
                )
                fig_line.update_traces(line_color=badge_color, line_width=2.5)
                fig_line.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=graph_text_color),
                    title=dict(font=dict(color=graph_text_color)),
                    xaxis=dict(tickfont=dict(color=graph_text_color), title=dict(font=dict(color=graph_text_color))),
                    yaxis=dict(tickfont=dict(color=graph_text_color), title=dict(font=dict(color=graph_text_color)))
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info(f"Aucune transaction chronologique disponible pour le foyer N° {selected_household}.")

        with col_radar:
            st.markdown("#### 🎯 Profil Comportemental (vs Base Globale)")
            features_radar = ['frequency', 'monetary_total', 'basket_average', 'unique_departments']
            valid_features = [f for f in features_radar if f in df_gold.columns]

            client_values, avg_values = [], []
            for feat in valid_features:
                min_v, max_v, mean_v = df_gold[feat].min(), df_gold[feat].max(), df_gold[feat].mean()
                norm_c = ((client_data[feat] - min_v) / (max_v - min_v)) * 100 if max_v > min_v else 50
                norm_a = ((mean_v - min_v) / (max_v - min_v)) * 100 if max_v > min_v else 50
                client_values.append(norm_c)
                avg_values.append(norm_a)

            valid_features_display = [f.replace('_', ' ').title() for f in valid_features]

            fig_radar = gg.Figure()
            fig_radar.add_trace(gg.Scatterpolar(r=client_values, theta=valid_features_display, fill='toself',
                                                name=f'Foyer {selected_household}', line_color=badge_color))
            fig_radar.add_trace(gg.Scatterpolar(r=avg_values, theta=valid_features_display, fill='toself', name='Moyenne Globale',
                                line_color='#9CA3AF'))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color=graph_text_color)),
                    angularaxis=dict(tickfont=dict(color=graph_text_color))
                ),
                legend=dict(font=dict(color=graph_text_color)),
                showlegend=True,
                template=plotly_template,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=graph_text_color),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        col_story, col_action = st.columns([1.3, 1])

        with col_story:
            st.markdown("#### 📄 Rapport Exécutif d'Analyse Client")
            story_text = f"""
            **Diagnostic Synthétique :**  
            Le foyer **{selected_household}** se classe parmi les **Top {100 - int(pct_monetary)}%** des clients les plus rentables avec une dépense de **{c_monetary:,.2f} $** ({delta_monetary:+.1f}% vs cohorte). 

            Son panier moyen s'élève à **{c_basket:.2f} $** pour **{int(c_freq)} commandes**. Sa sensibilité aux promotions s'établit à **{c_promo:.1f}%**.
            """
            st.info(story_text)

        with col_action:
            st.markdown("#### 🎯 Recommandation & Actions Prioritaires")
            st.markdown(f"**Priorité d'Action :** `{priority_label}`")
            for act in action_list:
                st.write(act)

        st.markdown("---")

        # 4. EXPORTATEUR DE DONNÉES BRUTES ET FILTRE DÉTAILLÉ
        with st.expander(f"📋 Consulter & Exporter l'historique brut du Foyer {selected_household}"):
            if not df_client_tx.empty:
                st.markdown(f"**Total de {len(df_client_tx)} lignes d'achats enregistrées :**")

                # Style du tableau avec le fond d'origine du thème (#161B22 pour dark, #FFFFFF pour clair)
                styled_df = df_client_tx.style.set_properties(**{
                    'background-color': table_bg,
                    'color': table_text,
                    'border-color': table_border
                }).set_table_styles([
                    {'selector': 'th', 'props': [('background-color', table_bg), ('color', table_text), ('font-weight', 'bold')]}
                ])

                st.dataframe(styled_df, use_container_width=True, height=250, hide_index=True)

                # Bouton de téléchargement CSV
                csv_data = df_client_tx.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Télécharger les données du Foyer {selected_household} (CSV)",
                    data=csv_data,
                    file_name=f"foyer_{selected_household}_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("Aucune transaction brute disponible à exporter pour ce foyer.")
else:
    st.error("Erreur lors du chargement des fichiers de la base de données CRM.")