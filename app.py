import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

CSV_PATH = "Wahlomatfertig.csv"

st.set_page_config(page_title="Plätzchen-Wahlomat", page_icon="🍪", layout="centered")


@st.cache_data
def load_data(file_path: str):
    df_raw = pd.read_csv(file_path, index_col="Plätzchen 2024")

    if "Kochbuch" in df_raw.columns:
        df_raw = df_raw.drop(columns=["Kochbuch"])

    fragen_series = df_raw.iloc[0].astype(str)
    platzerl_tabelle = df_raw.iloc[1:].fillna(0).astype(int)

    return platzerl_tabelle, fragen_series.to_dict()


try:
    platzerl_tabelle, fragen = load_data(CSV_PATH)
except FileNotFoundError:
    st.error(f"Die Datei `{CSV_PATH}` wurde nicht gefunden. Bitte überprüfe den Pfad.")
    st.stop()

st.title("🍪 Plätzchen-Wahlomat")
st.write("Finde heraus, welche Plätzchen am besten zu deinen Vorlieben passen!")

st.divider()

# Vorlieben abfragen
vorlieben = {}
cols = st.columns(2)

for i, (kategorie, frage_text) in enumerate(fragen.items()):
    col = cols[i % 2]
    with col:
        vorlieben[kategorie] = st.radio(
            label=frage_text,
            options=[1, 0, -1],
            format_func=lambda x: {1: "Ja!!! 😋", 0: "Egal. 😐", -1: "Nein!!!"}[x],
            index=1,
            key=f"radio_{kategorie}",
            horizontal=True,
        )

st.divider()

# Auswertung mit Kosinus-Ähnlichkeit
if st.button(
    "Sag mir, was ich mir wünsche!",
    type="primary",
    use_container_width=True,
):
    # 1. Prüfen, ob alle Antworten neutral sind
    if all(wert == 0 for wert in vorlieben.values()):
        st.error(
            "Du hast alle Fragen mit 'Egal' beantwortet. "
            "Bitte wähle mindestens einmal Ja oder Nein aus."
        )
        st.stop()

    # 2. Vorlieben in einen 2D-Vektor umwandeln
    vorlieben_array = (
        pd.Series(vorlieben).values.reshape(1, -1)
    )

    # 3. Kosinus-Ähnlichkeit berechnen
    similarities = cosine_similarity(
        platzerl_tabelle,
        vorlieben_array
    ).flatten()

    # 4. Ergebnisse sortieren
    aehnlichkeit = pd.Series(
        similarities,
        index=platzerl_tabelle.index
    ).sort_values(ascending=False)

    # 5. Top 5 anzeigen
    st.subheader("Deine Top-Favoriten:")

    top_n = aehnlichkeit.head(5)

    for rank, (plaetzchen_name, score) in enumerate(
        top_n.items(), start=1
    ):
        st.metric(
            label=f"Platz {rank}: {plaetzchen_name}",
            value=f"{score * 100:.1f}"
        )