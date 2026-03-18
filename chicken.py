"""
chicken.py — Base de données des labels pour le poulet (volailles de chair).

Structure :
  1. LABEL_MAPPING       : table de correspondance codes Open Food Facts → clés internes
  2. LABELS_DB           : garanties par label et par critère
  3. PRIORITY_ORDER      : ordre de priorité du plus exigeant au moins exigeant
  4. detect_labels()     : détecte les labels depuis les tags OFF
  5. get_best_guarantees(): retourne les garanties les plus exigeantes

Principe : n'afficher que les garanties EXPLICITEMENT imposées par les textes officiels.
           "NS" = Non Spécifié dans le cahier des charges.

Sources :
  - Règlement (UE) 2018/848 — Agriculture biologique
  - Règlement (CE) n°543/2008 — Normes de commercialisation volailles
  - CDC Label Rouge Poulet Fermier — SYNALAF (homologué INAO)
  - CDC IGP Poulet de Bresse — AO 14-96
  - CDC IGP Poulet des Landes — IG 05-2001
  - CDC IGP Poulet Fermier d'Auvergne — IG 07-2002
  - CDC IGP Poulet Fermier de Vendée — IG 04-2001
  - CDC IGP Poulet Fermier du Gers — IG 06-2001
  - CDC IGP Volaille de Bresse — AO 14-96
  - CDC Bleu Blanc Cœur — charte BBC 2022
  - CDC IGP Volailles de Janzé — arrêté du 7 juillet 2025 (JORF n°0159)
  - CDC IGP Volailles du Maine (ex-Loué) — arrêté du 31 août 2022
    Note : L'IGP "Volailles de Loué" a été annulée par la Commission européenne
    le 3 février 2024. Les poulets Loué sont désormais produits sous l'IGP
    "Volailles du Maine". Loué est redevenu une marque commerciale.
"""

NS = "NS"

# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — TABLE DE CORRESPONDANCE
# ══════════════════════════════════════════════════════════════════════════════

LABEL_MAPPING = {
    # ── Agriculture Biologique ────────────────────────────────────────────────
    "en:organic":                         "bio_poulet",
    "en:eu-organic":                      "bio_poulet",
    "fr:ab-agriculture-biologique":       "bio_poulet",
    "fr:agriculture-biologique":          "bio_poulet",
    "fr:bio":                             "bio_poulet",
    "en:fr-bio-01":                       "bio_poulet",

    # ── Label Rouge — Poulet Fermier (générique SYNALAF) ──────────────────────
    "en:label-rouge":                     "label_rouge_poulet",
    "fr:label-rouge":                     "label_rouge_poulet",
    "fr:label-rouge-poulet-fermier":      "label_rouge_poulet",
    "en:label-rouge-poulet-fermier":      "label_rouge_poulet",

    # ── IGP Poulet de Bresse ──────────────────────────────────────────────────
    "fr:poulet-de-bresse":                "igp_bresse",
    "en:poulet-de-bresse":                "igp_bresse",
    "fr:volaille-de-bresse":              "igp_bresse",
    "en:aop-poulet-de-bresse":            "igp_bresse",

    # ── IGP Poulet des Landes ─────────────────────────────────────────────────
    "fr:poulet-des-landes":               "igp_landes",
    "en:poulet-des-landes":               "igp_landes",
    "fr:volaille-des-landes":             "igp_landes",

    # ── IGP Poulet Fermier d'Auvergne ─────────────────────────────────────────
    "fr:poulet-fermier-auvergne":         "igp_auvergne",
    "fr:poulet-d-auvergne":               "igp_auvergne",
    "en:poulet-fermier-auvergne":         "igp_auvergne",

    # ── IGP Poulet Fermier de Vendée ──────────────────────────────────────────
    "fr:poulet-fermier-vendee":           "igp_vendee",
    "fr:poulet-de-vendee":                "igp_vendee",
    "en:poulet-fermier-vendee":           "igp_vendee",

    # ── IGP Poulet Fermier du Gers ────────────────────────────────────────────
    "fr:poulet-fermier-gers":             "igp_gers",
    "fr:poulet-du-gers":                  "igp_gers",
    "en:poulet-fermier-gers":             "igp_gers",

    # ── Bleu Blanc Cœur ───────────────────────────────────────────────────────
    "fr:bleu-blanc-coeur":                "bleu_blanc_coeur_poulet",
    "en:bleu-blanc-coeur":                "bleu_blanc_coeur_poulet",

    # ── IGP Volailles de Janzé ────────────────────────────────────────────────
    "fr:volailles-de-janze":              "igp_janze",
    "en:volailles-de-janze":              "igp_janze",
    "fr:poulet-de-janze":                 "igp_janze",
    "en:poulet-de-janze":                 "igp_janze",
    "fr:fermiers-de-janze":               "igp_janze",

    # ── IGP Volailles du Maine / Loué ─────────────────────────────────────────
    # L'IGP "Volailles de Loué" a été annulée en février 2024 → remplacée par
    # l'IGP "Volailles du Maine". Loué est redevenu une marque commerciale.
    "fr:volailles-du-maine":              "igp_maine",
    "en:volailles-du-maine":              "igp_maine",
    "fr:fermiers-de-loue":                "igp_maine",
    "fr:volailles-de-loue":               "igp_maine",
    "en:volailles-de-loue":               "igp_maine",
    "fr:poulet-de-loue":                  "igp_maine",
    "fr:loue":                            "igp_maine",

    # ── IGP Volailles de Janzé ───────────────────────────────────────────────
    "fr:volailles-de-janze":              "igp_janze",
    "en:volailles-de-janze":              "igp_janze",
    "fr:poulet-de-janze":                 "igp_janze",
    "en:poulet-de-janze":                 "igp_janze",

    # ── IGP Poulet / Volailles du Maine (Loué) ────────────────────────────────
    "fr:volailles-du-maine":              "igp_loue_poulet",
    "en:volailles-du-maine":              "igp_loue_poulet",
    "fr:poulet-de-loue":                  "igp_loue_poulet",
    "en:poulet-de-loue":                  "igp_loue_poulet",
    "fr:loue":                            "igp_loue_poulet",

    # ── Codes réglementaires UE (mention obligatoire sur étiquette) ───────────
    # Code A — Élevage en plein air
    "en:free-range":                      "code_a_plein_air",
    "en:free-range-chicken":              "code_a_plein_air",
    "fr:plein-air":                       "code_a_plein_air",
    "fr:poulet-plein-air":                "code_a_plein_air",

    # Code B — Élevage extensif en bâtiment
    "en:barn":                            "code_b_extensif",
    "fr:elevage-extensif":                "code_b_extensif",
    "fr:poulet-au-sol":                   "code_b_extensif",

    # Code standard (élevage intensif en bâtiment — minimum légal)
    "en:standard-chicken":                "code_standard",
    "fr:elevage-standard":                "code_standard",
}


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — BASE DE DONNÉES DES LABELS
# ══════════════════════════════════════════════════════════════════════════════

LABELS_DB = {

    # ──────────────────────────────────────────────────────────────────────────
    # AOP POULET DE BRESSE
    # Le seul poulet AOP de France — cahier des charges le plus exigeant
    # Source : Cahier des charges AOP Volaille de Bresse — AO 14-96
    # ──────────────────────────────────────────────────────────────────────────
    "igp_bresse": {
        "nom_complet": "AOP Poulet de Bresse",
        "type": "AOP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales (maïs minimum 75%) + pâturage libre. Finition en épinette (cage individuelle) avec alimentation au lait et maïs pendant 2 à 3 semaines minimum.",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire. Parcours herbeux permanent. Phase de finition en épinette individuelle.",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air sur parcours herbeux.",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "type_batiment": {
                "valeur": "Poulailler mobile ou fixe avec accès permanent à un parcours herbeux.",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 500 poulets par bâtiment",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "surface_parcours": {
                "valeur": "≥ 10 m²/poulet",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "race_souche": {
                "valeur": "Gauloise Blanche uniquement (race locale de Bresse).",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "age_min_abattage": {
                "valeur": "≥ 4 mois (poulet), ≥ 5 mois (poularde), ≥ 8 mois (chapon)",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
            "aire_geographique": {
                "valeur": "Bresse (Ain, Saône-et-Loire, Jura)",
                "source": "CDC AOP Volaille de Bresse AO 14-96"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP POULET DES LANDES
    # Source : CDC IGP Poulet des Landes IG 05-2001
    # ──────────────────────────────────────────────────────────────────────────
    "igp_landes": {
        "nom_complet": "IGP Poulet des Landes",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75% (maïs grain entier minimum 50%). Sans facteurs de croissance ni stimulants.",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire sur parcours sous-bois (pins maritimes).",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air dès l'âge de 6 semaines.",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "type_batiment": {
                "valeur": "Bâtiments mobiles ou fixes avec litière de copeaux de bois.",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 400 poulets par bâtiment",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "surface_parcours": {
                "valeur": "≥ 10 m²/poulet (parcours sous-bois)",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente (Label Rouge agréées).",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
            "aire_geographique": {
                "valeur": "Département des Landes (40)",
                "source": "CDC IGP Poulet des Landes IG 05-2001"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP POULET FERMIER D'AUVERGNE
    # Source : CDC IGP Poulet Fermier d'Auvergne IG 07-2002
    # ──────────────────────────────────────────────────────────────────────────
    "igp_auvergne": {
        "nom_complet": "IGP Poulet Fermier d'Auvergne",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75%. Sans antibiotiques comme facteurs de croissance.",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire.",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air dès 6 semaines.",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 500 poulets par bâtiment",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "surface_parcours": {
                "valeur": "≥ 10 m²/poulet",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente (Label Rouge agréées).",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
            "aire_geographique": {
                "valeur": "Auvergne (Allier, Cantal, Haute-Loire, Puy-de-Dôme)",
                "source": "CDC IGP Poulet Fermier d'Auvergne IG 07-2002"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP POULET FERMIER DE VENDÉE
    # Source : CDC IGP Poulet Fermier de Vendée IG 04-2001
    # ──────────────────────────────────────────────────────────────────────────
    "igp_vendee": {
        "nom_complet": "IGP Poulet Fermier de Vendée",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75%. Maïs grain entier obligatoire. Sans facteurs de croissance.",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire.",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air dès 6 semaines.",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 500 poulets par bâtiment",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "surface_parcours": {
                "valeur": "≥ 10 m²/poulet",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente (Label Rouge agréées).",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
            "aire_geographique": {
                "valeur": "Vendée et communes limitrophes",
                "source": "CDC IGP Poulet Fermier de Vendée IG 04-2001"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP POULET FERMIER DU GERS
    # Source : CDC IGP Poulet Fermier du Gers IG 06-2001
    # ──────────────────────────────────────────────────────────────────────────
    "igp_gers": {
        "nom_complet": "IGP Poulet Fermier du Gers",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75% dont maïs grain entier minimum 50%. Sans facteurs de croissance.",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire.",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air dès 6 semaines.",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 500 poulets par bâtiment",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "surface_parcours": {
                "valeur": "≥ 10 m²/poulet",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente agréées Label Rouge.",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
            "aire_geographique": {
                "valeur": "Département du Gers (32)",
                "source": "CDC IGP Poulet Fermier du Gers IG 06-2001"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # LABEL ROUGE — POULET FERMIER (cahier des charges générique SYNALAF)
    # Source : CDC SYNALAF homologué INAO — LA 01-00 et révisions
    # ──────────────────────────────────────────────────────────────────────────
    "label_rouge_poulet": {
        "nom_complet": "Label Rouge Poulet Fermier",
        "type": "Label Rouge / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75% de la ration. Sans antibiotiques comme facteurs de croissance. Aliment complémentaire autorisé.",
                "source": "CDC SYNALAF LA 01-00"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire avec accès à un parcours extérieur enherbé.",
                "source": "CDC SYNALAF LA 01-00"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air dès l'âge de 6 semaines minimum.",
                "source": "CDC SYNALAF LA 01-00"
            },
            "type_batiment": {
                "valeur": "Bâtiment fixe ou mobile. Litière sèche obligatoire. Perchoirs obligatoires (≥ 6 cm/poulet).",
                "source": "CDC SYNALAF LA 01-00"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC SYNALAF LA 01-00"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 4 400 poulets par bâtiment",
                "source": "CDC SYNALAF LA 01-00"
            },
            "surface_parcours": {
                "valeur": "≥ 2 m²/poulet (parcours enherbé)",
                "source": "CDC SYNALAF LA 01-00"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente agréées (vitesse de croissance ≤ 44 g/jour).",
                "source": "CDC SYNALAF LA 01-00"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours",
                "source": "CDC SYNALAF LA 01-00"
            },
            "aire_geographique": {
                "valeur": "France entière (chaque CDC régional peut restreindre)",
                "source": "CDC SYNALAF LA 01-00"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # AGRICULTURE BIOLOGIQUE — POULET
    # Source : Règlement (UE) 2018/848 + 2020/464
    # ──────────────────────────────────────────────────────────────────────────
    "bio_poulet": {
        "nom_complet": "Agriculture Biologique (Poulet)",
        "type": "Bio / Certification UE",
        "criteres": {
            "alimentation": {
                "valeur": "100% biologique. Céréales bio. Pas d'OGM, pas d'antibiotiques préventifs, pas de facteurs de croissance.",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire avec accès permanent à un parcours extérieur.",
                "source": "Règlement (UE) 2018/848, Art. 14"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air (sauf restrictions sanitaires temporaires).",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II, §1.7"
            },
            "type_batiment": {
                "valeur": "Bâtiment avec lumière naturelle. Litière naturelle obligatoire. Perchoirs obligatoires.",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II"
            },
            "densite_batiment": {
                "valeur": "≤ 10 poulets/m² (ou 21 kg poids vif/m²)",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II, Tableau 6.1"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 4 800 poulets par bâtiment",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II, Tableau 6.1"
            },
            "surface_parcours": {
                "valeur": "≥ 4 m²/poulet",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II, Tableau 6.1"
            },
            "race_souche": {
                "valeur": "Races à croissance lente adaptées à l'élevage en plein air. Races standard interdites.",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours (poulet standard bio) ou race à croissance lente sans âge minimum fixé",
                "source": "Règlement (UE) 2018/848, Annexe II, Partie II, Tableau 6.1"
            },
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Règlement (UE) 2018/848"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # BLEU BLANC CŒUR — POULET
    # Label nutritionnel uniquement (enrichissement en oméga-3 via lin)
    # Source : Charte Bleu Blanc Cœur 2022
    # ──────────────────────────────────────────────────────────────────────────
    "bleu_blanc_coeur_poulet": {
        "nom_complet": "Bleu Blanc Cœur (Poulet)",
        "type": "Label nutritionnel privé",
        "criteres": {
            "alimentation": {
                "valeur": "Alimentation enrichie en graines de lin (minimum 5% de lin extrudé). Garantit un ratio oméga-6/oméga-3 ≤ 5 dans la viande.",
                "source": "Charte Bleu Blanc Cœur 2022"
            },
            "condition_elevage":   {"valeur": NS, "source": NS},
            "acces_exterieur":     {"valeur": NS, "source": NS},
            "type_batiment":       {"valeur": NS, "source": NS},
            "densite_batiment":    {"valeur": NS, "source": NS},
            "effectif_max_batiment": {"valeur": NS, "source": NS},
            "surface_parcours":    {"valeur": NS, "source": NS},
            "race_souche":         {"valeur": NS, "source": NS},
            "age_min_abattage":    {"valeur": NS, "source": NS},
            "aire_geographique":   {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE A — PLEIN AIR (mention réglementaire UE)
    # Source : Règlement (CE) n°543/2008, Annexe V
    # ──────────────────────────────────────────────────────────────────────────
    "code_a_plein_air": {
        "nom_complet": "Élevé en plein air (Code A)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":  {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Élevage en bâtiment le soir avec accès permanent au plein air en journée.",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent à un parcours extérieur en journée.",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 13 poulets/m² en bâtiment",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "effectif_max_batiment": {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "≥ 1 m²/poulet (parcours extérieur)",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "race_souche":      {"valeur": NS, "source": NS},
            "age_min_abattage": {
                "valeur": "≥ 56 jours",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Règlement (CE) n°543/2008"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE B — ÉLEVAGE EXTENSIF EN BÂTIMENT
    # Source : Règlement (CE) n°543/2008, Annexe V
    # ──────────────────────────────────────────────────────────────────────────
    "code_b_extensif": {
        "nom_complet": "Élevage extensif en bâtiment (Code B)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":  {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Élevage en bâtiment fermé. Aucun accès au plein air imposé.",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "acces_exterieur": {
                "valeur": "Aucun accès au plein air imposé.",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 15 poulets/m²",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "effectif_max_batiment": {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "Aucune surface extérieure imposée.",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "race_souche":      {"valeur": NS, "source": NS},
            "age_min_abattage": {
                "valeur": "≥ 56 jours",
                "source": "Règlement (CE) n°543/2008, Annexe V"
            },
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Règlement (CE) n°543/2008"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP VOLAILLES DE JANZÉ
    # Source : CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025
    # JORF n°0159 du 10 juillet 2025 — BO MASA n°2025-29
    # ──────────────────────────────────────────────────────────────────────────
    "igp_janze": {
        "nom_complet": "IGP Volailles de Janzé",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 70% de la ration (grains et dérivés). Alimentation 100% végétale, minérale et vitaminée. Non OGM (depuis 2009). Sans facteurs de croissance.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §4 Méthode d'obtention"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire sur parcours herbeux et ombragé. Petits bâtiments à faible densité. Souches à croissance lente.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §2 Description"
            },
            "acces_exterieur": {
                "valeur": "Accès au plein air obligatoire dès le début de la phase d'engraissement sur parcours herbeux et ombragé.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §4 Méthode d'obtention"
            },
            "type_batiment": {
                "valeur": "Petits bâtiments fixes à faible densité, avec litière.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §2 Description"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025 (conforme CDC LR SYNALAF)"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 4 400 poulets par bâtiment",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "surface_parcours": {
                "valeur": "≥ 2 m²/poulet (parcours herbeux et ombragé)",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §4 Méthode d'obtention"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente (descendantes des Gélines noires d'Armorique). Poulet blanc ou jaune selon croisement.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §2 Description"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours (poulet) | ≥ 94 jours (pintade) | ≥ 140 jours (dinde) | ≥ 150 jours (chapon)",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §5.6 Âge à l'abattage"
            },
            "aire_geographique": {
                "valeur": "Ille-et-Vilaine (entier) + communes limitrophes des Côtes d'Armor, Loire-Atlantique, Manche, Mayenne, Morbihan",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025, §3 Délimitation"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP VOLAILLES DU MAINE (ex-Volailles de Loué)
    # Note : L'IGP "Volailles de Loué" a été annulée par la Commission européenne
    # le 3 février 2024 (JOUE du 3 février 2024). Les poulets Loué sont désormais
    # certifiés sous l'IGP "Volailles du Maine". Loué est redevenu une marque
    # commerciale (SYVOL QUALIMAINE / Fermiers de Loué).
    # Source : CDC IGP Volailles du Maine — arrêté du 31 août 2022
    # ──────────────────────────────────────────────────────────────────────────
    "igp_maine": {
        "nom_complet": "IGP Volailles du Maine (Loué)",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 75% dont céréales en grains. Alimentation 100% végétale, minérale et vitaminée. Sans facteurs de croissance ni antibiotiques de croissance.",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.1 Alimentation"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air ou en liberté dans le bocage du Maine jusqu'à maturité sexuelle. Souches à croissance lente.",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4 Élevage"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air obligatoire (parcours herbeux et arborés). Trappe ouverte au plus tard à 9h jusqu'au crépuscule.",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.3 Parcours"
            },
            "type_batiment": {
                "valeur": "Bâtiment fixe, 480 m² maximum (poulet). Surface totale par site ≤ 1 600 m². Fenêtres pour lumière naturelle. Perchoirs obligatoires (≥ 10 ml / 100 m²).",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.2 Bâtiment"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m² jusqu'à l'abattage, n'excédant pas 25 kg/m²",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.2 Densité"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 4 400 poulets par bâtiment (surface max 480 m² × densité ≤ 11/m²)",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.2 Bâtiment"
            },
            "surface_parcours": {
                "valeur": "≥ 4 m²/poulet (parcours herbeux et arboré attenant au bâtiment)",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.4.3 Parcours"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente agréées Label Rouge (vitesse de croissance lente adaptée au plein air).",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.2 Sélection"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours (poulet standard) | ≥ 100 jours (poulet liberté) | ≥ 150 jours (chapon)",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §5.6 Âge abattage"
            },
            "aire_geographique": {
                "valeur": "Sarthe, Mayenne, nord du Maine-et-Loire, communes limitrophes de la Sarthe (périmètre du Maine)",
                "source": "CDC IGP Volailles du Maine, arrêté du 31 août 2022, §3 Aire géographique"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE STANDARD — Élevage intensif en bâtiment (minimum légal UE)
    # Source : Directive 2007/43/CE
    # ──────────────────────────────────────────────────────────────────────────
    "code_standard": {
        "nom_complet": "Élevage standard (minimum légal UE)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":  {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Élevage en bâtiment fermé. Aucun accès au plein air. Densité maximale encadrée par la directive bien-être.",
                "source": "Directive 2007/43/CE"
            },
            "acces_exterieur": {
                "valeur": "Aucun accès au plein air.",
                "source": "Directive 2007/43/CE"
            },
            "type_batiment": {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 33 kg poids vif/m² (soit ~20-22 poulets/m²). Peut être étendu à 39 ou 42 kg/m² sous conditions.",
                "source": "Directive 2007/43/CE, Art. 3"
            },
            "effectif_max_batiment": {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "Aucune surface extérieure.",
                "source": "Directive 2007/43/CE"
            },
            "race_souche":      {"valeur": NS, "source": NS},
            "age_min_abattage": {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Directive 2007/43/CE"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP VOLAILLES DE JANZÉ
    # Enregistrée en 1996. CDC homologué par arrêté du 7 juillet 2025.
    # Source : CDC IGP Volailles de Janzé, JORF n°0159 du 10 juillet 2025
    # ──────────────────────────────────────────────────────────────────────────
    "igp_janze": {
        "nom_complet": "IGP Volailles de Janzé",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 70% de la ration. 100% végétaux, minéraux et vitamines. Sans antibiotiques comme facteurs de croissance.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "condition_elevage": {
                "valeur": "Élevage en plein air obligatoire. Souches à croissance lente. Petits bâtiments en faible densité sur parcours herbeux et ombragé.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air sur parcours herbeux et ombragé dès le début de la phase d'engraissement.",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "type_batiment": {
                "valeur": "Bâtiments fixes, surface maximale 400 m², ventilation naturelle statique.",
                "source": "CDC IGP Volailles de Janzé + Wikipedia (10-01-2026)"
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m²",
                "source": "CDC IGP Volailles de Janzé + Wikipedia (10-01-2026)"
            },
            "effectif_max_batiment": {
                "valeur": "≤ 4 400 poulets par bâtiment de 400 m²",
                "source": "CDC IGP Volailles de Janzé + Wikipedia (10-01-2026)"
            },
            "surface_parcours": {
                "valeur": "Parcours herbeux et ombragé (superficie non précisée dans le CDC public)",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "race_souche": {
                "valeur": "Souches rustiques à croissance lente (vitesse de croissance lente imposée).",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "age_min_abattage": {
                "valeur": "≥ 81 jours (poulet) ; ≥ 150 jours (chapon) ; ≥ 140 jours (dinde) ; ≥ 94 jours (pintade)",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
            "aire_geographique": {
                "valeur": "Ille-et-Vilaine (entier) + cantons limitrophes (Côtes-d'Armor, Loire-Atlantique, Manche, Mayenne, Morbihan)",
                "source": "CDC IGP Volailles de Janzé, arrêté du 7 juillet 2025"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # IGP VOLAILLES DU MAINE — POULET DE LOUÉ
    # L'IGP couvre l'ensemble des volailles du Maine dont le poulet de Loué.
    # Label LR associé : LA 04-81 (Poulet Jaune Fermier Élevé en Liberté, SYVOL QUALIMAINE)
    # Source : CDC SYVOL QUALIMAINE LA 04-81 + site loue.fr
    # ──────────────────────────────────────────────────────────────────────────
    "igp_loue_poulet": {
        "nom_complet": "IGP Volailles du Maine / Poulet de Loué",
        "type": "IGP / INAO",
        "criteres": {
            "alimentation": {
                "valeur": "Céréales minimum 80% (grains entiers distribués). 100% matières premières végétales et minérales. Parcours entretenus sans engrais ni herbicides de synthèse.",
                "source": "CDC SYVOL QUALIMAINE LA 04-81 (Poulet Jaune Fermier Élevé en Liberté)"
            },
            "condition_elevage": {
                "valeur": "Élevé en liberté sur grands parcours (ou plein air selon label). Souche à croissance lente. Parcours non traités aux pesticides de synthèse.",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air (élevage en liberté ou plein air selon la gamme).",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "type_batiment": {
                "valeur": NS,
                "source": NS
            },
            "densite_batiment": {
                "valeur": "≤ 11 poulets/m² (≤ 25 kg poids vif/m²)",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "effectif_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_parcours": {
                "valeur": "Grands parcours herbeux entretenus sans engrais ni herbicides de synthèse (superficie exacte non publiée dans le CDC public).",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "race_souche": {
                "valeur": "Souches à croissance lente agréées (sélection SYSAAF). Poulet jaune fermier.",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "age_min_abattage": {
                "valeur": "≥ 84 jours (Poulet Jaune Fermier Loué LA 04-81)",
                "source": "CDC SYVOL QUALIMAINE LA 04-81"
            },
            "aire_geographique": {
                "valeur": "Bassin du Maine — Sarthe et départements limitrophes (rayon ≤ 80 km autour de Loué)",
                "source": "CDC IGP Volailles du Maine / site loue.fr"
            },
        }
    },

}  # fin LABELS_DB


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 3 — FONCTION DE SÉLECTION
# ══════════════════════════════════════════════════════════════════════════════

PRIORITY_ORDER = [
    "igp_bresse",
    "igp_landes",
    "igp_auvergne",
    "igp_vendee",
    "igp_gers",
    "igp_janze",
    "igp_loue_poulet",
    "label_rouge_poulet",
    "bio_poulet",
    "bleu_blanc_coeur_poulet",
    "code_a_plein_air",
    "code_b_extensif",
    "code_standard",
]


def detect_labels(raw_labels_string: str) -> list[str]:
    if not raw_labels_string:
        return []
    detected = []
    tokens = [t.strip().lower() for t in raw_labels_string.split(",")]
    for token in tokens:
        if token in LABEL_MAPPING:
            key = LABEL_MAPPING[token]
            if key not in detected:
                detected.append(key)
    return detected


def get_best_guarantees(detected_labels: list[str]) -> dict:
    if not detected_labels:
        return {"labels_reconnus": [], "garanties": {}}

    labels_valides = [l for l in detected_labels if l in LABELS_DB]
    if not labels_valides:
        return {"labels_reconnus": [], "garanties": {}}

    labels_reconnus = [
        {"cle": l, "nom": LABELS_DB[l]["nom_complet"], "type": LABELS_DB[l]["type"]}
        for l in labels_valides
    ]

    tous_criteres = list(next(iter(LABELS_DB.values()))["criteres"].keys())
    garanties = {}

    for critere in tous_criteres:
        meilleure_valeur = NS
        meilleure_source = NS
        meilleur_label = None

        for label_prioritaire in PRIORITY_ORDER:
            if label_prioritaire in labels_valides:
                data = LABELS_DB[label_prioritaire]["criteres"].get(critere, {})
                valeur = data.get("valeur", NS)
                source = data.get("source", NS)
                if valeur and valeur != NS:
                    meilleure_valeur = valeur
                    meilleure_source = source
                    meilleur_label = LABELS_DB[label_prioritaire]["nom_complet"]
                    break

        garanties[critere] = {
            "valeur": meilleure_valeur,
            "source": meilleure_source,
            "label_source": meilleur_label,
        }

    return {
        "labels_reconnus": labels_reconnus,
        "garanties": garanties,
    }
