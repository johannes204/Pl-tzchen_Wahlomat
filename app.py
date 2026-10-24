import pandas as pd
import streamlit as st


# Daten laden (mit Cache für bessere Performance)
@st.cache_data
def load_data():
  platzerl_tabelle = (
      pd.read_csv(
          "Wahlomatfertig.csv",
          index_col="Plätzchen 2024",
          usecols=lambda col: col != "Kochbuch",
          skiprows=[1],
      )
      .fillna(0)
      .astype(int)
  )
  platzerl_tabelle2 = pd.read_csv(
      "Wahlomatfertig.csv",
      index_col="Plätzchen 2024",
      usecols=lambda col: col != "Kochbuch",
      nrows=1,
  ).fillna(0).astype(str)
  return platzerl_tabelle, platzerl_tabelle2


platzerl_tabelle, platzerl_tabelle2 = load_data()
fragen = {
    kategorie: platzerl_tabelle2[kategorie].iat[0]
    for kategorie in platzerl_tabelle2.columns
}

st.title("🍪 Plätzchen-Wahlomat")

# Fragen und Radio-Buttons generieren
vorlieben = {}
for kategorie, frage_text in fragen.items():
  vorlieben[kategorie] = st.radio(
      label=frage_text,
      options=[1, 0, -1],
      format_func=lambda x: {1: "Ja!!!", 0: "Egal.", -1: "Nein!!!"}[x],
      index=1,  # Standardmäßig auf "Egal." (0)
      key=kategorie,
  )

# Auswertungs-Button
if st.button("Sag mir was ich mir wünsche?"):
  punkte = pd.Series(0, index=platzerl_tabelle.index)
  for kategorie in fragen:
    punkte = punkte + platzerl_tabelle[kategorie] * vorlieben[kategorie]

  punkte.sort_values(ascending=False, inplace=True)

  st.subheader("Deine Favoriten:")
  for i in range(min(5, len(punkte))):
    st.write(f"**{punkte.iat[i]} Punkte:** {punkte.index[i]}")
