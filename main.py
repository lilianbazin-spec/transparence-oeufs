from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware
from eggs import detect_labels, get_best_guarantees

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/scan/{barcode}")
def scan_product(barcode: str):

    # ── Étape 1 : interroger Open Food Facts ──────────────────────────────────
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == 0:
        return {"found": False, "message": "Produit non trouvé dans Open Food Facts"}

    product = data["product"]

    # ── Étape 2 : récupérer les labels bruts ──────────────────────────────────
    labels_tags = product.get("labels_tags", [])
    labels_bruts_str = ", ".join(labels_tags)

    # ── Étape 3 : analyser les labels avec eggs.py ────────────────────────────
    labels_detectes = detect_labels(labels_bruts_str)
    resultat = get_best_guarantees(labels_detectes)

    # ── Étape 4 : corriger l'aire géographique selon les données du produit ───
    #
    # Le règlement UE bio (2018/848) est valable sur tout le territoire UE,
    # donc eggs.py retourne "Tout territoire UE" pour le label bio.
    # Mais Open Food Facts fournit le champ "origins" qui indique le pays
    # de production réel. On l'utilise pour affiner l'affichage.
    #
    # Exemples de valeurs Open Food Facts :
    #   origins          → "France" ou "en:france" ou "France, Bretagne"
    #   manufacturing_places → "Loué, Sarthe"
    #   countries        → "en:france"

    origine_produit = (
        product.get("origins", "")
        or product.get("manufacturing_places", "")
        or product.get("countries", "")
    ).strip()

    # Si on a une origine ET que le critère aire_geographique est renseigné,
    # on remplace la valeur générique par l'origine réelle du produit.
    if origine_produit and "garanties" in resultat:
        garantie_aire = resultat["garanties"].get("aire_geographique", {})
        valeur_actuelle = garantie_aire.get("valeur", "NS")

        # On n'écrase que si la valeur est générique (UE ou France entière)
        # et non une zone IGP précise (ex: "Sarthe, Mayenne")
        valeurs_generiques = [
            "Tout territoire UE",
            "France entière",
        ]
        if valeur_actuelle in valeurs_generiques:
            resultat["garanties"]["aire_geographique"] = {
                "valeur": origine_produit,
                "source": "Champ 'origins' Open Food Facts (donnée déclarée par le producteur)",
                "label_source": "Open Food Facts",
            }

    # ── Étape 5 : construire et retourner la réponse complète ─────────────────
    return {
        "found": True,
        "product": {
            "name":            product.get("product_name", "Non renseigné"),
            "brand":           product.get("brands", "Non renseigné"),
            "categories":      product.get("categories", "Non renseigné"),
            "image_url":       product.get("image_front_url", ""),
            "labels_bruts":    labels_bruts_str,
            "labels_reconnus": resultat["labels_reconnus"],
            "garanties":       resultat["garanties"],
        }
    }