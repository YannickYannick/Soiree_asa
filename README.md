# Afro Night Event Manager

Application web de gestion d'événements nightlife récurrents, conçue pour l'organisation de soirées payantes en club parisien.

## Fonctionnalités

### Module 1 — Simulation financière dynamique
- Sliders interactifs : pax attendus, dépense bar moyenne, % TPE, staff, VIP
- Calcul temps réel : recettes, trésorerie fin de soirée, résultat net
- Frise temporelle à double échelle (pré-soirée + nuit)
- 3 scénarios comparatifs (Pessimiste / Neutre / Optimiste)

### Module 2 — Calendrier de tarification avec stocks
- 5 phases de prix : Super Early Bird → Sur place
- Gestion des stocks par type (solo, girls ×4, duo mixte)
- Visualisation frise des phases avec progression

### Module 3 — Gestion des tables VIP
- 10 slots configurables
- Formules : 250€ à 1500€
- Commission promoteur éditable
- Option ressert ×2

### Module 4 — Stratégie Instagram
- 14 publications planifiées sur 24 jours
- Filtrage par phase et type (Post/Reel/Story)
- Verrouillage en attente d'accord venue INWEE

### Module 5 — Budget consolidé & P&L
- Lignes éditables en temps réel
- Séparation : dépenses fixes (avant/nuit) / humaines (post)
- Métriques clés : trésorerie fin de soirée, résultat net, marge

### Module 6 — Suivi des ventes
- Courbes cumulées filles/garçons
- Barres journalières
- Indicateur de ratio genre

## Installation

```bash
# Cloner le repository
cd "c:\Users\yannb\Documents\1. Programmation\6. soirée asa"

# Créer un environnement virtuel (optionnel)
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur
python manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000/

## Stack technique

- **Backend** : Django 5.x
- **Frontend** : Tailwind CSS (CDN) + Alpine.js
- **Charts** : Chart.js
- **Base de données** : SQLite (dev) / PostgreSQL (prod)

## Cas d'usage

Soirée **Afro Night** (amapiano × zouk × commercial)
- Lieu : La Péniche, Paris 5e
- Capacité : 300 personnes
- Modèle : entrées + tables VIP + bar géré par l'organisateur

## Règles métier intégrées

1. **Accord INWEE obligatoire** — Publications verrouillées tant que non approuvées
2. **Ratio femmes ≥ 45%** — Alerte si ratio critique
3. **Pas de deal groupe masculin** — Hommes paient le plein tarif
4. **TPE INWEE 6,5%** — Commission sur encaissements CB
5. **SACEM** — Montant fixe (3,9% × 4800€ TTC = 187€)
6. **Résiliation < 45 jours** — 4800€ forfaitaires

## Contexte contractuel

- **Venue** : La Péniche, 02 quai de la Tournelle, 75005 Paris
- **Opérateur** : INWEE — Groupe Atmosphère
- **Contact** : Matthieu Bouaziz — matthieu@inwee.fr
- **Client** : Association ODELYIA

---

*Développé pour la soirée Afro Night — Édition 20 juin 2026*
