# Déploiement Railway — Soirée ASA

## 1. Créer le projet Railway

1. [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub** → repo `YannickYannick/Soiree_asa`
3. Railway crée un service **Web** automatiquement

## 2. Ajouter PostgreSQL

1. Dans le projet → **+ New** → **Database** → **PostgreSQL**
2. Clique sur le service Postgres → onglet **Variables** ou **Connect**
3. Copie `DATABASE_URL` (ou lie la variable au service web, voir étape 3)

## 3. Variables d'environnement (service Web)

Onglet **Variables** du service Django :

| Variable | Valeur |
|----------|--------|
| `SECRET_KEY` | Génère une clé longue (ex. `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ton-app.up.railway.app` (remplace par ton domaine Railway) |
| `CSRF_TRUSTED_ORIGINS` | `https://ton-app.up.railway.app` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (référence au service Postgres) |
| `RAILWAY_ENVIRONMENT` | `production` |

**Référence Postgres :** dans Variables, clique **Add Reference** → choisis le service PostgreSQL → `DATABASE_URL`.

## 4. Domaine public

1. Service Web → **Settings** → **Networking** → **Generate Domain**
2. Mets à jour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` avec cette URL exacte (sans slash final).

## 5. Premier déploiement

Le `Procfile` lance automatiquement :
- `migrate`
- `collectstatic`
- `gunicorn`

## 6. Données initiales (une fois)

Railway → service Web → **Settings** → shell ou **Run command** :

```bash
python manage.py shell -c "from events.views import get_or_create_default_event; get_or_create_default_event()"
```

Puis ouvre `/event/1/instagram/regenerate/` pour recharger le planning Instagram (ou refais la commande shell de régénération).

## 7. Superuser admin (optionnel)

```bash
python manage.py createsuperuser
```

Accès admin : `https://ton-app.up.railway.app/admin/`

## Dépannage

- **Application failed to respond** : vérifie `ALLOWED_HOSTS` et les logs (Deployments → View logs).
- **Build échoue sur weasyprint** : retirer `weasyprint` de `requirements.txt` si tu n’utilises pas l’export PDF.
- **Page sans CSS admin** : relancer un deploy (collectstatic).
