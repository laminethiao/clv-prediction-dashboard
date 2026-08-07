
import streamlit as st



def apply_custom_theme():
    """
    Gère le thème (Clair / Sombre) et injecte le CSS personnalisé
    sans altérer la structure des boutons et titres.
    """
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'Clair'

    is_dark = st.session_state.theme_mode == 'Sombre'

    if is_dark:
        # --- MODE SOMBRE ---
        css = """
        <style>
            /* Application du fond sombre sur l'application */
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
                background-color: #0E1117 !important; 
                color: #FAFAFA !important; 
            }
            [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] { 
                background-color: #161B22 !important; 
            }

            /* Styles des boutons et barres de navigation */
            [data-testid="stSidebarNavLink"], div.stButton > button, div.stDownloadButton > button {
                background-color: #1E3A8A !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                margin-bottom: 6px !important;
                padding: 8px 12px !important;
                transition: all 0.3s ease !important;
                width: 100% !important;
            }

            [data-testid="stSidebarNavLink"] span, div.stButton > button p, div.stDownloadButton > button p {
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: 14px !important;
            }

            [data-testid="stSidebarNavLink"]:hover, div.stButton > button:hover, div.stDownloadButton > button:hover {
                background-color: #10B981 !important;
                cursor: pointer !important;
            }

            /* Titres et Métriques */
            h1, h2, h3, h4, h5, p, label, .stMetric label { 
                color: #FAFAFA !important; 
            }
            [data-testid="stMetricValue"] { 
                color: #38BDF8 !important; 
            }

            /* Correction ciblée du Selectbox (rechercher un foyer) */
            div[data-baseweb="select"] {
                background-color: #161B22 !important;
                border-radius: 8px !important;
            }
            div[data-baseweb="select"] > div {
                background-color: #161B22 !important;
                color: #FAFAFA !important;
                border-color: #30363D !important;
            }
            div[data-baseweb="select"] span {
                color: #FAFAFA !important;
            }

            /* Expander */
            .streamlit-expanderHeader {
                background-color: #161B22 !important;
                color: #FAFAFA !important;
                border-radius: 8px;
            }
        </style>
        """

        plotly_template = "plotly_dark"
        text_color = "#FAFAFA"



    else:
        # --- MODE CLAIR ---
        css = """
        <style>
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
                background-color: #FFFFFF !important; 
                color: #0F172A !important; 
            }
            [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] { 
                background-color: #F8FAFC !important; 
            }

            [data-testid="stSidebarNavLink"], div.stButton > button, div.stDownloadButton > button {
                background-color: #1E3A8A !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                margin-bottom: 6px !important;
                padding: 8px 12px !important;
                transition: all 0.3s ease !important;
                width: 100% !important;
            }

            [data-testid="stSidebarNavLink"] span, div.stButton > button p, div.stDownloadButton > button p {
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: 14px !important;
            }

            [data-testid="stSidebarNavLink"]:hover, div.stButton > button:hover, div.stDownloadButton > button:hover {
                background-color: #10B981 !important;
                cursor: pointer !important;
            }

            [data-testid="stSidebarNavLink"][aria-current="page"] {
                background-color: #2563EB !important;
                border-left: 5px solid #10B981 !important;
            }

            h1, h2, h3, h4, h5, p, label, .stMetric label { 
                color: #0F172A !important; 
            }
            [data-testid="stMetricValue"] { 
                color: #1E3A8A !important; 
            }

            div[data-baseweb="select"] > div {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                border-color: #CBD5E1 !important;
            }

            .streamlit-expanderHeader {
                background-color: #F1F5F9 !important;
                color: #0F172A !important;
                border-radius: 8px;
            }
        </style>
        """
        plotly_template = "plotly_white"
        text_color = "#0F172A"

    st.markdown(css, unsafe_allow_html=True)

    # Bouton de bascule en bas de sidebar
    for _ in range(7):
        st.sidebar.write("")

    st.sidebar.markdown("---")

    label_bouton = "☀️ Passer au Mode Clair" if is_dark else "🌙 Passer au Mode Sombre"
    if st.sidebar.button(label_bouton, use_container_width=True):
        st.session_state.theme_mode = 'Sombre' if st.session_state.theme_mode == 'Clair' else 'Clair'

    return is_dark, plotly_template, text_color