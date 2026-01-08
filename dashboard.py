import streamlit as st
import json
import time
import os
import pandas as pd
from PIL import Image

# Config de la page
st.set_page_config(
    page_title="PwnIA Command Center",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style Hacker (CSS)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; font-family: 'Courier New'; }
    .stMetricValue { color: #ff3333 !important; }
    div[data-testid="stMetricLabel"] { color: #00ff41 !important; }
    .css-1d391kg { background-color: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

st.title("💀 PwnIA : AUTONOMOUS C2 SERVER")

# Fonction de chargement des données
def load_data():
    try:
        with open("mission_state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

# Placeholder pour l'auto-refresh
placeholder = st.empty()

while True:
    data = load_data()
    
    with placeholder.container():
        if not data:
            st.warning("⚠️ En attente de l'agent PwnIA... (Lancez le script python)")
        else:
            # --- Ligne 1 : Métriques Clés ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("CIBLE", data.get("target_ip", "N/A"))
            col2.metric("STATUS", data.get("status", "IDLE"))
            col3.metric("PORTS OUVERTS", len(data.get("ports_open", [])))
            col4.metric("VULNÉRABILITÉS", len(data.get("confirmed_vulnerabilities", [])))

            st.markdown("---")

            # --- Ligne 2 : Détails & Vision ---
            c1, c2 = st.columns([1, 1])

            with c1:
                st.subheader("📡 Services & Ports")
                services = data.get("identified_services", {})
                if services:
                    # Conversion propre pour le tableau
                    df_serv = pd.DataFrame(list(services.items()), columns=["Port", "Service"])
                    st.table(df_serv)
                else:
                    st.info("Scan en cours...")

                st.subheader("🚨 Vulnérabilités Confirmées")
                vulns = data.get("confirmed_vulnerabilities", [])
                if vulns:
                    for v in vulns:
                        st.error(f"☠️ {v}")
                else:
                    st.success("Aucune vulnérabilité critique détectée pour l'instant.")

                st.subheader("💰 Loot (Secrets Exfiltrés)")
                loot = data.get("loot", [])
                if loot:
                    for l in loot:
                        st.warning(f"💎 {l}")

            with c2:
                st.subheader("👁️ Flux Visuel (Vision)")
                if os.path.exists("screenshot.png"):
                    try:
                        image = Image.open("screenshot.png")
                        # --- CORRECTION 2026 ---
                        st.image(image, caption=f"Cible: {data.get('target_ip')}", width="stretch")
                    except:
                        st.text("Mise à jour de l'image...")
                else:
                    st.text("En attente du module Vision...")

    # Refresh toutes les 2 secondes
    time.sleep(2)
