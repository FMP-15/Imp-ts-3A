import json
import os

# --- Chargement des barèmes ---
with open("data/baremes_communes.json", encoding="utf-8") as f:
    COMMUNES = json.load(f)

with open("data/baremes_cantonaux.json", encoding="utf-8") as f:
    CANTONAUX = json.load(f)

with open("data/baremes_confederaux.json", encoding="utf-8") as f:
    CONFEDERAUX = json.load(f)["barèmes"]


# --- Fonctions internes ---
def get_commune_by_npa(npa):
    npa = str(npa).strip()
    for commune in COMMUNES:
        if npa in commune["npa"]:
            return commune
    raise ValueError("NPA non trouvé dans la base de données des communes.")

def get_situation_key(canton, statut, enfant):
    if canton == "VD":
        if statut == "Marié":
            return "Marié(e)"
        elif statut == "Célibataire" and enfant:
            return "Personne vivant seule, avec enfant (en concubinage)"
        else:
            return "Personne vivant seule, avec / sans enfant"
    else:
        raise NotImplementedError("Seul le canton de Vaud est actuellement supporté.")

def appliquer_bareme(revenu, bareme):
    impot = 0.0
    precedent = 0
    for tranche in bareme:
        max_tranche = tranche["tranche_max"]
        taux = tranche["taux"] / 100
        if revenu > max_tranche:
            impot += (max_tranche - precedent) * taux
            precedent = max_tranche
        else:
            impot += (revenu - precedent) * taux
            break
    return impot

def get_taux_religion(commune, religion):
    if religion.lower() == "aucune":
        return 0.0
    religion_map = {
        "réformée": "réformée",
        "protestante": "réformée",
        "catholique": "catholique",
        "chrétienne": "chrétienne",
        "autre": "réformée"  # au choix, selon politique
    }
    rel = religion_map.get(religion.lower(), "réformée")
    return commune["taux_religion"].get(rel, 0.0)


# --- Fonctions principales ---
def calcul_total_impot(revenu, npa, statut, enfant, religion):
    commune = get_commune_by_npa(npa)
    canton = commune["canton"]
    situation_key = get_situation_key(canton, statut, enfant)

    # Barème fédéral
    bareme_conf = CONFEDERAUX.get(situation_key)
    impot_conf = appliquer_bareme(revenu, bareme_conf)

    # Barème cantonal
    bareme_canton = CANTONAUX[canton][situation_key]
    impot_canton = appliquer_bareme(revenu, bareme_canton)

    # Communal
    taux_communal = commune["taux_communal"] / 100
    impot_communal = impot_canton * taux_communal

    # Religieux
    taux_religion = get_taux_religion(commune, religion) / 100
    impot_religieux = impot_canton * taux_religion

    total = impot_conf + impot_canton + impot_communal + impot_religieux
    return round(total, 2)

def calcul_total_impot_avec_3a(revenu, montant_3a, npa, statut, enfant, religion):
    revenu_reduit = max(0, revenu - montant_3a)
    return calcul_total_impot(revenu_reduit, npa, statut, enfant, religion)
