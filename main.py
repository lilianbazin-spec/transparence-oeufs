from fastapi import FastAPI
from fastapi.responses import FileResponse
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

# ── Sert index.html à la racine ───────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("index.html")


# ── Table de correspondance catégories OFF → clés internes ───────────────────
# Quand les labels_tags sont vides ou insuffisants, on regarde les catégories
CATEGORIES_MAPPING = {
    # Plein air
    "en:free-range-eggs":                        "code_1_plein_air",
    "fr:oeufs-de-poules-elevees-en-plein-air":   "code_1_plein_air",
    "en:free-range-hen-eggs":                    "code_1_plein_air",

    # Au sol
    "en:barn-eggs":                              "code_2_sol",
    "fr:oeufs-de-poules-elevees-au-sol":         "code_2_sol",
    "en:barn-laid-eggs":                         "code_2_sol",

    # Cage
    "en:eggs-from-caged-hens":                   "code_3_cage",
    "fr:oeufs-de-poules-elevees-en-cage":        "code_3_cage",

    # Bio
    "en:organic-eggs":                           "bio",
    "fr:oeufs-biologiques":                      "bio",
}

def detect_from_categories(categories_tags: list) -> list[str]:
    """
    Cherche des indices de système d'élevage dans les catégories OFF
    quand les labels_tags sont insuffisants.
    """
    detected = []
    for tag in categories_tags:
        tag_norm = tag.strip().lower()
        if tag_norm in CATEGORIES_MAPPING:
            key = CATEGORIES_MAPPING[tag_norm]
            if key not in detected:
                detected.append(key)
    return detected


# ── Endpoint scan ─────────────────────────────────────────────────────────────
@app.get("/scan/{barcode}")
def scan_product(barcode: str):

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == 0:
        return {"found": False, "message": "Produit non trouvé dans Open Food Facts"}

    product = data["product"]

    # ── Labels bruts (labels_tags) ────────────────────────────────────────────
    labels_tags = product.get("labels_tags", [])
    labels_bruts_str = ", ".join(labels_tags)

    # ── Détection via labels_tags ─────────────────────────────────────────────
    labels_detectes = detect_labels(labels_bruts_str)

    # ── Fallback : détection via categories_tags ──────────────────────────────
    # Si aucun code d'élevage n'est détecté dans les labels,
    # on regarde dans les catégories (ex: "Œufs de poules élevées en plein air")
    codes_elevage = {"code_1_plein_air", "code_2_sol", "code_3_cage", "bio",
                     "bio_coherence", "demeter", "label_rouge_plein_air",
                     "label_rouge_liberte", "oeufs_de_loue", "cocorette"}
    a_code_elevage = any(l in codes_elevage for l in labels_detectes)

    if not a_code_elevage:
        categories_tags = product.get("categories_tags", [])
        from_categories = detect_from_categories(categories_tags)
        for key in from_categories:
            if key not in labels_detectes:
                labels_detectes.append(key)

    # ── Calcul des garanties ──────────────────────────────────────────────────
    resultat = get_best_guarantees(labels_detectes)

    # ── Correction aire géographique via champ origins ────────────────────────
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

    # ── Réponse ───────────────────────────────────────────────────────────────
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
