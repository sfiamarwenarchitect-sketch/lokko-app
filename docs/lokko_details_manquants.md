# Lokko — Détails Complémentaires (Non Documentés)

> Ce fichier couvre tout ce qui n'apparaît pas dans :
> - `lokko_context_deepseek.md`
> - `lokko_agents_ia_details.md`
> - `lokko_uiux_details.md`

---

## 1. Modèle Économique Complet

### Commission vendeur (progressive par prix)
```
< 100 TND    →  8% commission Lokko
100–500 TND  → 10% commission Lokko
> 500 TND    → 12% commission Lokko (Lokko Select)
```

### Autres sources de revenus (V2+)
```
Boost d'annonce :
  - Payer pour apparaître en priorité dans le feed
  - Tarif suggéré : 2–5 TND / 24h
  - Limité à 10% du feed total (ne pas saturer)

Lokko Premium (abonnement vendeur) :
  - 19 TND/mois
  - Avantages : 0 commission sur 5 ventes/mois, analytics avancés,
    badge "Pro Seller", support prioritaire

Publicité marques locales (V3) :
  - Marques tunisiennes peuvent payer pour placer des articles
    en native ad dans le feed
  - Format : carte identique aux vraies annonces + tag "Sponsorisé"

Assurance transaction (V3) :
  - Option payante à la checkout (~1% du prix)
  - Couvre : article non conforme, vendeur fantôme, litige
```

### Projections volume (marché tunisien)
```
Bêta (M1–M3)   :   500 utilisateurs actifs   →   ~50 transactions/mois
V1 (M4–M6)     :  2 000 utilisateurs actifs  →  ~300 transactions/mois
V1+ (M7–M12)   : 10 000 utilisateurs actifs  → 1 500 transactions/mois
Breakeven estimé : ~3 000 transactions/mois à commission moyenne 10%
```

---

## 2. Système d'Enchères — Règles Détaillées

### Loop Selling — Cascade complète
```
Cycle 1 : Prix initial vendeur      → durée 24–48h (choix vendeur)
Cycle 2 : Prix × 0.80 (-20%)       → durée identique au cycle 1
Cycle 3 : Prix cycle 2 × 0.80      → durée identique
Après cycle 3 : Article archivé automatiquement
  → Vendeur notifié : "Ton article n'a pas trouvé preneur. Tu peux le republier."
  → L'article peut être republié manuellement (nouveau cycle 1, nouveau prix)
```

### Prix minimum plancher
```
Lokko impose un prix minimum par catégorie pour éviter la dévaluation :
  Sneakers        → min 30 TND
  Vêtements       → min 10 TND
  Sacs & Accessoires → min 15 TND
  Bijoux          → min 8 TND
  Lokko Select    → min 300 TND

Si le prix cycle 3 tomberait sous le plancher → article archivé au cycle 2
```

### Option "Buy Now" (achat immédiat)
```
Disponible si prix < 100 TND
  → Acheteur peut court-circuiter l'enchère et acheter directement
  → Vendeur peut activer/désactiver l'option par article
  → Si activé : bouton "Acheter maintenant" sur la fiche article
  → Achat immédiat clôture l'enchère définitivement
```

### Enchère gagnée — processus
```
1. Timer atteint 0h 00min
2. Meilleure offre acceptée automatiquement (si > 60% du prix)
3. Si aucune offre > 60% → cycle suivant déclenché automatiquement
4. Vendeur et acheteur notifiés simultanément
5. Fenêtre de paiement acheteur : 24h
6. Si pas de paiement dans 24h → offre annulée → article cycle suivant
7. Vendeur peut relancer l'offre au 2ème meilleur acheteur (dans 1h)
```

---

## 3. Système de Réputation & Avis

### Notation après transaction
```
Acheteur note vendeur (1–5 étoiles) sur :
  - Conformité article (photo = réalité ?)
  - Réactivité vendeur
  - Qualité emballage / remise en main propre

Vendeur note acheteur (1–5 étoiles) sur :
  - Sérieux (a payé dans les délais ?)
  - Communication
  - Respect du rendez-vous (si retrait en main propre)
```

### Affichage avis
```
Note globale = moyenne pondérée :
  Conformité article   × 0.5
  Réactivité           × 0.3
  Qualité remise       × 0.2

Affichage : ★★★★½ 4.8 · (47 avis)
Seuil affichage note : minimum 3 avis (avant → "Nouveau vendeur")
```

### Système de litiges
```
Délai pour ouvrir un litige : 48h après réception
Motifs possibles :
  - Article non conforme
  - Article non reçu
  - Contrefaçon suspectée

Process litige :
  1. Acheteur ouvre litige + photos
  2. Vendeur a 24h pour répondre
  3. Si pas de réponse → remboursement automatique acheteur
  4. Si désaccord → équipe Lokko tranche sous 72h
  5. Résolution : remboursement partiel / total ou confirmation vente
```

---

## 4. Livraison & Logistique

### Options disponibles (Tunisie)
```
1. Retrait en main propre (gratuit)
   - Vendeur publie sa ville (ex: Tunis, Sfax, Sousse)
   - Acheteur et vendeur se coordonnent via le chat in-app
   - Lieu de rendez-vous suggéré par Lokko : lieux publics sécurisés
     (centres commerciaux, cafés connus)

2. Livraison Tunis capitale (+5 TND)
   - Partenaires livreurs : Topnet, Jumia Express (à négocier)
   - Délai : 24–48h

3. Livraison nationale (+12 TND)
   - Tunisie entière via Poste Tunisienne ou livreur partenaire
   - Délai : 2–4 jours ouvrables

4. Livraison internationale GCC (V2)
   - DHL / Aramex pour les commandes > 200 TND
   - Frais calculés à la checkout selon destination
```

### Séquestre paiement (Escrow)
```
Le paiement acheteur est mis en séquestre par Lokko dès la transaction.
Libération vers vendeur uniquement si :
  - Acheteur confirme réception OK  (48h après livraison)
  - OU délai de 5 jours écoulé sans litige ouvert

Si litige ouvert → fonds gelés jusqu'à résolution
```

---

## 5. Chat In-App

### Fonctionnalités
```
- Messagerie directe acheteur ↔ vendeur sur chaque annonce
- Messages texte + photos (pour questions sur l'article)
- Délai de réponse moyen affiché sur profil vendeur
  ("Répond en général en < 2h")
- Blocage/signalement utilisateur
- Messages automatiques Lokko :
  "L'enchère se termine dans 2h — conclue rapidement !"
  "Paiement confirmé — arrange la livraison ici."
```

### Règles chat
```
- Chat activé uniquement après une offre ou un like mutuel
  (éviter le spam à froid)
- Pas de coordonnées personnelles dans les messages
  (numéro de téléphone, email → détection + avertissement)
- Conservation des messages 90 jours après transaction
```

---

## 6. Recherche & Découverte

### Filtres disponibles
```
Catégorie    → Femme / Homme / Enfant / Accessoires
Sous-catégorie → Sneakers / Robes / Jeans / Hijab / Sacs...
Taille        → XS / S / M / L / XL / XXL + pointures
Marque        → Liste des marques populaires Tunisia
État          → Neuf / Très bon état / Bon état / Acceptable
Prix          → Slider min–max (TND)
Localisation  → Tunis / Sfax / Sousse / Bizerte / Autre
Mode vente    → Enchère / Troc / Prix fixe
Cycle         → Cycle 1 (prix original) / Cycle 2–3 (soldé)
```

### Algorithme de recherche
```
Stack : Elasticsearch
Pondération :
  1. Pertinence texte (titre + description)        × 0.4
  2. Score IA feed (Gorse, si user connecté)       × 0.3
  3. Fraîcheur (date publication)                  × 0.2
  4. Score trust vendeur                           × 0.1

Boosting spécial :
  - Articles Lokko Select : +20% score
  - Vendeurs vérifiés : +10% score
  - Articles en cycle 2–3 (soldés) : affichés dans section "Bonnes affaires"
```

### Suggestions & Trending
```
Page Recherche :
  - Trending aujourd'hui (top 10 articles likés en 24h)
  - Catégories populaires cette semaine
  - "Ils sont repartis vite" (articles vendus en < 2h → crée FOMO)
  - Recherches récentes (localStorage)
  - Suggestions basées sur le style de l'utilisateur (Gorse)
```

---

## 7. Gestion des Comptes

### Inscription
```
Méthodes :
  - Numéro de téléphone (OTP SMS) — méthode principale Tunisie
  - Email + mot de passe
  - Apple Sign In (iOS)
  - Google Sign In (Android)

Données collectées à l'inscription :
  - Prénom + Nom
  - Numéro de téléphone (obligatoire)
  - Ville (optionnel mais recommandé pour la livraison)
  - Préférences style (onboarding)
```

### Vérification d'identité (KYC)
```
Obligatoire pour :
  - Vendre au-delà de 1 000 TND de transactions cumulées
  - Débloquer la livraison nationale
  - Accéder à Lokko Select (vendeur)

Documents acceptés :
  - CIN tunisienne (recto + verso)
  - Passeport
  - Permis de conduire

Délai vérification : 24–48h (vérification manuelle V1)
Badge "✓ Identité vérifiée" sur le profil
```

### Paramètres compte
```
- Langue : Arabe / Français / Anglais
- Devise d'affichage : TND / EUR / AED
- Notifications : toggle par type
- Confidentialité : profil public / privé
- Blocage utilisateurs
- Suppression compte (RGPD)
- Export données personnelles (RGPD)
```

---

## 8. Sécurité & Fraude

### Détection fraude automatique
```
Signaux surveillés :
  - Même IP / appareil = plusieurs comptes (multi-compte)
  - Volume anormal de listings en peu de temps
  - Prix systématiquement très bas (vol probable)
  - Nombreuses annulations acheteur (mauvaise foi)
  - Score contrefaçon Nyckel > 0.7 sur plusieurs articles

Actions automatiques :
  Score < 30       → Shadow ban (article caché du feed, vendeur non notifié)
  3 litiges/mois  → Suspension temporaire 7 jours
  Contrefaçon avérée → Bannissement permanent + signalement autorités
```

### Protection données (conformité)
```
Hébergement données : AWS région Europe (Frankfurt)
  → Données tunisiennes hébergées hors Tunisie (légal si déclaré INPDP)

INPDP (Instance Nationale Protection Données Personnelles) :
  → Déclaration obligatoire avant lancement
  → Lokko doit soumettre le formulaire de déclaration traitement données

Données chiffrées :
  - Mots de passe : bcrypt
  - Paiements : jamais stockés en clair (tokenisation Flouci/D17)
  - Photos : stockées AWS S3, accès par URL signée temporaire
```

---

## 9. Support Client

### Canaux
```
V1 :
  - FAQ in-app (section Aide)
  - Formulaire de contact → email réponse sous 24–48h
  - Signalement in-app (bouton sur chaque article/profil)

V2 :
  - Chat support in-app (heures ouvrables)
  - WhatsApp Business (populaire en Tunisie)
```

### Cas de support prioritaires
```
P1 (réponse < 2h) :
  - Paiement débité mais transaction non confirmée
  - Compte bloqué injustement
  - Article très différent de la description (litige)

P2 (réponse < 24h) :
  - Problème livraison
  - Annonce supprimée sans raison apparente
  - Problème vérification identité

P3 (réponse < 48h) :
  - Questions générales
  - Suggestions fonctionnalités
  - Signalement contenu inapproprié
```

---

## 10. Expansion GCC (Phase 2)

### Marchés cibles
```
1. Tunisiens expatriés en France, Italie, Allemagne (diaspora)
2. GCC : Émirats Arabes Unis (Dubai, Abu Dhabi) — forte diaspora tunisienne
3. Maroc, Algérie (même langue, culture fashion similaire)
```

### Adaptations nécessaires pour GCC
```
Devise       : AED (Dirham) + conversion en temps réel TND/AED
Paiement     : Apple Pay + Google Pay (dominant GCC)
Livraison    : Aramex + DHL (réseau GCC)
Langue       : Arabe standard + Anglais (pas dialectal)
Catégories   : Abaya, Kaftan, Parfums orientaux → nouvelles catégories
TVA          : 5% UAE VAT → calcul automatique à la checkout
Lokko Select : Plus de volume (pouvoir d'achat GCC élevé)
```

### Modèle de lancement GCC
```
Stratégie : partir de la diaspora tunisienne (achat en TND, livraison vers GCC)
  → Phase 1 : Tunisie vend → GCC achète (export)
  → Phase 2 : GCC vend → GCC achète (marché local)
  → Phase 3 : Marketplace régionale MENA
```

---

## 11. Métriques Clés (KPIs)

### KPIs produit
```
Acquisition :
  CAC (Coût Acquisition Client)  < 5 TND cible
  Source trafic : Instagram/TikTok Tunisia (organique)

Engagement :
  DAU/MAU ratio                  > 30%
  Sessions par jour / utilisateur > 2
  Swipes par session              > 15
  Durée session moyenne           > 4 minutes

Conversion :
  Taux conversion feed → achat    > 3%
  Taux de completion enchère      > 60% (au moins une offre)
  Délai moyen vente               < 48h

Rétention :
  D7 rétention                    > 40%
  D30 rétention                   > 20%
  Sellers actifs / mois           > 50% des inscrits vendeurs

Économique :
  GMV (Gross Merchandise Value)   KPI principal
  Take rate moyen                 10%
  Litige rate                     < 2% des transactions
```

### KPIs IA
```
Seller Engine :
  Taux adoption (vendeurs qui utilisent l'auto-remplissage) > 80%
  Précision catégorie IA                                    > 85%
  Précision estimation prix (dans ±30% du prix réel)        > 70%

Stylist Engine :
  CTR feed personnalisé vs trending                         +25% min
  Temps avant premier swipe like                            < 5 cartes

Trust Engine :
  Faux positifs contrefaçon                                 < 5%
  Litiges "article non conforme"                            < 2%

Alerte Prix :
  Taux d'ajustement suite alerte                            > 40%
  Ventes suite ajustement                                   > 25%
```

---

## 12. Roadmap Produit

### Phase 0 — Fondations (M1–M2)
```
✓ Setup stack technique (React Native + NestJS + PostgreSQL)
✓ Auth (téléphone OTP + Apple/Google)
✓ Upload photo + création annonce (manuel, sans IA)
✓ Feed basique (sans personnalisation — trending par défaut)
✓ Système enchères Loop Selling (timer + cascade)
✓ Paiement Flouci
✓ Chat in-app basique
```

### Phase 1 — IA V1 (M3–M4) ← MVP réel
```
✓ AI Seller Engine (API4AI)
✓ Alerte prix surestimé (worker + notification)
✓ AI Trust Engine (Nyckel)
✓ Feed personnalisé Gorse (cold start)
✓ Push notifications (toutes les types)
✓ Vérification identité manuelle
✓ Lancement bêta fermée (100 users Tunis)
```

### Phase 2 — Croissance (M5–M8)
```
- AI Matching Engine (Mistral)
- Loop Bartering (troc)
- Lokko Select (luxe)
- Livraison nationale (partenaire logistique)
- Onboarding optimisé (A/B test tuto swipe)
- Boost annonce (monétisation)
- Lancement public Tunisie
```

### Phase 3 — Expansion (M9–M12)
```
- Lokko Premium (abonnement vendeur)
- Publicité marques locales
- GCC : premier marché (Émirats)
- App bien notée App Store TN / Google Play TN
- Analytics vendeur avancés (tableau de bord perfs)
- API publique (partenariats boutiques tunisiennes)
```

---

## 13. Stack Marketing (Lancement Tunisia)

### Canaux d'acquisition
```
Instagram Tunisia :
  - Compte @lokko.tn
  - Reels : "Ça se vend en 24h sur Lokko" (preuve sociale)
  - Stories : Silence Visuel en demo (accrocheur visuellement)
  - Influenceurs fashion Tunis : micro (10K–100K) > macro

TikTok Tunisia :
  - Format : "POV tu trouves des Nike pour 80 TND"
  - Tendance #SecondMainTunisie
  - Challenges : #LokkoSwipe (swipe challenge)

Bouche-à-oreille :
  - Programme parrainage : vendeur invite ami → 0% commission sur 3 ventes
  - "Vends ton premier article, on prend 0%" (offre lancement)

Communautés Facebook Tunisia :
  - Groupes "Vente / Achat vêtements Tunis" → partenariat ou présence
  - Annonces Facebook/Instagram géociblées Tunisie
```

### Positionnement message
```
Tagline principale :
  "La mode tunisienne, à ta portée."

Messages clés :
  Pour acheteur  : "Trouve des articles de marque à prix accessible"
  Pour vendeur   : "Vends en 24h, l'IA fait tout pour toi"
  Pour les deux  : "La mode circulaire, c'est maintenant en Tunisie"

Argument différenciant vs Facebook Marketplace :
  "Sur Facebook tu galères. Sur Lokko, l'IA gère le prix,
   la description, et te dit si ton article va se vendre."
```

---

## 14. Aspects Légaux (Tunisie)

### Statut juridique recommandé
```
Forme : SARL (Société À Responsabilité Limitée)
Capital minimum : 1 000 TND
Registre Commerce : RNE (Registre National des Entreprises)
Code APE/NAF tunisien : Commerce électronique de détail
```

### Obligations légales
```
INPDP :
  → Déclaration traitement données personnelles (avant lancement)
  → Droit d'accès et suppression pour les utilisateurs

CGU / CGV :
  → Droit applicable : droit tunisien
  → Tribunal compétent : Tunis
  → Mentions obligatoires : identité éditeur, hébergeur, modération

Fiscalité :
  → TVA sur les commissions Lokko : 19% (TVA Tunisie)
  → Facturation aux vendeurs professionnels
  → Déclaration mensuelle auprès des douanes si volume import/export

Contenu :
  → Lokko = marketplace (pas vendeur) → responsabilité limitée
  → Obligation de modération "bonne foi" sur les contenus signalés
```

---

*Lokko — Détails Complémentaires v1.0 — 26 Oct 2026*
