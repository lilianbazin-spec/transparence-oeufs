from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from fastapi.middleware.cors import CORSMiddleware
from eggs import detect_labels as eggs_detect_labels, get_best_guarantees as eggs_get_best_guarantees
from chicken import detect_labels as chicken_detect_labels, get_best_guarantees as chicken_get_best_guarantees

# Catégories de produit détectées via les categories_tags OFF
CHICKEN_KEYWORDS = ["chicken", "poulet", "volaille-de-chair", "broiler"]
EGGS_KEYWORDS    = ["egg", "oeuf", "œuf"]

def detect_product_type(categories_tags: list, product_name: str = "") -> str:
    """
    Retourne 'chicken', 'eggs' ou 'unknown' selon les catégories du produit.
    """
    texte = " ".join(categories_tags).lower() + " " + product_name.lower()
    if any(kw in texte for kw in CHICKEN_KEYWORDS):
        return "chicken"
    if any(kw in texte for kw in EGGS_KEYWORDS):
        return "eggs"
    return "unknown"

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


# ── Détection du système d'élevage dans les catégories OFF ──────────────────
# On utilise des mots-clés plutôt que des tags exacts — bien plus robuste
# car OFF peut utiliser "en:free-range-eggs", "en:free-range-hen-eggs", etc.

CATEGORIES_KEYWORDS = [
    # (mots-clés à chercher dans le tag, clé interne)
    # Bio — testé en premier car plus exigeant
    (["organic-egg", "oeufs-bio", "oeufs-biologiques", "bio-egg"], "bio"),

    # Plein air
    (["free-range", "plein-air", "plein_air",
      "elevees-en-plein", "élevées-en-plein",
      "outdoor", "oeufs-plein"], "code_1_plein_air"),

    # Au sol
    (["barn", "au-sol", "au_sol",
      "elevees-au-sol", "élevées-au-sol",
      "sol-egg", "floor-reared"], "code_2_sol"),

    # Cage
    (["caged", "en-cage", "en_cage",
      "cage-egg", "battery"], "code_3_cage"),
]

def detect_from_categories(categories_tags: list) -> list[str]:
    """
    Cherche le système d'élevage dans les catégories OFF par mots-clés.
    Retourne la liste des clés internes détectées.
    """
    detected = []
    for tag in categories_tags:
        tag_norm = tag.strip().lower()
        for keywords, key in CATEGORIES_KEYWORDS:
            if key not in detected:
                if any(kw in tag_norm for kw in keywords):
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

    # ── Détection du type de produit ─────────────────────────────────────────
    categories_tags = product.get("categories_tags", [])
    product_type = detect_product_type(categories_tags, product.get("product_name", ""))

    # ── Sélection du module selon le type de produit ──────────────────────────
    if product_type == "chicken":
        detect_fn       = chicken_detect_labels
        get_guarantees  = chicken_get_best_guarantees
    else:
        detect_fn       = eggs_detect_labels
        get_guarantees  = eggs_get_best_guarantees

    # ── Détection via labels_tags ─────────────────────────────────────────────
    labels_detectes = detect_fn(labels_bruts_str)

    # ── Fallback : détection via categories_tags ──────────────────────────────
    codes_elevage_eggs    = {"code_1_plein_air", "code_2_sol", "code_3_cage", "bio",
                             "bio_coherence", "demeter", "label_rouge_plein_air",
                             "label_rouge_liberte", "oeufs_de_loue", "cocorette"}
    codes_elevage_chicken = {"code_a_plein_air", "code_b_extensif", "code_standard",
                             "bio_poulet", "label_rouge_poulet"}
    codes_elevage = codes_elevage_chicken if product_type == "chicken" else codes_elevage_eggs
    a_code_elevage = any(l in codes_elevage for l in labels_detectes)

    if not a_code_elevage:
        from_categories = detect_from_categories(categories_tags)
        for key in from_categories:
            if key not in labels_detectes:
                labels_detectes.append(key)

    # ── Calcul des garanties ──────────────────────────────────────────────────
    resultat = get_guarantees(labels_detectes)

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
            "product_type":   product_type,
            "labels_bruts":    labels_bruts_str,
            "labels_reconnus": resultat["labels_reconnus"],
            "garanties":       resultat["garanties"],
        }
    }
