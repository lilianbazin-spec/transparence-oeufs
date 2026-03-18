from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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

# ── Sert le fichier index.html à la racine ────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("index.html")


# ── Endpoint scan ─────────────────────────────────────────────────────────────
@app.get("/scan/{barcode}")
def scan_product(barcode: str):

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == 0:
        return {"found": False, "message": "Produit non trouvé dans Open Food Facts"}

    product = data["product"]

    labels_tags = product.get("labels_tags", [])
    labels_bruts_str = ", ".join(labels_tags)

    labels_detectes = detect_labels(labels_bruts_str)
    resultat = get_best_guarantees(labels_detectes)

    # Correction aire géographique via champ origins Open Food Facts
    origine_produit = (
        product.get("origins", "")
        or product.get("manufacturing_places", "")
        or product.get("countries", "")
    ).strip()

    valeurs_generiques = ["Tout territoire UE", "France entière"]
    if origine_produit and "garanties" in resultat:
        garantie_aire = resultat["garanties"].get("aire_geographique", {})
        if garantie_aire.get("valeur") in valeurs_generiques:
            resultat["garanties"]["aire_geographique"] = {
                "valeur": origine_produit,
                "source": "Champ 'origins' Open Food Facts (donnée déclarée par le producteur)",
                "label_source": "Open Food Facts",
            }

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
