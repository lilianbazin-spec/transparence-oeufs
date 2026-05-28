# Transparence Œufs

Application web qui scanne le code-barres d'un produit (œufs ou volaille), interroge
[Open Food Facts](https://world.openfoodfacts.org/), et affiche les **garanties réelles**
imposées par chaque label (Bio, Label Rouge, IGP, etc.) d'après les textes officiels.

C'est un site web pensé pour mobile : on l'ouvre dans le navigateur d'un téléphone et on
utilise l'appareil photo pour scanner le code-barres. Il n'y a pas d'application native à installer.

## Stack

- **Backend** : FastAPI (Python), sert aussi le frontend.
- **Frontend** : `index.html` (page unique, scan caméra via `html5-qrcode`).
- **Données** : `eggs.py` et `chicken.py` (bases de labels), logique commune dans `labels_core.py`.

## Lancer en local

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000
```

Puis ouvrir <http://localhost:10000/>. Depuis un téléphone sur le même réseau,
utiliser l'adresse IP de la machine (ex. `http://192.168.1.20:10000/`).

> Le scan caméra nécessite un contexte sécurisé (HTTPS ou `localhost`). En accès par IP
> sur le réseau local, certains navigateurs bloqueront la caméra : saisie manuelle du
> code-barres dans ce cas.

## Utilisation

1. Saisir un code-barres, ou appuyer sur 📷 pour le scanner.
2. Le résultat affiche les labels reconnus et, pour chaque critère, la garantie la plus
   exigeante avec sa source réglementaire.
3. On peut comparer deux produits côte à côte.

## Déploiement

Configuré pour [Render](https://render.com/) via `render.yaml` (build : `pip install`,
start : `uvicorn` sur le port `10000`). Déploiement automatique au push.

## Structure

| Fichier | Rôle |
|---|---|
| `main.py` | API FastAPI, endpoint `/scan/{barcode}`, sert `index.html` |
| `index.html` | Frontend mobile-first (scan, comparaison) |
| `eggs.py` | Base de labels œufs (tables de données) |
| `chicken.py` | Base de labels volaille (tables de données) |
| `labels_core.py` | Logique commune de détection et d'agrégation des garanties |
