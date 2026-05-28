"""
labels_core.py — Logique commune de détection et d'agrégation des labels.

Les modules eggs.py et chicken.py fournissent leurs propres tables de données
(LABEL_MAPPING, LABELS_DB, PRIORITY_ORDER) et délèguent la logique ici.
"""

NS = "NS"


def detect_labels(raw_labels_string: str, label_mapping: dict) -> list[str]:
    """
    Prend la chaîne brute de labels Open Food Facts (ex: "en:organic, fr:label-rouge")
    et retourne la liste des clés internes reconnues (ex: ["bio", "label_rouge_plein_air"]).
    """
    if not raw_labels_string:
        return []

    detected = []
    tokens = [t.strip().lower() for t in raw_labels_string.split(",")]
    for token in tokens:
        if token in label_mapping:
            key = label_mapping[token]
            if key not in detected:
                detected.append(key)
    return detected


def get_best_guarantees(detected_labels: list[str], labels_db: dict, priority_order: list[str]) -> dict:
    """
    Prend une liste de clés internes de labels et retourne, pour chaque critère,
    la garantie la plus exigeante trouvée selon priority_order.
    Retourne aussi la liste des labels reconnus avec leur nom complet.
    """
    if not detected_labels:
        return {"labels_reconnus": [], "garanties": {}}

    labels_valides = [l for l in detected_labels if l in labels_db]
    if not labels_valides:
        return {"labels_reconnus": [], "garanties": {}}

    labels_reconnus = [
        {"cle": l, "nom": labels_db[l]["nom_complet"], "type": labels_db[l]["type"]}
        for l in labels_valides
    ]

    tous_criteres = list(next(iter(labels_db.values()))["criteres"].keys())
    garanties = {}

    for critere in tous_criteres:
        meilleure_valeur = NS
        meilleure_source = NS
        meilleur_label = None

        for label_prioritaire in priority_order:
            if label_prioritaire in labels_valides:
                data = labels_db[label_prioritaire]["criteres"].get(critere, {})
                valeur = data.get("valeur", NS)
                source = data.get("source", NS)
                if valeur and valeur != NS:
                    meilleure_valeur = valeur
                    meilleure_source = source
                    meilleur_label = labels_db[label_prioritaire]["nom_complet"]
                    break

        garanties[critere] = {
            "valeur": meilleure_valeur,
            "source": meilleure_source,
            "label_source": meilleur_label,
        }

    return {"labels_reconnus": labels_reconnus, "garanties": garanties}
