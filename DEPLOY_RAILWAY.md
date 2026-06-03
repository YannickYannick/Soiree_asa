# Déploiement Railway — guide complet (recommencer)

## Étape 1 — GitHub (déjà fait)

Repo : `https://github.com/YannickYannick/Soiree_asa`

## Étape 2 — Projet Railway

1. [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub** → **`Soiree_asa`** (pas un autre repo)
3. **Root Directory** : vide (racine, pas `frontend`)

## Étape 3 — PostgreSQL

1. **+ New** → **Database** → **PostgreSQL**

## Étape 4 — Variables (service Web Django)

| Variable | Valeur |
|----------|--------|
| `SECRET_KEY` | clé longue aléatoire |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ton-domaine.up.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://ton-domaine.up.railway.app` |
| `DATABASE_URL` | **Add Reference** → Postgres → `DATABASE_URL` |
| `RAILWAY_ENVIRONMENT` | `production` |
| `MISE_PYTHON_GITHUB_ATTESTATIONS` | `false` (secours si build Python échoue) |

## Étape 5 — Domaine

Service Web → **Settings** → **Networking** → **Generate Domain**

Mettre à jour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` avec cette URL.

## Étape 6 — Attendre deploy vert

Le build doit afficher : Python détecté → `pip install` → **Success**.

Fichiers du repo pour le build :
- `mise.toml` — Python 3.12.8 sans attestations GitHub
- `runtime.txt` — `python-3.12.8`
- `Procfile` — migrate + collectstatic + gunicorn

## Étape 7 — Données initiales

### Option A — Interface Railway

Service Web → **Settings** → commande one-shot ou Console :

```bash
python manage.py migrate --noinput
python manage.py shell -c "from events.views import get_or_create_default_event; get_or_create_default_event()"
```

### Option B — SSH (CLI)

```powershell
cd "c:\Users\yannb\Documents\1. Programmation\6. soirée asa"
railway login
railway link
railway ssh
```

Puis les mêmes commandes `python manage.py ...` dans le shell.

**SSH avec IDs (nouvelle syntaxe CLI) :**

```powershell
railway ssh -p a32a6714-e6db-4f25-b94d-68b4f8dfbea2 -e fd7f19c6-3f95-4366-95b7-6a712e29c877 -s 1fae085c-e86e-4cb7-b1d0-1e9290ac4311
```

> L’ancienne syntaxe `--project=...` ne fonctionne plus sur Railway CLI v4.

**SSH ne marche que si :**
- tu es connecté (`railway login`)
- le dernier déploiement est **Success** (pas Failed)

## Dépannage

| Problème | Solution |
|----------|----------|
| `Unauthorized` | `railway login` |
| `mise` / attestations Python | `mise.toml` + variable `MISE_PYTHON_GITHUB_ATTESTATIONS=false` |
| `npm ci` | Mauvais repo ou Root Directory = `frontend` |
| DisallowedHost | Corriger `ALLOWED_HOSTS` |
| CSRF | `CSRF_TRUSTED_ORIGINS` avec `https://` |
