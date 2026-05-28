# Guide de contribution — Transparence Œufs

Ce fichier décrit les règles à suivre pour garder le code propre et éviter de répéter
les erreurs passées. Il s'adresse aux humains **comme aux assistants IA** (Claude,
ChatGPT, etc.).

> **Si vous utilisez un assistant IA via une interface web** : copiez-collez ce fichier
> au début de la conversation et demandez à l'IA de le respecter avant toute modification.

---

## 1. Vue d'ensemble du projet

Application web (pas une app mobile native) qui scanne le code-barres d'un produit
(œufs ou volaille), interroge [Open Food Facts](https://world.openfoodfacts.org/), et
affiche les **garanties réelles** imposées par chaque label d'après les textes officiels.

| Fichier | Rôle | À modifier quand… |
|---|---|---|
| `main.py` | API FastAPI, endpoint `/scan/{barcode}`, sert `index.html` | logique serveur, détection du type de produit |
| `index.html` | Frontend (page unique, scan caméra) | interface, affichage |
| `eggs.py` | Données labels œufs | nouveau label/critère œuf |
| `chicken.py` | Données labels volaille | nouveau label/critère volaille |
| `labels_core.py` | Logique commune de détection/agrégation | **rarement** — code partagé |

---

## 2. Règles d'or (à ne jamais enfreindre)

### Git & fichiers

1. **Ne jamais committer de gros fichiers binaires ni d'installeurs.**
   Le dossier `Git/` (installeur Git pour Windows, 426 Mo) a été committé par erreur
   dans le passé. Vérifiez `git status` avant chaque commit : seuls les fichiers du
   projet (`.py`, `.html`, `.md`, configs) doivent apparaître.
2. **Respecter le `.gitignore`.** Ne pas committer `__pycache__/`, `.venv/`, `Git/`.
3. **Tous les fichiers texte sont en UTF-8.** Ne jamais enregistrer en UTF-16
   (`requirements.txt` et `render.yaml` l'étaient et étaient illisibles par pip/Render).
   Sous Windows, vérifier l'encodage de l'éditeur.

### Code Python

4. **Les requêtes réseau ont toujours un `timeout` et un `try/except`.**
   `requests.get(url, timeout=10)` + gestion d'erreur. Sans ça, l'API plante (500) si
   Open Food Facts est lent ou injoignable.
5. **Ne pas dupliquer la logique.** `detect_labels` et `get_best_guarantees` vivent dans
   `labels_core.py`. `eggs.py` et `chicken.py` ne font qu'appeler ces fonctions avec
   leurs propres tables de données. Ne pas recopier la logique.
6. **Les données vivent avec leur module.** Ex. : `ELEVAGE_CODES` est défini dans
   `eggs.py`/`chicken.py`, pas codé en dur dans `main.py`. Si vous ajoutez un label,
   tout se passe dans le module concerné.
7. **Épingler les dépendances.** Dans `requirements.txt`, garder des bornes de version
   (ex. `fastapi>=0.110,<1.0`). Ne pas laisser un nom de paquet sans version.

### Frontend

8. **Pas de duplication de logique JS.** Utiliser les helpers existants
   (`setBusy`, `setStatus`, `estCertifieProduit`) plutôt que recopier le code.
9. **Le scan caméra exige HTTPS ou `localhost`.** En testant par IP locale, la caméra
   peut être bloquée par le navigateur — c'est normal, utiliser la saisie manuelle.

---

## 3. Conventions

- **Langue** : commentaires, messages de commit, noms de variables métier en **français**
  (cohérent avec l'existant : `produits`, `garanties`, `lancerRecherche`…).
- **Commentaires** : expliquer le *pourquoi*, pas le *quoi*. Pas de commentaire évident.
- **Messages de commit** : courts, à l'impératif, en français. Une ligne de titre + 
  détails en liste si besoin.

---

## 4. Comment ajouter un label (cas le plus fréquent)

Exemple : ajouter un nouveau label d'œuf.

1. Dans `eggs.py` → `LABEL_MAPPING` : associer le(s) code(s) Open Food Facts
   (ex. `"fr:nouveau-label"`) à une clé interne (ex. `"nouveau_label"`).
2. Dans `eggs.py` → `LABELS_DB` : ajouter une entrée `"nouveau_label"` avec
   `nom_complet`, `type`, et les `criteres` (chaque critère a `valeur` + `source`).
   Utiliser `NS` si un critère n'est pas spécifié par le cahier des charges.
3. Dans `eggs.py` → `PRIORITY_ORDER` : insérer la clé au bon rang (du plus exigeant
   au moins exigeant).
4. Si c'est un système d'élevage, l'ajouter à `ELEVAGE_CODES`.
5. **Toujours citer la source réglementaire** (règlement UE, cahier des charges INAO,
   IGP…) dans le champ `source` et l'en-tête du fichier.

La même procédure s'applique à `chicken.py`.

---

## 5. Vérifications avant de committer

```bash
# 1. Les modules s'importent sans erreur
python3 -c "from main import app"

# 2. Aucun fichier indésirable n'est suivi
git status            # ne doit lister que des fichiers du projet

# 3. Lancer l'app en local et tester un scan
uvicorn main:app --host 0.0.0.0 --port 10000
```

Ne jamais marquer une tâche comme terminée si l'app ne démarre pas ou si un scan plante.

---

## 6. Principe directeur du projet

> N'afficher que les garanties **explicitement imposées** par les textes officiels.
> Si un critère n'est pas spécifié dans le cahier des charges, c'est `NS` (Non Spécifié) —
> ne jamais inventer ni supposer une garantie. La crédibilité de l'app repose là-dessus.
