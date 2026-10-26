# Lokko — UI/UX Spécification Complète

> Document de référence design pour l'application mobile Lokko.  
> Stack : React Native · Marché cible : Tunisie (TND) → GCC (AED)

---

## 1. Philosophie Design

### Principe fondateur
L'interface doit **faire ressentir la mode avant de la vendre**. Le design est minimaliste, rapide, et sensoriel — comme feuilleter un magazine de mode sur son téléphone.

### Valeurs UX
| Valeur | Traduction concrète |
|--------|-------------------|
| **Vitesse** | Chaque action en < 1 tap. Feed qui se charge en < 200ms. |
| **Confiance** | Badges vendeur visibles. Prix marché IA toujours présent. |
| **Plaisir** | Animations fluides. Micro-interactions sur chaque swipe. |
| **Clarté** | Une seule action principale par écran. Zéro friction pour acheter. |

### Identité visuelle
```
Palette principale :
  Noir profond   #0D0D0D  — fond principal (nuit mode)
  Blanc cassé    #F5F0EB  — textes, surfaces claires
  Or champagne   #C9A84C  — accent premium, CTA principaux
  Gris anthracite #2A2A2A  — surfaces secondaires, cartes
  Rouge alerte   #E63946  — erreurs, alertes prix, urgence

Typographie :
  Display  → Playfair Display (élégant, mode)
  Corps    → Inter (lisible, moderne)
  Labels   → JetBrains Mono (prix, badges, données)

Bordures : radius = 16px (cartes) / 50px (boutons pill)
Ombres  : légères, diffuses — jamais lourdes
```

---

## 2. Navigation Principale

### Structure (Bottom Tab Bar)
```
┌──────────────────────────────────────────┐
│                                          │
│              CONTENU ÉCRAN               │
│                                          │
├──────┬──────┬──────┬──────┬──────────────┤
│ Feed │Recher│ Vend │Dress │   Profil     │
│  🏠  │  🔍  │  ➕  │  👗  │    👤        │
└──────┴──────┴──────┴──────┴──────────────┘
```

| Tab | Icône | Fonction |
|-----|-------|----------|
| **Feed** | 🏠 | Flux principal de swipe |
| **Recherche** | 🔍 | Recherche + filtres + catégories |
| **Vendre** | ➕ | Créer une annonce (CTA central) |
| **Dressing** | 👗 | Mes articles en vente + en cours |
| **Profil** | 👤 | Compte, achats, favoris, paramètres |

### Règle tab central (Vendre)
- Bouton ➕ plus grand que les autres (56px vs 44px)
- Couleur or champagne `#C9A84C` — seul élément coloré de la nav bar
- Tap → ouvre directement la caméra

---

## 3. Écran Feed — Cœur de l'Application

### Layout carte article
```
┌─────────────────────────────────────────┐
│                                         │
│         PHOTO ARTICLE (90% écran)       │
│              (plein format)             │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ ⏱ 08:42 restant    🔁 Cycle 2/3│    │  ← barre état enchère
│  └─────────────────────────────────┘    │
│                                         │
│  [▓▓▓▓▓▓▓░░░]  62% du temps écoulé     │  ← progress bar
│                                         │
│  Air Max 90 Blanches         ★ Vérifié  │  ← titre + badge trust
│  Nike · Pointure 42 · Très bon état     │
│                                         │
│  ░░░ [SILENCE VISUEL 3s] ░░░            │  ← prix masqué au chargement
│       → révèle : 145 TND                │
│                                         │
│  [❤ LIKE]    [💛 OFFRIR]    [⬆ ACHETER]│  ← 3 actions swipe
└─────────────────────────────────────────┘
```

### Silence Visuel (feature signature)
- À l'affichage de chaque carte : le prix est **masqué derrière un fondu flou** pendant **3 secondes**
- Pendant ces 3s : l'utilisateur juge uniquement sur la photo et le style
- Après 3s : le prix apparaît avec une animation de dévoilement (slide-up + fade-in)
- **Objectif** : forcer le jugement esthétique avant le jugement prix

```
Animation Silence Visuel :
  t=0s   → Prix = bloc flou (#2A2A2A) avec "..." 
  t=3s   → Blur disparaît, prix slide-up depuis le bas
  Durée  → 400ms ease-out
  Son    → léger "reveal" sonore (optionnel, OFF par défaut)
```

### Gestes de swipe
```
← Glisser gauche   = SKIP (pas intéressé)
   Animation : carte part à gauche, icône ✕ rouge, rebond léger

→ Glisser droite   = LIKE (sauvegarder dans favoris)
   Animation : carte part à droite, icône ♥ rose, particules cœur

↑ Glisser haut     = ACHETER (intention achat forte)
   Animation : carte monte, icône 🛒 or, confettis dorés
   → Ouvre directement la modale de paiement

↓ Glisser bas      = DÉTAILS (voir plus d'infos)
   Animation : carte descend légèrement, drawer s'ouvre par-dessus
```

### Seuils de déclenchement swipe
```javascript
// Seuil minimal pour valider le geste (px)
SWIPE_THRESHOLD_X = 80   // gauche/droite
SWIPE_THRESHOLD_Y = 100  // haut/bas

// Rotation de la carte pendant le glissement
rotation = (deltaX / screenWidth) * 15  // max 15 degrés
```

### Indicateurs visuels en temps réel (Feed)
```
┌─────────────────────────────────────────┐
│  Top droite : ⏱ Timer compte à rebours  │
│  → Rouge si < 2h restantes              │
│  → Orange si < 6h restantes             │
│  → Blanc sinon                          │
│                                         │
│  Badge cycle : 🔁 Cycle 2/3             │
│  → Rappel que c'est la 2ème mise        │
│  → Prix a déjà baissé vs cycle 1        │
│                                         │
│  Barre progression : pleine = temps écoulé│
│  → Vert > 50% restant                  │
│  → Orange 20-50% restant               │
│  → Rouge < 20% restant                 │
└─────────────────────────────────────────┘
```

---

## 4. Écran Création d'Annonce (Vendre)

### Étape 1 — Capture photo
```
┌─────────────────────────────────────────┐
│              VISEUR CAMÉRA              │
│                                         │
│    ┌───────────────────────────────┐    │
│    │                               │    │
│    │    [ Zone de cadrage IA ]     │    │
│    │    "Centre l'article ici"     │    │
│    │                               │    │
│    └───────────────────────────────┘    │
│                                         │
│  Conseils :                             │
│  ✓ Fond neutre (blanc/gris)             │
│  ✓ Bonne lumière                        │
│  ✓ Article à plat ou porté              │
│                                         │
│  [📷 PRENDRE LA PHOTO]                  │
│  [🖼 Choisir depuis galerie]            │
└─────────────────────────────────────────┘
```

### Étape 2 — Analyse IA (loading state)
```
┌─────────────────────────────────────────┐
│                                         │
│         [Photo prise]                   │
│                                         │
│    ┌───────────────────────────────┐    │
│    │  ✨ L'IA analyse ton article  │    │
│    │                               │    │
│    │  [████████░░] 80%             │    │
│    │                               │    │
│    │  → Détection marque...  ✓    │    │
│    │  → Estimation prix...   ✓    │    │
│    │  → Vérification état... ⏳   │    │
│    └───────────────────────────────┘    │
│                                         │
│  Durée : 2–5 secondes (skeleton loader) │
└─────────────────────────────────────────┘
```

### Étape 3 — Formulaire pré-rempli par l'IA
```
┌─────────────────────────────────────────┐
│  ← Retour           Créer l'annonce     │
│                                         │
│  [Photo] [Photo+] [Photo+] [Photo+]     │  ← jusqu'à 4 photos
│                                         │
│  ✨ Pré-rempli par l'IA                 │
│  ┌─────────────────────────────────┐    │
│  │ Titre                            │   │
│  │ Nike Air Max 90 Blanches         │   │  ← éditable
│  └─────────────────────────────────┘    │
│                                         │
│  Catégorie    Sneakers          ▾       │
│  Marque       Nike              ▾       │
│  État         Très bon état     ▾       │
│  Taille       42                ▾       │
│                                         │
│  ── Prix ──────────────────────────     │
│  Prix demandé          [145] TND        │
│  Estimation IA :  120–180 TND   ℹ       │  ← toujours visible
│                                         │
│  Mode de vente                          │
│  ◉ Enchère (Loop Selling)               │
│  ○ Troc (Loop Bartering)                │
│  ○ Prix fixe                            │
│                                         │
│  Durée enchère                          │
│  ◉ 24h  ○ 48h                           │  ← adapté Tunisie (vs 12h original)
│                                         │
│  [     PUBLIER L'ANNONCE     ]          │  ← bouton or champagne
└─────────────────────────────────────────┘
```

### Règle prix visible
- L'estimation IA `(120–180 TND)` est **toujours affichée** sous le champ prix
- Si le vendeur entre un prix > 130% de l'estimation → warning inline immédiat :
  ```
  ⚠ Ton prix est 40% au-dessus du marché.
  Les articles similaires se vendent entre 120 et 180 TND.
  [Ajuster au prix suggéré : 145 TND]  [Continuer quand même]
  ```

---

## 5. Modale Alerte Prix Surestimé

### Déclenchement
Apparaît quand le worker IA détecte un problème (voir spéc agents IA).  
Accessible depuis : push notification → ou badge ⚠ sur l'article dans le Dressing.

### Design de la modale
```
┌─────────────────────────────────────────┐
│                                    ✕    │
│                                         │
│  ⚠️  Ton article ne se vend pas         │
│                                         │
│  "Nike Air Max 90 Blanches"             │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Raison détectée :              │    │
│  │  → Seulement 3 personnes ont    │    │
│  │    liké ton article en 24h      │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Prix actuel        145 TND             │
│  Prix marché IA  120–180 TND            │
│  Prix suggéré    ★ 130 TND              │  ← recommandation IA
│                                         │
│  Ajuste ton prix :                      │
│  ┌──────────────────────────────────┐   │
│  │  90 ●─────────────────────── 200│   │  ← slider
│  │              [130] TND           │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ⏱ Timer enchère : 14h 22min restants  │
│  (le timer ne repart pas si tu ajustes) │
│                                         │
│  Ajustements restants : 2/3             │
│                                         │
│  [   ✓ AJUSTER MON PRIX   ]             │  ← bouton or principal
│  [     Garder 145 TND      ]            │  ← texte secondaire
└─────────────────────────────────────────┘
```

### Règles UX de la modale
- Slider **pré-positionné** sur le prix suggéré par l'IA
- Afficher le timer restant pour créer une légère urgence (sans être agressif)
- Compteur d'ajustements `2/3` visible — transparence totale
- Si `adjustment_n >= 3` : slider désactivé + message "Limite atteinte pour ce cycle"
- Le vendeur peut **fermer sans agir** (croix en haut à droite) → aucun penalty

---

## 6. Écran Dressing (Mes Articles)

```
┌─────────────────────────────────────────┐
│  Mon Dressing                    + Vendre│
│                                         │
│  [En vente (5)] [Vendus (12)] [Archivés]│  ← tabs
│                                         │
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │[Photo] │ │[Photo] │ │[Photo] │       │
│  │        │ │        │ │ ⚠️ ×1  │       │  ← badge alerte prix
│  │Air Max │ │Robe    │ │Hoodie  │       │
│  │145 TND │ │89 TND  │ │ 65 TND │       │
│  │⏱ 14h  │ │⏱  2h  │ │⏱  6h  │       │
│  │🔵 Enc. │ │🔴 Urg. │ │⚠ Alert│       │
│  └────────┘ └────────┘ └────────┘       │
│                                         │
│  ┌────────┐ ┌────────┐                  │
│  │[Photo] │ │[Photo] │                  │
│  │Jeans   │ │Sac     │                  │
│  │120 TND │ │220 TND │                  │
│  │🔁 C2/3 │ │⭐ Sélec│                  │  ← Lokko Select badge
│  └────────┘ └────────┘                  │
└─────────────────────────────────────────┘
```

### Badges sur les cartes du Dressing
| Badge | Couleur | Signification |
|-------|---------|---------------|
| ⏱ Xh restantes | Blanc | Temps avant fin enchère |
| 🔴 Urgent | Rouge | < 2h restantes |
| ⚠ Alerte | Orange | Prix surestimé détecté |
| 🔁 C2/3 | Bleu | Article en cycle 2 ou 3 |
| ⭐ Lokko Select | Or | Catégorie luxe |
| ✓ Vendu | Vert | Transaction complète |

---

## 7. Écran Article Détail

```
┌─────────────────────────────────────────┐
│ ←                              ⋯  ♡    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  │        GALERIE PHOTOS           │    │  ← swipe horizontal photos
│  │        (1/4 indicator)          │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Nike Air Max 90 Blanches               │
│  Pointure 42 · Très bon état            │
│                                         │
│  ★ Vendeur Vérifié · @mohamedT · ⭐4.8 │
│  Tunis, Bab El Khadra                   │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ⏱ Enchère se termine dans 14h 22min   │
│  [████████░░░░░░░░░░░] 45% écoulé       │
│                                         │
│  Prix actuel         145 TND            │
│  Meilleure offre     120 TND   (3 off.) │
│                                         │
│  Prix marché IA : 120–180 TND    ℹ      │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  Description                            │
│  Sneakers Nike Air Max 90, coloris      │
│  blanc/rouge. Portées 3 fois. Semelle   │
│  propre, aucun défaut visible.          │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  Taille 42 · Livraison : Tunis + GCC    │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  [  FAIRE UNE OFFRE  ]  [  ACHETER  ]   │
│        ↑ input TND          ↑ 145 TND   │
└─────────────────────────────────────────┘
```

---

## 8. Écran Loop Selling — Vue Acheteur

### Modale "Faire une offre"
```
┌─────────────────────────────────────────┐
│  Faire une offre             ✕          │
│                                         │
│  Nike Air Max 90 · Prix demandé 145 TND │
│                                         │
│  Ton offre                              │
│  ┌─────────────────────────────────┐    │
│  │          [120]  TND             │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Prix du marché : 120–180 TND           │
│  Meilleure offre actuelle : 120 TND     │
│                                         │
│  ℹ Le vendeur a 2h pour accepter.       │
│    Si pas de réponse → offre expirée.   │
│                                         │
│  [   ENVOYER MON OFFRE   ]              │
└─────────────────────────────────────────┘
```

### Cascade de prix (Loop Selling)
```
Cycle 1 (J1–J2) : 145 TND  → Si pas vendu ↓
Cycle 2 (J3–J4) : 116 TND  (-20%) → Si pas vendu ↓
Cycle 3 (J5–J6) : 92 TND   (-20%) → Si pas vendu → Archivé

L'acheteur voit le badge "🔁 Cycle 2 – Prix baissé de 20%" 
ce qui crée une urgence naturelle d'acheter maintenant.
```

---

## 9. Loop Bartering — Troc

### Flow troc
```
1. Acheteur swipe up sur un article → voit l'option "Proposer un troc"
2. Acheteur choisit un de ses articles à échanger
   (IA filtre automatiquement les articles de valeur similaire ±20%)
3. Vendeur reçoit la proposition : Photo A ↔ Photo B + diff. en TND si besoin
4. Vendeur accepte / refuse / contre-propose
5. Si accepté → échange confirmé, les deux articles marqués "Échangé"
```

### Écran sélection article à troquer
```
┌─────────────────────────────────────────┐
│  ← Proposer un troc                     │
│                                         │
│  Tu proposes :                          │
│  ┌────────────────────────────────┐     │
│  │ [Photo Air Max]                │     │
│  │ Nike Air Max · 145 TND         │     │
│  └────────────────────────────────┘     │
│                                         │
│  Articles compatibles dans ton dressing │
│  (valeur similaire ±20%)                │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐            │
│  │[Robe]│ │[Sac] │ │[Jean]│            │
│  │89TND │ │130TND│ │75TND │            │
│  └──────┘ └──────┘ └──────┘            │
│                                         │
│  [Sac sélectionné]                      │
│                                         │
│  Différence : + 15 TND en ta faveur     │
│  → L'autre personne paie 15 TND extra   │
│                                         │
│  [  ENVOYER LA PROPOSITION  ]           │
└─────────────────────────────────────────┘
```

---

## 10. Écran Profil Vendeur

```
┌─────────────────────────────────────────┐
│                        [Suivre] [⋯]     │
│                                         │
│         [Avatar photo]                  │
│         @mohamedT                       │
│         Tunis · Membre depuis Jan 2025  │
│                                         │
│  ★★★★½  4.8  · 47 avis                  │
│                                         │
│  ┌────────────┬────────────┬──────────┐  │
│  │  Vérifié   │  98 ventes │ 0 litiges│  │
│  │  ★ Trust   │            │          │  │
│  └────────────┴────────────┴──────────┘  │
│                                         │
│  Spécialités : Sneakers · Streetwear    │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  Articles en vente (8)                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │[img] │ │[img] │ │[img] │ │[img] │  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
└─────────────────────────────────────────┘
```

### Badges trust (affichés sur le profil et les cartes)
```
★ Vérifié    → Score ≥ 75  → Fond vert doux + étoile or
⚠ Attention  → Score 40-74 → Fond orange + triangle
🚫 Bloqué    → Score < 40  → Fond rouge + croix
             → Articles masqués du feed (acheteur ne voit pas)
```

---

## 11. Onboarding (Première Ouverture)

### Étape 1 — Splash + Tagline
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│            L  O  K  K  O                │
│                                         │
│     "La mode tunisienne, à ta portée"  │
│                                         │
│                                         │
│         [Commencer]                     │
│         [J'ai déjà un compte]           │
│                                         │
└─────────────────────────────────────────┘
```

### Étape 2 — Préférences style (cold start IA)
```
┌─────────────────────────────────────────┐
│  Qu'est-ce qui te correspond ?          │
│  (choix multiple)                       │
│                                         │
│  ┌──────────┐ ┌──────────┐             │
│  │Streetwear│ │  Hijab   │             │
│  │  Fashion │ │  Fashion │             │
│  └──────────┘ └──────────┘             │
│  ┌──────────┐ ┌──────────┐             │
│  │ Sneakers │ │  Robes & │             │
│  │& Baskets │ │  Tenues  │             │
│  └──────────┘ └──────────┘             │
│  ┌──────────┐ ┌──────────┐             │
│  │  Luxe &  │ │  Casual  │             │
│  │  Sélect  │ │ Everyday │             │
│  └──────────┘ └──────────┘             │
│                                         │
│  [Continuer →]  (ou Passer)            │
└─────────────────────────────────────────┘
```

### Étape 3 — Tuto swipe interactif (30 secondes)
```
Carte interactive avec article factice :
  "Glisse à droite si tu aimes ➡"  → l'utilisateur essaie
  "Glisse en haut pour acheter ⬆"  → animation démo
  "Le prix se dévoile dans 3s..."   → démonstration Silence Visuel
```

---

## 12. Notifications Push

### Types et messages
| Type | Titre | Body |
|------|-------|------|
| Alerte prix | "Ton article ne se vend pas 😕" | "Ajuste le prix de [Titre] → prix suggéré : X TND" |
| Nouvelle offre | "Nouvelle offre reçue 💰" | "[Acheteur] a fait une offre de X TND sur [Titre]" |
| Enchère gagnée | "Tu as gagné l'enchère 🎉" | "[Titre] t'appartient ! Procède au paiement." |
| Troc proposé | "Proposition d'échange 🔁" | "[Vendeur] veut échanger [son article] contre [ton article]" |
| Fin d'enchère proche | "⏱ Plus que 2h !" | "[Titre] se termine bientôt. Meilleure offre : X TND" |
| Article vendu | "Vendu ! 🎊" | "[Titre] a été vendu pour X TND. Merci !" |
| Cycle suivant | "Prix baissé 📉" | "[Titre] passe en Cycle 2. Nouveau prix : X TND (-20%)" |

### Règles fréquence
```
Max 3 notifications marketing / jour / utilisateur
Alertes transactionnelles = pas de limite (achat, paiement)
Alerte prix = 1 seule notification par déclencheur (pas de spam)
Silence nocturne : 23h → 8h (heure de Tunis UTC+1)
```

---

## 13. Paiement

### Écrans paiement (Tunisie)
```
┌─────────────────────────────────────────┐
│  Confirmer l'achat               ✕      │
│                                         │
│  Nike Air Max 90 Blanches               │
│  145 TND                                │
│                                         │
│  Méthode de paiement                    │
│  ◉ [🟢 Flouci]   Paiement mobile TN    │
│  ○ [D17]         Carte prépayée         │
│  ○ [💳 Carte]    Visa / Mastercard      │
│                                         │
│  Livraison                              │
│  ◉ Retrait en main propre (gratuit)     │
│  ○ Livraison Tunis (+5 TND)             │
│  ○ Livraison nationale (+12 TND)        │
│                                         │
│  ─────────────────────────────────────  │
│  Sous-total          145 TND            │
│  Livraison             0 TND            │
│  Commission Lokko    -15 TND  (10%)     │  ← affiché pour transparence
│  ─────────────────────────────────────  │
│  Total vendeur       130 TND            │
│                                         │
│  [   CONFIRMER ET PAYER   ]             │
└─────────────────────────────────────────┘
```

---

## 14. Lokko Select (Catégorie Luxe)

### Différenciation visuelle
```
Badge ⭐ LOKKO SELECT :
  - Fond doré #C9A84C avec texte noir
  - Présent sur la carte feed + page article
  - Filigrane subtil sur la photo

Critères inclusion automatique (IA) :
  - Prix > 500 TND
  - Marque détectée dans liste luxe (Gucci, Louis Vuitton, Dior...)
  - Score trust vendeur ≥ 80
  - Photos haute qualité (résolution + lumière détectée OK)

Avantages Lokko Select :
  - Placement prioritaire dans le feed
  - Vignette gold dans le dressing
  - Badge "Authentifié" si check manuel complété
```

---

## 15. Accessibilité & Performance

### Accessibilité
```
- Contraste minimum WCAG AA (4.5:1) pour tous les textes
- Tailles tactiles minimum 44×44px (recommandation Apple/Google)
- Labels accessibilité sur tous les boutons (VoiceOver / TalkBack)
- Mode sombre natif (déjà dans la palette — fond #0D0D0D)
- Réduction de mouvement respectée (prefers-reduced-motion)
```

### Performance cible
```
- Feed swipe : 60fps constant
- Chargement image : lazy loading + blur placeholder
- Skeleton loaders sur tous les états de chargement
- Analyse photo IA : skeleton 2–5s (pas de spinner bloquant)
- Feed personnalisé : < 200ms (Redis cache)
- Taille APK/IPA cible : < 50MB
```

### États vides
```
- Feed vide (nouveau user) → "Dis-nous ce que tu aimes" → onboarding préférences
- Dressing vide → "Vends ton premier article en 2 min" → bouton + avec tuto
- Pas de résultats recherche → suggestions alternatives + trending
```

---

*Lokko UI/UX Spec v1.0 — 26 Oct 2026*
