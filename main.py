import streamlit as st
from backend.calculs import (
    calcul_total_impot,
    calcul_total_impot_avec_3a,
)

st.set_page_config(page_title="Calculateur d’économie d’impôt – 3e pilier (3A)", layout="centered")

# --- Titre ---
st.title("Calculateur d’économie d’impôt – 3e pilier (3A)")

# --- Entrée utilisateur ---
st.header("Vos informations fiscales")

revenu = st.number_input("Revenu net imposable annuel (CHF)", min_value=0, step=1000)

npa = st.text_input("Code postal (NPA)", max_chars=4)

statut_civil = st.selectbox("Statut civil", ["Célibataire", "Marié"])

enfant = st.checkbox("Enfant(s) à charge")

religion = st.selectbox("Affiliation religieuse", ["Aucune", "Catholique", "Protestante", "Chrétienne", "Autre"])

montant_3a = st.number_input("Montant versé au 3e pilier A (CHF)", min_value=0, max_value=7056)

# --- Calcul ---
if st.button("Calculer l’économie d’impôt"):
    try:
        # Calcul sans déduction 3A
        impot_sans_3a = calcul_total_impot(
            revenu=revenu,
            npa=npa,
            statut=statut_civil,
            enfant=enfant,
            religion=religion
        )

        # Calcul avec déduction 3A
        impot_avec_3a = calcul_total_impot_avec_3a(
            revenu=revenu,
            montant_3a=montant_3a,
            npa=npa,
            statut=statut_civil,
            enfant=enfant,
            religion=religion
        )

        economie = impot_sans_3a - impot_avec_3a

        # Résultats
        st.subheader("Résultats")
        st.write(f"Impôt total sans 3A : **CHF {impot_sans_3a:,.2f}**")
        st.write(f"Impôt total avec 3A : **CHF {impot_avec_3a:,.2f}**")
        st.write(f"Économie d’impôt : **CHF {economie:,.2f}**")

        # Graphique comparatif
        st.subheader("Comparaison graphique")
        st.bar_chart({
            "Sans 3A": [impot_sans_3a],
            "Avec 3A": [impot_avec_3a]
        })

    except ValueError as ve:
        st.error(f"Erreur de saisie : {ve}")
    except Exception as e:
        st.error("Une erreur est survenue lors du calcul.")
        st.text(str(e))
