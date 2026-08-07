import streamlit as st
import pandas as pd
import pickle
import os


# 1. Chargement des modèles et scalers
@st.cache_resource
def load_ml_assets():
    """Charge le modèle CatBoost et le StandardScaler depuis le dossier models/"""
    model_path = os.path.join("models", "model_catboost_clv.pkl")
    scaler_path = os.path.join("models", "scaler_clv.pkl")

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    return model, scaler


# 2. Chargement des transactions brutes (Silver)
@st.cache_data
def load_parquet_data():
    """Charge le fichier fact_transactions_silver.parquet depuis le dossier data/"""
    # Note : Ajout du 's' à transactions pour correspondre à ton fichier réel
    file_path = os.path.join("data", "fact_transactions_silver.parquet")
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    else:
        st.warning(f"Fichier {file_path} introuvable.")
        return None


# 3. Chargement de la table agrégée par client (Gold)
@st.cache_data
def load_gold_data():
    """Charge la table client agrégée df_gold (1).parquet depuis le dossier data/"""
    # Note : Correspondance avec ton nom exact détecté par le diagnostic
    file_path = os.path.join("data", "df_gold (1).parquet")
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)

        # Nettoyage des colonnes doublons à la volée pour que l'application reste propre
        # On ne garde que les versions finales sans suffixe
        cols_to_drop = [c for c in df.columns if c.endswith('_x') or c.endswith('_y')]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        return df
    else:
        st.warning(f"Fichier {file_path} introuvable.")
        return None