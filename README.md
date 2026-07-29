# LOKKO — Prototype MVP

Marketplace de mode de luxe avec IA, enchères privées et système d'échange.

## Structure du projet

```
lokko-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py          # Point d'entrée FastAPI
│   │   ├── models.py        # Modèles SQLAlchemy (User, Product, Bid, etc.)
│   │   ├── database.py      # Configuration SQLite
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── ai_engine.py     # Moteur de recommandation IA
│   │   └── routes/
│   │       ├── users.py     # Routes utilisateurs
│   │       ├── products.py  # Routes produits (feed, dressing)
│   │       └── bids.py      # Routes enchères + swipe
│   ├── requirements.txt
│   └── .venv/               # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.js         # Interface React complète
│   │   ├── App.css        # Design premium (noir/or/serif)
│   │   └── index.js       # Point d'entrée React
│   └── package.json
└── README.md
```

## Fonctionnalités implémentées

### ✅ Backend (FastAPI)
- **Modèles de données complets** : User, Product, Bid, Exchange, SwipeHistory, TrustLog, AILookCard
- **Système d'enchères privées** avec règle des 70%
- **Timer en cascade 12h** pour les offres
- **Moteur IA de recommandation** basé sur l'historique de swipe
- **Score de confiance** dynamique
- **Safe Haven Rule** pour les pièces suspectes
- **Base de données SQLite** (passe à PostgreSQL en prod)

### ✅ Frontend (React)
- **Écran de swipe plein écran** (une pièce par écran)
- **Prix masqué** (apparaît après 3s ou clic sur l'œil)
- **Système d'offre privée** avec modale et validation
- **Feed avec insertion de "Look du Jour" IA** tous les 10 swipes
- **Navigation par onglets** : Feed, Dressing, Offres, Échange
- **Design premium** : noir/or/serif, espace négatif, animations
- **Données de démonstration** intégrées (6 produits de luxe)

## Pour lancer le prototype

```bash
# Terminal 1 - Backend
cd backend
.venv/bin/python -m uvicorn app.main:app --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

Le frontend se lance sur `http://localhost:3000` avec des données de démo intégrées.

## Prochaines étapes

1. **Connecter le frontend au backend** (remplacer les données mock par des appels API)
2. **Ajouter l'authentification** (JWT + invitation bêta)
3. **Améliorer l'IA** (modèles de recommandation, authentification visuelle)
4. **Système de paiement** (Stripe pour les 8% de commission)
5. **Déploiement** (Railway pour le backend, Vercel pour le frontend)

## Stack technique
- **Backend**: FastAPI + SQLAlchemy + SQLite (→ PostgreSQL)
- **Frontend**: React 18 + CSS custom (Playfair Display + Inter)
- **IA**: Moteur de scoring basé sur l'historique (→ modèles ML en V2)
- **Déploiement**: Railway + Vercel (ou Render)