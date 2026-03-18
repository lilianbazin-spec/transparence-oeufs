"""
eggs.py — Base de données des labels pour les œufs de poules pondeuses.

Structure :
  1. LABEL_MAPPING       : table de correspondance codes Open Food Facts → clés internes
  2. LABELS_DB           : garanties par label et par critère
  3. get_best_guarantees : fonction qui retourne les garanties les plus exigeantes
                           pour une liste de labels donnée

Principe : n'afficher que les garanties EXPLICITEMENT imposées par les textes officiels.
           "NS" = Non Spécifié dans le cahier des charges.

Sources :
  - Règlement (UE) 2018/848 + Règlement d'exécution (UE) 2020/464
  - Cahiers des charges INAO : LA 35-99, LA 18-98, LA 03/99, LA 04/02
  - Cahier des charges Bio Cohérence v.01/26 (janvier 2026)
  - Fiche technique Demeter France 2022
"""

# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — TABLE DE CORRESPONDANCE
# Traduit les codes Open Food Facts (bruts, en minuscules) vers les clés internes
# ══════════════════════════════════════════════════════════════════════════════

LABEL_MAPPING = {
    # Agriculture Biologique
    "en:organic":                        "bio",
    "en:eu-organic":                     "bio",
    "fr:ab-agriculture-biologique":      "bio",
    "fr:agriculture-biologique":         "bio",
    "en:fr-bio-01":                      "bio",
    "fr:bio":                            "bio",

    # Label Rouge — Plein Air (sans mention liberté)
    "en:label-rouge":                    "label_rouge_plein_air",
    "fr:label-rouge":                    "label_rouge_plein_air",

    # Label Rouge Fermier — Liberté
    # (détecté via la catégorie "free-range" + label rouge, géré dans main.py)
    "fr:label-rouge-fermier":            "label_rouge_liberte",
    "en:label-rouge-fermier":            "label_rouge_liberte",

    # Œufs de Loué
    "fr:oeufs-de-loue":                  "oeufs_de_loue",
    "en:oeufs-de-loue":                  "oeufs_de_loue",
    "fr:loue":                           "oeufs_de_loue",

    # Cocorette
    "fr:cocorette":                      "cocorette",
    "en:cocorette":                      "cocorette",

    # Bleu Blanc Cœur
    "fr:bleu-blanc-coeur":               "bleu_blanc_coeur",
    "en:bleu-blanc-coeur":               "bleu_blanc_coeur",

    # Bio Cohérence
    "fr:bio-coherence":                  "bio_coherence",
    "en:bio-coherence":                  "bio_coherence",

    # Demeter
    "en:demeter":                        "demeter",
    "fr:demeter":                        "demeter",

    # ── Codes réglementaires UE (système d'élevage) ───────────────────────────
    # Code 0 — Biologique (déjà couvert par "bio" ci-dessus via en:organic)

    # Code 1 — Plein air (plusieurs variantes de tags Open Food Facts)
    "en:free-range":                          "code_1_plein_air",
    "en:free-range-eggs":                     "code_1_plein_air",
    "en:eggs-from-free-range-hens":           "code_1_plein_air",
    "fr:plein-air":                           "code_1_plein_air",
    "fr:oeufs-plein-air":                     "code_1_plein_air",
    "fr:oeufs-de-poules-elevees-en-plein-air": "code_1_plein_air",

    # Code 2 — Au sol
    "en:barn-eggs":                           "code_2_sol",
    "en:barn":                                "code_2_sol",
    "en:eggs-from-hens-kept-in-barns":        "code_2_sol",
    "fr:au-sol":                              "code_2_sol",
    "fr:oeufs-de-poules-elevees-au-sol":      "code_2_sol",

    # Code 3 — Cage aménagée
    "en:eggs-from-caged-hens":                "code_3_cage",
    "en:caged-eggs":                          "code_3_cage",
    "en:cage":                                "code_3_cage",
    "fr:cage-amenagee":                       "code_3_cage",
    "fr:oeufs-de-poules-elevees-en-cage":     "code_3_cage",

    # Œufs de France (label interprofessionnel)
    "fr:oeufs-de-france":                "oeufs_de_france",
    "en:oeufs-de-france":                "oeufs_de_france",
    "fr:label-oeufs-de-france":          "oeufs_de_france",

    # Tags produit 3414280077060 (plein air, tags OFF non standard)
    "fr:respect-du-bien-etre-animal":    "code_1_plein_air",
    "fr:exploitations-familiales":       "code_1_plein_air",  # indice plein air

    # Tags produit 3435760953124 (au sol, détecté via catégories dans main.py)

    # Nourri sans OGM
    "fr:nourri-sans-ogm":                "nourri_sans_ogm",
    "en:no-gmo":                         "nourri_sans_ogm",
    "fr:sans-ogm":                       "nourri_sans_ogm",
    "en:non-gmo":                        "nourri_sans_ogm",
    "fr:alimentation-100-vegetaux-et-mineraux-et-vitamines": "nourri_sans_ogm",

    # Origine France (label interprofessionnel)
    "fr:origine-france":                 "origine_france",
    "en:origine-france":                 "origine_france",

    # Volailles Fermières du Maine
    "fr:volailles-fermieres-du-maine":   "volailles_maine",
    "en:volailles-fermieres-du-maine":   "volailles_maine",

    # Volailles Fermières de Gascogne
    "fr:volailles-fermieres-de-gascogne": "volailles_gascogne",
    "en:volailles-fermieres-de-gascogne": "volailles_gascogne",
}


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — BASE DE DONNÉES DES LABELS
#
# Chaque critère est un dictionnaire avec :
#   "valeur"  : la donnée affichable (string)
#   "source"  : référence réglementaire exacte
#
# "NS" = Non Spécifié dans le cahier des charges officiel
# ══════════════════════════════════════════════════════════════════════════════

NS = "NS"

LABELS_DB = {

    # ──────────────────────────────────────────────────────────────────────────
    "bio": {
        "nom_complet": "Agriculture Biologique (AB / Bio UE)",
        "type": "Label public UE + France",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale, 100% bio. ≥30% produite à la ferme ou dans la région. Fourrages grossiers obligatoires. OGM et acides aminés de synthèse interdits.",
                "source": "2018/848, Annexe II, Partie II, §1.9.4.2 + Art.11§1"
            },
            "condition_elevage": {
                "valeur": "Au sol, sans cage. ≥1/3 de la surface intérieure en dur avec litière (paille, copeaux, sable ou tourbe). Éclairage & ventilation naturels.",
                "source": "2018/848, Annexe II, Partie II, §1.9.4.4 a)"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire pendant ≥1/3 de leur vie. Accès continu au plus tard à 25 semaines (175 jours).",
                "source": "2018/848, Annexe II, Partie II, §1.9.4.4 d) et e)"
            },
            "exterieur": {
                "valeur": "Parcours végétalisé (végétation variée). Abris et arbustes répartis. Rayon max 150 m depuis les trappes (350 m avec ≥4 abris/ha).",
                "source": "2018/848, §1.9.4.4 h) + 2020/464, Art.16(6)"
            },
            "densite_batiment": {
                "valeur": "6 poules/m²",
                "source": "2020/464, Annexe I, Partie IV, §3"
            },
            "effectif_max_batiment": {
                "valeur": "3 000 / compartiment",
                "source": "2018/848, Annexe II, Partie II, §1.9.4.4 n)"
            },
            "surface_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_site": {
                "valeur": NS,
                "source": NS
            },
            "effectif_par_elevage": {
                "valeur": NS,
                "source": NS
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, végétation variée, abris. Vide et remis en herbe entre cycles.",
                "source": "2018/848, §1.9.4.4 h) + 2020/464, Art.16"
            },
            "surface_parcours": {
                "valeur": "≥ 4 m²/poule (en rotation)",
                "source": "2020/464, Annexe I, Partie IV, §3"
            },
            "vide_sanitaire_batiment": {
                "valeur": "Obligatoire (durée non chiffrée dans le règlement)",
                "source": "2020/464, Art.15"
            },
            "vide_sanitaire_parcours": {
                "valeur": "≥ 7 semaines",
                "source": "Guide de lecture INAO + 2018/848, §1.9.4.4 c)"
            },
            "age_max_poules": {
                "valeur": NS,
                "source": NS
            },
            "age_min_abattage": {
                "valeur": NS,
                "source": NS
            },
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "2018/848"
            },
            "frequence_ramassage": {
                "valeur": NS,
                "source": NS
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "label_rouge_plein_air": {
        "nom_complet": "Label Rouge — Œufs Plein Air",
        "type": "Label public France (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥60% céréales. Sans colorants de synthèse. Sans matières premières animales.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "condition_elevage": {
                "valeur": "Au sol (sans étage), litière. Éclairage & ventilation naturels.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "exterieur": {
                "valeur": "Parcours herbeux et ombragé, entretenu, réimplanté pendant le vide sanitaire.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "surface_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_site": {
                "valeur": NS,
                "source": NS
            },
            "effectif_par_elevage": {
                "valeur": "≤ 12 000",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, ombragé, clôturé, réservé aux pondeuses.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "surface_parcours": {
                "valeur": "≥ 5 m²/poule",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 2 semaines",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "vide_sanitaire_parcours": {
                "valeur": NS,
                "source": NS
            },
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "age_min_abattage": {
                "valeur": NS,
                "source": NS
            },
            "aire_geographique": {
                "valeur": "France entière",
                "source": "Notice technique INAO"
            },
            "frequence_ramassage": {
                "valeur": "Manuel, ≥ 2 fois/jour",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "label_rouge_liberte": {
        "nom_complet": "Label Rouge — Œufs Fermiers (Liberté)",
        "type": "Label public France (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥65% céréales. Sans colorants de synthèse. Sans matières premières animales.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "condition_elevage": {
                "valeur": "Au sol (sans étage), litière. Éclairage & ventilation naturels.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule. Qualification « liberté ».",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "exterieur": {
                "valeur": "Parcours herbeux et arboré, entretenu sans engrais ni herbicides de synthèse.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "surface_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_site": {
                "valeur": NS,
                "source": NS
            },
            "effectif_par_elevage": {
                "valeur": "≤ 12 000",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, arboré, clôturé, entretenu sans intrants de synthèse.",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "surface_parcours": {
                "valeur": "≥ 8 m²/poule",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 3 semaines",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "vide_sanitaire_parcours": {
                "valeur": NS,
                "source": NS
            },
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
            "age_min_abattage": {
                "valeur": NS,
                "source": NS
            },
            "aire_geographique": {
                "valeur": "France entière",
                "source": "Notice technique INAO"
            },
            "frequence_ramassage": {
                "valeur": "Manuel, ≥ 2 fois/jour",
                "source": "Notice technique INAO, arr. 10/10/2012"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "oeufs_de_loue": {
        "nom_complet": "Œufs de Loué (IGP + Label Rouge)",
        "type": "IGP UE + Label Rouge (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥65% céréales. Sans colorants de synthèse. Sans matières premières animales.",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "condition_elevage": {
                "valeur": "Au sol (sans cage ni étage), litière. Éclairage & ventilation naturels.",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule. Qualification « liberté ».",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "exterieur": {
                "valeur": "Parcours herbeux et arboré, entretenu sans engrais ni herbicides de synthèse.",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "surface_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_site": {
                "valeur": NS,
                "source": NS
            },
            "effectif_par_elevage": {
                "valeur": "≤ 6 000 (1 seul bâtiment par exploitation)",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, arboré, clôturé, sans intrants de synthèse.",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "surface_parcours": {
                "valeur": "≥ 8 m²/poule",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 3 semaines",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "vide_sanitaire_parcours": {
                "valeur": NS,
                "source": NS
            },
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
            "age_min_abattage": {
                "valeur": NS,
                "source": NS
            },
            "aire_geographique": {
                "valeur": "Sarthe, Mayenne & cantons limitrophes — rayon ≈80 km autour de Loué",
                "source": "IGP IG/19/97"
            },
            "frequence_ramassage": {
                "valeur": "Manuel, 2 à 3 fois/jour",
                "source": "CDC SYVOL QUALIMAINE n° LA 35-99"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "cocorette": {
        "nom_complet": "Cocorette (Label Rouge Fermier)",
        "type": "Label Rouge (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥70% céréales & sous-produits (dont ≥30% maïs). Sans colorants de synthèse.",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "condition_elevage": {
                "valeur": "Au sol (sans cage ni étage), litière. Nids en bois garnis de paille. Éclairage & ventilation naturels.",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule.",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "exterieur": {
                "valeur": "Parcours arboré, clôturé, avec arbres/haies/taillis pour l'ombre.",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "effectif_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_batiment": {
                "valeur": NS,
                "source": NS
            },
            "surface_max_site": {
                "valeur": NS,
                "source": NS
            },
            "effectif_par_elevage": {
                "valeur": "≤ 3 800",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "parcours_exterieur": {
                "valeur": "Arboré, clôturé, entretenu.",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "surface_parcours": {
                "valeur": "≥ 8 m²/poule",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "vide_sanitaire_batiment": {
                "valeur": NS,
                "source": NS
            },
            "vide_sanitaire_parcours": {
                "valeur": NS,
                "source": NS
            },
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "age_min_abattage": {
                "valeur": NS,
                "source": NS
            },
            "aire_geographique": {
                "valeur": "France entière",
                "source": "CDC ODGPF n° LA 18-98"
            },
            "frequence_ramassage": {
                "valeur": "Ramassage manuel dans les nids en bois",
                "source": "CDC ODGPF n° LA 18-98"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "bleu_blanc_coeur": {
        "nom_complet": "Bleu Blanc Cœur",
        "type": "Label privé nutritionnel",
        "criteres": {
            "alimentation": {
                "valeur": "Ration enrichie en graines de lin (source oméga-3). Aucune autre contrainte spécifique au-delà du code d'élevage de base.",
                "source": "Charte Bleu Blanc Cœur"
            },
            "condition_elevage":      {"valeur": NS, "source": NS},
            "acces_exterieur":        {"valeur": NS, "source": NS},
            "exterieur":              {"valeur": NS, "source": NS},
            "densite_batiment":       {"valeur": NS, "source": NS},
            "effectif_max_batiment":  {"valeur": NS, "source": NS},
            "surface_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_site":       {"valeur": NS, "source": NS},
            "effectif_par_elevage":   {"valeur": NS, "source": NS},
            "parcours_exterieur":     {"valeur": NS, "source": NS},
            "surface_parcours":       {"valeur": NS, "source": NS},
            "vide_sanitaire_batiment":{"valeur": NS, "source": NS},
            "vide_sanitaire_parcours":{"valeur": NS, "source": NS},
            "age_max_poules":         {"valeur": NS, "source": NS},
            "age_min_abattage":       {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "France entière",
                "source": "Charte Bleu Blanc Cœur"
            },
            "frequence_ramassage":    {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "bio_coherence": {
        "nom_complet": "Bio Cohérence",
        "type": "Label privé exigeant (au-delà du bio UE)",
        "criteres": {
            "alimentation": {
                "valeur": "Identique AB + 100% d'origine française pour les matières premières végétales (soja : origine UE autorisée). 100% bio. Ferme entièrement bio obligatoire.",
                "source": "CDC Bio Cohérence v.01/26 (janvier 2026)"
            },
            "condition_elevage": {
                "valeur": "Identique AB. Ferme 100% bio obligatoire.",
                "source": "CDC Bio Cohérence v.01/26"
            },
            "acces_exterieur": {
                "valeur": "Identique AB (≥1/3 de la vie, accès continu au plus tard à 25 semaines).",
                "source": "CDC Bio Cohérence v.01/26 + 2018/848"
            },
            "exterieur": {
                "valeur": "Identique AB.",
                "source": "CDC Bio Cohérence v.01/26 + 2018/848"
            },
            "densite_batiment": {
                "valeur": "6 poules/m²",
                "source": "2020/464, Annexe I, Partie IV, §3"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "CDC Bio Cohérence v.01/26"
            },
            "surface_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_site":       {"valeur": NS, "source": NS},
            "effectif_par_elevage": {
                "valeur": "≤ 12 000",
                "source": "CDC Bio Cohérence v.01/26"
            },
            "parcours_exterieur": {
                "valeur": "Identique AB.",
                "source": "CDC Bio Cohérence v.01/26 + 2018/848"
            },
            "surface_parcours": {
                "valeur": "≥ 4 m²/poule (en rotation)",
                "source": "2020/464, Annexe I, Partie IV, §3"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 2 semaines",
                "source": "CDC Bio Cohérence v.01/26"
            },
            "vide_sanitaire_parcours": {
                "valeur": "≥ 7 semaines",
                "source": "CDC Bio Cohérence v.01/26 + 2018/848"
            },
            "age_max_poules":         {"valeur": NS, "source": NS},
            "age_min_abattage":       {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "France entière",
                "source": "CDC Bio Cohérence v.01/26"
            },
            "frequence_ramassage":    {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "demeter": {
        "nom_complet": "Demeter (Biodynamie)",
        "type": "Label privé biodynamique",
        "criteres": {
            "alimentation": {
                "valeur": "≥50% produite sur le domaine ou en collaboration Demeter voisin. ≥70% d'origine Demeter. ≥20% en grains entiers. Aliments conventionnels interdits. Préparations biodynamiques obligatoires.",
                "source": "Fiche technique Demeter France 2022"
            },
            "condition_elevage": {
                "valeur": "Au sol, sans cage. Bacs de sable et zones ensoleillées obligatoires. 2 coqs pour 100 poules recommandés. Toutes mutilations interdites (bec, etc.).",
                "source": "Fiche technique Demeter France 2022"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire pour les poules pondeuses.",
                "source": "Fiche technique Demeter France 2022"
            },
            "exterieur": {
                "valeur": "Parcours extérieur obligatoire. Zones d'herbage accessibles. Exigences biodynamiques supplémentaires.",
                "source": "Fiche technique Demeter France 2022"
            },
            "densite_batiment": {
                "valeur": "4,4 poules/m²",
                "source": "Fiche technique Demeter France 2022"
            },
            "effectif_max_batiment":  {"valeur": NS, "source": NS},
            "surface_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_site":       {"valeur": NS, "source": NS},
            "effectif_par_elevage":   {"valeur": NS, "source": NS},
            "parcours_exterieur": {
                "valeur": "Identique AB minimum + exigences biodynamiques supplémentaires.",
                "source": "Fiche technique Demeter France 2022"
            },
            "surface_parcours": {
                "valeur": "≥ 4 m²/poule",
                "source": "Fiche technique Demeter France 2022"
            },
            "vide_sanitaire_batiment":{"valeur": NS, "source": NS},
            "vide_sanitaire_parcours":{"valeur": NS, "source": NS},
            "age_max_poules":         {"valeur": NS, "source": NS},
            "age_min_abattage":       {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "France entière",
                "source": "Fiche technique Demeter France 2022"
            },
            "frequence_ramassage":    {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "volailles_maine": {
        "nom_complet": "Volailles Fermières du Maine (IGP + Label Rouge)",
        "type": "IGP UE + Label Rouge (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥60% céréales. Sans colorants de synthèse.",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "condition_elevage": {
                "valeur": "Au sol, sans étage. Litière. Éclairage & ventilation naturels.",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule.",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "exterieur": {
                "valeur": "Parcours herbeux et ombragé, entretenu.",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "surface_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_site":       {"valeur": NS, "source": NS},
            "effectif_par_elevage": {
                "valeur": "≤ 12 000",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, clôturé, réservé aux pondeuses.",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "surface_parcours": {
                "valeur": "≥ 5 m²/poule (plein air) ou ≥ 8 m²/poule (liberté)",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 2 semaines",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "vide_sanitaire_parcours":{"valeur": NS, "source": NS},
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
            "age_min_abattage":       {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Sarthe, Mayenne et départements limitrophes",
                "source": "IGP Volailles du Maine"
            },
            "frequence_ramassage": {
                "valeur": "Manuel, ≥ 2 fois/jour",
                "source": "CDC INAO LA 03/99 / LA 04/02"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    "volailles_gascogne": {
        "nom_complet": "Volailles Fermières de Gascogne (IGP + Label Rouge)",
        "type": "IGP UE + Label Rouge (INAO)",
        "criteres": {
            "alimentation": {
                "valeur": "100% végétale & minérale. ≥60% céréales (dont ≥30% maïs). Sans colorants de synthèse.",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "condition_elevage": {
                "valeur": "Au sol, sans étage. Litière. Éclairage & ventilation naturels.",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "acces_exterieur": {
                "valeur": "Obligatoire. Accès libre de 11h au crépuscule.",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "exterieur": {
                "valeur": "Parcours herbeux et ombragé, entretenu.",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "effectif_max_batiment": {
                "valeur": "6 000",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "surface_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_site":       {"valeur": NS, "source": NS},
            "effectif_par_elevage": {
                "valeur": "≤ 12 000",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "parcours_exterieur": {
                "valeur": "Herbeux, clôturé, réservé aux pondeuses.",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "surface_parcours": {
                "valeur": "≥ 5 m²/poule",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "vide_sanitaire_batiment": {
                "valeur": "≥ 2 semaines",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "vide_sanitaire_parcours":{"valeur": NS, "source": NS},
            "age_max_poules": {
                "valeur": "≤ 72 semaines",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
            "age_min_abattage":       {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Gers, Landes, Hautes-Pyrénées, Lot-et-Garonne et dép. limitrophes",
                "source": "IGP Volailles de Gascogne"
            },
            "frequence_ramassage": {
                "valeur": "Manuel, ≥ 2 fois/jour",
                "source": "CDC INAO Volailles Fermières de Gascogne"
            },
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE 1 — Plein air
    # Source : Règlement (CE) n° 589/2008, Annexe II
    # ──────────────────────────────────────────────────────────────────────────
    "code_1_plein_air": {
        "nom_complet": "Plein Air (Code 1)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":            {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Au sol, sans cage. Accès permanent à un parcours extérieur pendant la journée.",
                "source": "Règlement (CE) n° 589/2008, Annexe II"
            },
            "acces_exterieur": {
                "valeur": "Accès permanent au plein air pendant la journée.",
                "source": "Règlement (CE) n° 589/2008, Annexe II"
            },
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "Règlement (CE) n° 589/2008, Annexe II"
            },
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "≥ 4 m²/poule",
                "source": "Règlement (CE) n° 589/2008, Annexe II"
            },
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Règlement (CE) n° 589/2008"
            },
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE 2 — Au sol
    # Source : Directive 1999/74/CE ; Règlement (CE) n° 589/2008
    # ──────────────────────────────────────────────────────────────────────────
    "code_2_sol": {
        "nom_complet": "Élevage au sol (Code 2)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":            {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Au sol, sans cage. Élevage en bâtiment fermé avec litière.",
                "source": "Directive 1999/74/CE"
            },
            "acces_exterieur": {
                "valeur": "Aucun accès au plein air imposé.",
                "source": "Directive 1999/74/CE"
            },
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "≤ 9 poules/m²",
                "source": "Directive 1999/74/CE"
            },
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "Aucune surface extérieure imposée.",
                "source": "Directive 1999/74/CE"
            },
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Directive 1999/74/CE"
            },
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CODE 3 — Cage aménagée
    # Source : Directive 1999/74/CE
    # ──────────────────────────────────────────────────────────────────────────
    "code_3_cage": {
        "nom_complet": "Cage aménagée (Code 3)",
        "type": "Code réglementaire UE",
        "criteres": {
            "alimentation":            {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Élevage en cage aménagée. 750 cm² par poule (dont 600 cm² utilisables). Nid collectif, perchoir (15 cm/poule) et zone de litière obligatoires.",
                "source": "Directive 1999/74/CE, Art. 6"
            },
            "acces_exterieur": {
                "valeur": "Aucun accès au plein air.",
                "source": "Directive 1999/74/CE"
            },
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment": {
                "valeur": "750 cm²/poule (dont 600 cm² utilisables)",
                "source": "Directive 1999/74/CE, Art. 6"
            },
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours": {
                "valeur": "Aucune surface extérieure.",
                "source": "Directive 1999/74/CE"
            },
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "Tout territoire UE",
                "source": "Directive 1999/74/CE"
            },
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # ŒUFS DE FRANCE
    # Label interprofessionnel géré par CNPO (Comité National pour la promotion
    # de l'Œuf). Garantit l'origine France uniquement, pas de critères d'élevage
    # spécifiques au-delà de la réglementation UE en vigueur.
    # Source : Cahier des charges Œufs de France / CNPO
    # ──────────────────────────────────────────────────────────────────────────
    "oeufs_de_france": {
        "nom_complet": "Œufs de France",
        "type": "Label interprofessionnel",
        "criteres": {
            "alimentation":            {"valeur": NS, "source": NS},
            "condition_elevage": {
                "valeur": "Conforme à la réglementation UE en vigueur (code d'élevage apposé sur l'œuf).",
                "source": "Cahier des charges Œufs de France / CNPO"
            },
            "acces_exterieur":         {"valeur": NS, "source": NS},
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment":        {"valeur": NS, "source": NS},
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours":        {"valeur": NS, "source": NS},
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "France",
                "source": "Cahier des charges Œufs de France / CNPO"
            },
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # NOURRI SANS OGM
    # Garantit uniquement que l'alimentation des animaux est exempte d'OGM.
    # Pas d'exigence sur les conditions d'élevage.
    # Source : Règlement (CE) n°1829/2003 + cahiers des charges privés (Agri-Confiance, etc.)
    # ──────────────────────────────────────────────────────────────────────────
    "nourri_sans_ogm": {
        "nom_complet": "Nourri sans OGM",
        "type": "Label privé / allégation",
        "criteres": {
            "alimentation": {
                "valeur": "Alimentation des animaux sans OGM (≥ 0,9% de seuil de tolérance UE).",
                "source": "Règlement (CE) n°1829/2003 + cahier des charges privé"
            },
            "condition_elevage":       {"valeur": NS, "source": NS},
            "acces_exterieur":         {"valeur": NS, "source": NS},
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment":        {"valeur": NS, "source": NS},
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours":        {"valeur": NS, "source": NS},
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique":       {"valeur": NS, "source": NS},
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

    # ──────────────────────────────────────────────────────────────────────────
    # ORIGINE FRANCE
    # Label interprofessionnel garantissant uniquement l'origine française
    # du produit. Pas d'exigence sur les conditions d'élevage.
    # Source : Décret n°2002-1120 relatif à l'indication de provenance
    # ──────────────────────────────────────────────────────────────────────────
    "origine_france": {
        "nom_complet": "Origine France",
        "type": "Label interprofessionnel",
        "criteres": {
            "alimentation":            {"valeur": NS, "source": NS},
            "condition_elevage":       {"valeur": NS, "source": NS},
            "acces_exterieur":         {"valeur": NS, "source": NS},
            "exterieur":               {"valeur": NS, "source": NS},
            "densite_batiment":        {"valeur": NS, "source": NS},
            "effectif_max_batiment":   {"valeur": NS, "source": NS},
            "surface_max_batiment":    {"valeur": NS, "source": NS},
            "surface_max_site":        {"valeur": NS, "source": NS},
            "effectif_par_elevage":    {"valeur": NS, "source": NS},
            "parcours_exterieur":      {"valeur": NS, "source": NS},
            "surface_parcours":        {"valeur": NS, "source": NS},
            "vide_sanitaire_batiment": {"valeur": NS, "source": NS},
            "vide_sanitaire_parcours": {"valeur": NS, "source": NS},
            "age_max_poules":          {"valeur": NS, "source": NS},
            "age_min_abattage":        {"valeur": NS, "source": NS},
            "aire_geographique": {
                "valeur": "France",
                "source": "Décret n°2002-1120 relatif à l'indication de provenance"
            },
            "frequence_ramassage":     {"valeur": NS, "source": NS},
        }
    },

}  # fin LABELS_DB


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 3 — FONCTION DE SÉLECTION
#
# Logique : pour chaque critère, on retourne la valeur du label
# qui apparaît en premier dans PRIORITY_ORDER (du plus exigeant
# au moins exigeant). Si aucun label reconnu n'a de valeur pour
# ce critère, on retourne NS.
# ══════════════════════════════════════════════════════════════════════════════

# Ordre de priorité : du label le plus exigeant au moins exigeant
# Cet ordre peut être affiné critère par critère dans une version future
PRIORITY_ORDER = [
    "demeter",
    "bio_coherence",
    "bio",
    "oeufs_de_loue",
    "cocorette",
    "label_rouge_liberte",
    "label_rouge_plein_air",
    "volailles_maine",
    "volailles_gascogne",
    "bleu_blanc_coeur",
    "oeufs_de_france",
    "origine_france",
    "nourri_sans_ogm",
    "code_1_plein_air",
    "code_2_sol",
    "code_3_cage",
]


def detect_labels(raw_labels_string: str) -> list[str]:
    """
    Prend la chaîne brute de labels Open Food Facts (ex: "en:organic, fr:label-rouge")
    et retourne la liste des clés internes reconnues (ex: ["bio", "label_rouge_plein_air"]).
    """
    if not raw_labels_string:
        return []

    detected = []
    # On normalise : minuscules, on découpe par virgule, on enlève les espaces
    tokens = [t.strip().lower() for t in raw_labels_string.split(",")]

    for token in tokens:
        if token in LABEL_MAPPING:
            internal_key = LABEL_MAPPING[token]
            if internal_key not in detected:
                detected.append(internal_key)

    return detected


def get_best_guarantees(detected_labels: list[str]) -> dict:
    """
    Prend une liste de clés internes de labels (ex: ["bio", "label_rouge_plein_air"])
    et retourne un dictionnaire avec, pour chaque critère, la garantie
    la plus exigeante trouvée parmi les labels détectés.

    Retourne aussi la liste des labels reconnus avec leur nom complet.
    """
    if not detected_labels:
        return {
            "labels_reconnus": [],
            "garanties": {}
        }

    # On filtre uniquement les labels présents dans notre base
    labels_valides = [l for l in detected_labels if l in LABELS_DB]

    if not labels_valides:
        return {
            "labels_reconnus": [],
            "garanties": {}
        }

    # Noms complets des labels reconnus pour l'affichage
    labels_reconnus = [
        {"cle": l, "nom": LABELS_DB[l]["nom_complet"], "type": LABELS_DB[l]["type"]}
        for l in labels_valides
    ]

    # Pour chaque critère, on cherche la meilleure valeur
    # selon l'ordre de priorité défini dans PRIORITY_ORDER
    tous_criteres = list(next(iter(LABELS_DB.values()))["criteres"].keys())
    garanties = {}

    for critere in tous_criteres:
        meilleure_valeur = NS
        meilleure_source = NS
        meilleur_label = None

        # On parcourt les labels dans l'ordre de priorité
        for label_prioritaire in PRIORITY_ORDER:
            if label_prioritaire in labels_valides:
                valeur = LABELS_DB[label_prioritaire]["criteres"][critere]["valeur"]
                source = LABELS_DB[label_prioritaire]["criteres"][critere]["source"]
                if valeur != NS:
                    meilleure_valeur = valeur
                    meilleure_source = source
                    meilleur_label = LABELS_DB[label_prioritaire]["nom_complet"]
                    break  # On s'arrête dès qu'on trouve une valeur non-NS

        garanties[critere] = {
            "valeur": meilleure_valeur,
            "source": meilleure_source,
            "label_source": meilleur_label,
        }

    return {
        "labels_reconnus": labels_reconnus,
        "garanties": garanties,
    }
