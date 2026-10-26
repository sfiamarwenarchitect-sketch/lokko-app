# Lokko — Détails Complets des Agents IA

> Spécification technique exhaustive des 4 moteurs IA de l'application Lokko.  
> À utiliser comme référence d'implémentation pour un développeur / agent IA.

---

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────┐
│                   AI CORE BRAIN                     │
│         (Orchestrateur NestJS — bus d'événements)   │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ SELLER   │ │  TRUST   │ │ STYLIST  │ │MATCHING│ │
│  │ ENGINE   │ │ ENGINE   │ │ ENGINE   │ │ ENGINE │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────────────────┘
```

**Principe** : chaque moteur est un microservice Python FastAPI indépendant. Le Core Brain les appelle via HTTP interne. Aucun moteur ne connaît les autres — le Core Brain gère les dépendances.

---

## Agent 1 — AI Seller Engine

### Rôle
Transformer une photo brute en annonce structurée. Le vendeur prend une photo, l'IA fait le reste.

### Service externe
**API4AI Fashion API**
- URL : `https://fashion.api4ai.cloud/v1/results`
- Auth : header `Api-Key: <YOUR_KEY>`
- Free tier : **500 requêtes/mois**
- Latence : 2–5 secondes (afficher skeleton loader côté mobile)

### Inputs
```json
{
  "image": "<fichier multipart ou URL>",
  "seller_id": "uuid",
  "listing_id": "uuid"
}
```

### Outputs produits
```json
{
  "category": "sneakers",
  "subcategory": "running",
  "brand": "Nike",
  "brand_confidence": 0.91,
  "colors": ["blanc", "rouge"],
  "condition": "like_new",
  "gender": "homme",
  "season": "toutes saisons",
  "ai_price_min": 85,
  "ai_price_max": 130,
  "ai_price_suggested": 105,
  "title_suggestion": "Nike Air Max blanches – Très bon état",
  "description_suggestion": "Sneakers Nike Air Max, coloris blanc/rouge. Portées 3 fois. Semelle propre, aucun défaut visible.",
  "phash": "a3f4b2c1d8e9...",
  "confidence": 0.88
}
```

### Logique interne
```python
# FastAPI endpoint
@app.post("/ai/analyze-photo")
async def analyze_photo(image: UploadFile, listing_id: str):
    
    # 1. Appel API4AI
    result = await api4ai_call(image)
    
    # 2. Enrichissement prix (référentiel interne PostgreSQL)
    price_range = await get_market_price(result["category"], result["brand"], result["condition"])
    
    # 3. Génération titre + description (template + Mistral si besoin)
    title = generate_title(result)
    description = generate_description(result)
    
    # 4. Hash perceptuel (anti-doublon)
    phash = compute_phash(image)
    duplicate = await check_duplicate(phash)
    
    # 5. Sauvegarde PostgreSQL
    await save_listing_ai_metadata(listing_id, result, price_range, phash)
    
    return {**result, "price_range": price_range, "title": title, 
            "description": description, "phash": phash, "is_duplicate": duplicate}
```

### Anti-doublon (pHash)
```python
from PIL import Image
import imagehash

def compute_phash(image_bytes):
    img = Image.open(BytesIO(image_bytes))
    return str(imagehash.phash(img))

async def check_duplicate(phash: str, threshold: int = 8):
    # Hamming distance ≤ 8 = doublon probable
    existing = await db.query(
        "SELECT listing_id FROM listing_ai_metadata WHERE phash IS NOT NULL"
    )
    for row in existing:
        dist = imagehash.hex_to_hash(phash) - imagehash.hex_to_hash(row.phash)
        if dist <= threshold:
            return True
    return False
```

### Référentiel prix tunisien (table PostgreSQL)
```sql
CREATE TABLE market_price_reference (
  id          SERIAL PRIMARY KEY,
  category    TEXT,
  brand       TEXT,
  condition   TEXT,       -- new / like_new / good / fair
  price_min   DECIMAL,    -- en TND
  price_max   DECIMAL,
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Exemples de données seed
INSERT INTO market_price_reference VALUES
  (DEFAULT, 'sneakers', 'Nike', 'like_new', 80, 180, NOW()),
  (DEFAULT, 'sneakers', 'Adidas', 'good', 50, 120, NOW()),
  (DEFAULT, 'robe', 'Zara', 'new', 40, 90, NOW()),
  (DEFAULT, 'hijab', 'Unknown', 'new', 10, 35, NOW());
```

### Fallback si API4AI down
```python
FALLBACK_CATEGORIES = {
  "vetement": {"price_min": 20, "price_max": 150},
  "chaussures": {"price_min": 40, "price_max": 200},
  "accessoires": {"price_min": 10, "price_max": 80}
}
# Si API4AI timeout → catégorie "vetement" par défaut, confidence = 0
```

---

## Agent 2 — AI Trust Engine

### Rôle
Évaluer la fiabilité d'un vendeur et détecter les contrefaçons. Protège l'acheteur.

### Service externe
**Nyckel** — classifieur ML entraînable
- URL : `https://www.nyckel.com/v0.9/functions/<FUNCTION_ID>/invoke`
- Auth : Bearer token OAuth2
- Free tier : **1 000 classifications/mois**
- Training : interface web ou API (upload images + labels)

### Score vendeur — algorithme composite
```python
def compute_trust_score(seller_id: str) -> dict:
    
    # Données historiques depuis PostgreSQL
    stats = get_seller_stats(seller_id)
    
    # Composantes du score (total = 100)
    score_components = {
        "completion_rate": stats.completed / stats.total_sales * 30,  # max 30 pts
        "avg_rating": (stats.avg_rating / 5) * 25,                    # max 25 pts
        "dispute_penalty": max(0, 15 - stats.disputes * 5),           # max 15 pts
        "account_age": min(15, stats.days_active / 30),               # max 15 pts
        "verified_id": 10 if stats.id_verified else 0,                # max 10 pts
        "response_time": 5 if stats.avg_response_h < 2 else 0,       # max  5 pts
    }
    
    total_score = sum(score_components.values())
    
    # Label
    if total_score >= 75:
        label = "verified"
        badge = "★ Vérifié"
    elif total_score >= 40:
        label = "warning"
        badge = "⚠ Attention"
    else:
        label = "blocked"
        badge = "🚫 Bloqué"
    
    return {"score": round(total_score), "label": label, "badge": badge,
            "components": score_components}
```

### Détection contrefaçon (Nyckel)
```python
@app.post("/ai/trust-score")
async def trust_score(seller_id: str, listing_id: str, image_url: str):
    
    # 1. Score vendeur (règles métier)
    vendor_score = compute_trust_score(seller_id)
    
    # 2. Classifieur contrefaçon Nyckel
    counterfeit_result = await nyckel_classify(image_url)
    # Returns: {"labelName": "authentic"|"counterfeit", "confidence": 0.0-1.0}
    
    # 3. Flags combinés
    flags = {
        "counterfeit_suspected": counterfeit_result["labelName"] == "counterfeit"
                                  and counterfeit_result["confidence"] > 0.7,
        "low_rating": vendor_score["score"] < 40,
        "new_seller": vendor_score["components"]["account_age"] < 5,
        "high_dispute_rate": vendor_score["components"]["dispute_penalty"] < 5
    }
    
    # 4. Si score < 30 → alerte modération
    if vendor_score["score"] < 30:
        await trigger_moderation_alert(seller_id, listing_id, vendor_score, flags)
    
    # 5. Sauvegarde
    await save_trust_score(seller_id, vendor_score, flags)
    
    return {**vendor_score, "flags": flags, "counterfeit": counterfeit_result}
```

### Entraînement du classifieur Nyckel
```
Dataset minimum recommandé :
├── authentic/     (≥200 images par marque prioritaire)
│   ├── nike_authentic_001.jpg
│   ├── adidas_authentic_001.jpg
│   └── ...
└── counterfeit/   (≥200 images contrefaçons connues)
    ├── fake_nike_001.jpg
    └── ...

Marques prioritaires pour la Tunisie V1 :
  Nike, Adidas, Puma, New Balance, Zara, H&M, Gucci (Lokko Select)
```

### Table PostgreSQL
```sql
CREATE TABLE seller_trust_scores (
  seller_id   UUID PRIMARY KEY REFERENCES users(id),
  score       INT CHECK (score BETWEEN 0 AND 100),
  label       TEXT CHECK (label IN ('verified','warning','blocked')),
  flags       JSONB DEFAULT '{}',
  components  JSONB,        -- détail des composantes
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE seller_stats (
  seller_id       UUID PRIMARY KEY,
  total_sales     INT DEFAULT 0,
  completed       INT DEFAULT 0,
  disputes        INT DEFAULT 0,
  avg_rating      FLOAT DEFAULT 0,
  id_verified     BOOLEAN DEFAULT FALSE,
  avg_response_h  FLOAT DEFAULT 24,
  days_active     INT DEFAULT 0
);
```

### Règle de mise à jour
```
Recalculer le score après :
  - Chaque transaction complétée
  - Chaque avis reçu
  - Chaque dispute ouverte / résolue
  - Vérification d'identité validée
```

---

## Agent 3 — AI Stylist Engine

### Rôle
Personnaliser le feed de chaque utilisateur selon ses comportements. Plus l'utilisateur swipe, plus le feed est précis.

### Service externe
**Gorse** — moteur de recommandation open-source
- Licence : Apache 2.0 (gratuit, self-hosted)
- Repo : `https://github.com/gorse-io/gorse`
- Déploiement : Docker Compose
- Latence cible : **< 200ms** via Redis cache

### Installation Docker
```yaml
# docker-compose.gorse.yml
version: "3"
services:
  gorse-worker:
    image: zhenghaoz/gorse-worker
    ports:
      - "8089:8089"
    environment:
      GORSE_CACHE_STORE: redis://redis:6379
      GORSE_DATA_STORE: postgres://lokko:password@postgres:5432/lokko
    command: --master-host gorse-master --master-port 8086 --http-port 8089

  gorse-server:
    image: zhenghaoz/gorse-server
    ports:
      - "8087:8087"
    environment:
      GORSE_CACHE_STORE: redis://redis:6379
      GORSE_DATA_STORE: postgres://lokko:password@postgres:5432/lokko
    command: --master-host gorse-master --master-port 8086 --http-port 8087

  gorse-master:
    image: zhenghaoz/gorse-master
    ports:
      - "8086:8086"
      - "8088:8088"
    volumes:
      - ./gorse.toml:/etc/gorse/config.toml
    environment:
      GORSE_CACHE_STORE: redis://redis:6379
      GORSE_DATA_STORE: postgres://lokko:password@postgres:5432/lokko
```

### Configuration Gorse (gorse.toml)
```toml
[recommend]
  popular_window = 360      # trending sur 360h (15 jours)
  fit_period = 20           # recalcul modèle toutes 20 min
  
[collaborative]
  model_fit_period = 60
  enable_index_rebuild = true
  
[offline]
  check_recommend_period = 1
  refresh_recommend_period = 24
```

### Envoi des événements swipe
```python
import httpx

GORSE_SERVER = "http://gorse-server:8087"

@app.post("/ai/swipe-event")
async def record_swipe(user_id: str, listing_id: str, 
                        event_type: str, context: dict):
    # event_type: "like" | "skip" | "up" | "purchase" | "view"
    
    # Mapping vers types Gorse
    feedback_type_map = {
        "like": "like",
        "up": "purchase",      # swipe haut = intention achat forte
        "purchase": "purchase",
        "skip": "dislike",
        "view": "read"
    }
    
    # Push vers Gorse
    async with httpx.AsyncClient() as client:
        await client.post(f"{GORSE_SERVER}/api/feedback", json=[{
            "FeedbackType": feedback_type_map.get(event_type, "read"),
            "UserId": user_id,
            "ItemId": listing_id,
            "Timestamp": datetime.utcnow().isoformat()
        }])
    
    # Log local pour analytics
    await save_swipe_event(user_id, listing_id, event_type, context)
    
    return {"status": "accepted"}
```

### Récupération du feed personnalisé
```python
@app.get("/ai/feed/{user_id}")
async def get_feed(user_id: str, limit: int = 20, cursor: str = None):
    
    # Cache Redis d'abord (TTL 5 min)
    cache_key = f"feed:{user_id}:{cursor}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Si nouveau user (cold start) → trending Tunisia
    is_new_user = await check_is_new_user(user_id)
    
    if is_new_user:
        recommendations = await get_trending_tunisia(limit)
    else:
        # Gorse recommandations personnalisées
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GORSE_SERVER}/api/recommend/{user_id}",
                params={"n": limit, "cursor": cursor or ""}
            )
            items = resp.json()
        
        recommendations = [{"listing_id": item["Id"], 
                            "score": item["Score"],
                            "reason": "personalized"} for item in items]
    
    # Injecter "Look du Jour" toutes les 10 items
    recommendations = inject_look_du_jour(recommendations, user_id)
    
    # Cache 5 minutes
    await redis.setex(cache_key, 300, json.dumps(recommendations))
    
    return recommendations
```

### Look du Jour
```python
async def generate_look_du_jour(user_id: str) -> list:
    """
    Compose 3 articles complémentaires (outfit complet).
    Généré 1x/24h par user, basé sur ses préférences.
    """
    # 1. Récupérer le style dominant de l'user (top catégories likées)
    user_style = await get_dominant_style(user_id)
    
    # 2. Chercher 1 article par "couche" : haut + bas + chaussures (ou hijab)
    top = await find_matching_item(user_style, category="tops")
    bottom = await find_matching_item(user_style, category="bottoms", 
                                       color_harmony=top["colors"])
    shoes = await find_matching_item(user_style, category="sneakers",
                                      color_harmony=[top["colors"], bottom["colors"]])
    
    return [
        {"listing_id": top["id"], "role": "haut", "look_id": generate_look_id()},
        {"listing_id": bottom["id"], "role": "bas"},
        {"listing_id": shoes["id"], "role": "chaussures"}
    ]

def inject_look_du_jour(feed: list, user_id: str) -> list:
    """Insère le Look du Jour à position 7 du feed."""
    look = asyncio.run(generate_look_du_jour(user_id))
    look_card = {"type": "look_du_jour", "items": look, "score": 999}
    return feed[:7] + [look_card] + feed[7:]
```

### Trending Tunisia (cold start)
```python
async def get_trending_tunisia(limit: int) -> list:
    """
    Items avec le plus de likes/vues dans les 48 dernières heures.
    Filtrés par catégories prioritaires tunisiennes.
    """
    return await db.query("""
        SELECT l.id as listing_id, COUNT(s.id) as score, 'trending' as reason
        FROM listings l
        LEFT JOIN swipe_events s ON s.listing_id = l.id
        WHERE s.created_at > NOW() - INTERVAL '48 hours'
          AND s.event_type = 'like'
          AND l.category IN ('robe','sneakers','hijab','streetwear','pantalon')
          AND l.status = 'active'
        GROUP BY l.id
        ORDER BY score DESC
        LIMIT $1
    """, limit)
```

---

## Agent 4 — AI Matching Engine

### Rôle
Classer les offres d'enchère, matcher les échanges troc, générer les descriptions riches.

### Service externe
**Mistral API** (Mistral 7B Instruct)
- URL : `https://api.mistral.ai/v1/chat/completions`
- Auth : Bearer token
- Coût : ~0.25€ / 1M tokens (V1 bêta ≈ 5–35€/mois selon usage)
- Modèle recommandé : `mistral-small-latest`

### Ranking des offres d'enchère
```python
@app.post("/ai/match-offers")
async def rank_offers(listing_id: str, offers: list[dict]):
    """
    Input:  [{buyer_id, amount, timestamp, buyer_trust_score}]
    Output: [{offer_id, rank, score, reason}]
    """
    listing = await get_listing(listing_id)
    
    ranked = []
    for offer in offers:
        # Score composite (0–100)
        price_score    = (offer["amount"] / listing["price"]) * 50   # max 50 pts
        trust_score    = (offer["buyer_trust_score"] / 100) * 30     # max 30 pts
        recency_score  = compute_recency_score(offer["timestamp"]) * 20  # max 20 pts
        
        total = price_score + trust_score + recency_score
        
        ranked.append({
            "offer_id": offer["id"],
            "score": round(total, 2),
            "reason": f"Prix {offer['amount']} TND · Confiance {offer['buyer_trust_score']}/100"
        })
    
    # Trier par score décroissant
    ranked.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    
    return ranked

def compute_recency_score(timestamp: str) -> float:
    """Offre récente = meilleur score. Demi-vie 6h."""
    age_hours = (datetime.utcnow() - parse_timestamp(timestamp)).seconds / 3600
    return max(0, 1 - (age_hours / 12))
```

### Barter Matching (troc)
```python
@app.post("/ai/barter-match")
async def find_barter_matches(listing_id: str, user_id: str):
    """
    Trouve des articles à échanger dont la valeur estimée est ±20%
    de la valeur de l'article proposé.
    """
    my_listing = await get_listing(listing_id)
    my_value = my_listing["ai_price_suggested"]
    
    # Tolérance ±20%
    min_value = my_value * 0.8
    max_value = my_value * 1.2
    
    # Chercher articles actifs dans la fourchette (autre user)
    candidates = await db.query("""
        SELECT l.id, l.title, m.ai_price_suggested, l.category, l.seller_id
        FROM listings l
        JOIN listing_ai_metadata m ON m.listing_id = l.id
        WHERE m.ai_price_suggested BETWEEN $1 AND $2
          AND l.seller_id != $3
          AND l.status = 'active'
          AND l.barter_ok = TRUE
        ORDER BY ABS(m.ai_price_suggested - $4)
        LIMIT 10
    """, min_value, max_value, user_id, my_value)
    
    return {"matches": candidates, "my_value": my_value, "tolerance": "±20%"}
```

### Génération de descriptions (Mistral)
```python
async def generate_description(metadata: dict) -> str:
    """Utilise Mistral pour générer une description vendeuse."""
    
    prompt = f"""Tu es un expert en vente de mode en ligne sur le marché tunisien.
Génère une description courte (2-3 phrases max) et attrayante pour cet article :
- Catégorie : {metadata['category']}
- Marque : {metadata['brand']}
- Couleurs : {', '.join(metadata['colors'])}
- État : {metadata['condition']}
- Prix suggéré : {metadata['ai_price_suggested']} TND

Réponds uniquement avec la description, sans introduction."""
    
    response = await mistral_client.chat(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()
```

### Résumé négociation (Mistral)
```python
async def summarize_negotiation(messages: list[dict]) -> str:
    """Résume un échange de négociation entre acheteur et vendeur."""
    
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    prompt = f"""Résume en 1 phrase cette négociation de vente de mode.
    
{conversation}

Mentionne le prix final proposé si visible. Sois neutre et factuel."""
    
    response = await mistral_client.chat(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    
    return response.choices[0].message.content.strip()
```

---

## Agent 5 — Alerte Prix Surestimé (Feature transversale)

> Ce n'est pas un moteur IA à proprement parler — c'est un **worker NestJS** qui orchestre les moteurs 1 et 4 pour détecter et notifier les prix anormaux.

### Worker (Bull Queue — NestJS)
```typescript
// price-alert.processor.ts
@Processor('price-alert')
export class PriceAlertProcessor {
  
  @Cron('0 * * * *') // Toutes les heures
  async checkAllActiveListings() {
    const listings = await this.listingRepo.findActive();
    for (const listing of listings) {
      const shouldAlert = await this.evaluateListing(listing);
      if (shouldAlert.triggered) {
        await this.priceAlertQueue.add('notify-seller', {
          listingId: listing.id,
          sellerId: listing.sellerId,
          suggestedPrice: shouldAlert.suggestedPrice,
          reason: shouldAlert.reason
        });
      }
    }
  }
  
  private async evaluateListing(listing: Listing): Promise<AlertEvaluation> {
    const metadata = await this.aiMetadataRepo.findByListingId(listing.id);
    const elapsed = Date.now() - listing.startedAt.getTime();
    const duration = listing.duration * 1000;
    const bestOffer = listing.bestOffer || 0;
    const rightSwipes = listing.rightSwipeCount || 0;
    const ageHours = elapsed / 3600000;
    
    // Règle 1 : Pas d'offre ≥60% après 50% durée
    const r1 = elapsed > duration * 0.5 && bestOffer < listing.price * 0.6;
    
    // Règle 2 : < 5 right-swipes après 24h
    const r2 = ageHours > 24 && rightSwipes < 5;
    
    // Règle 3 : Prix > 30% au-dessus estimation IA
    const r3 = metadata && listing.price > metadata.aiPriceMax * 1.3;
    
    return {
      triggered: r1 || r2 || r3,
      reason: r1 ? 'below_offer' : r2 ? 'low_engagement' : 'over_market',
      suggestedPrice: metadata?.aiPriceSuggested || listing.price * 0.75
    };
  }
}
```

### Notification push (FCM)
```typescript
// notification.service.ts
async sendPriceAlert(sellerId: string, listing: Listing, suggestedPrice: number) {
  const deviceToken = await this.userRepo.getDeviceToken(sellerId);
  
  await firebase.messaging().send({
    token: deviceToken,
    notification: {
      title: "Ton article ne se vend pas 😕",
      body: `Le prix suggéré pour "${listing.title}" est ${suggestedPrice} TND. Ajuste ?`
    },
    data: {
      type: "price_alert",
      listing_id: listing.id,
      suggested_price: String(suggestedPrice),
      action: "open_adjustment_modal"
    },
    apns: { payload: { aps: { badge: 1, sound: "default" } } }
  });
}
```

### Contraintes immuables
```
❌ JAMAIS réinitialiser le timer d'enchère lors d'un ajustement de prix
❌ Maximum 3 ajustements par cycle — bloquer le bouton si adjustment_n >= 3
✓  Le vendeur garde toujours l'option "Garder mon prix"
✓  Alerte envoyée 1 seule fois par déclencheur (éviter le spam)
```

### Table d'audit
```sql
CREATE TABLE price_adjustments (
  id             UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  listing_id     UUID NOT NULL REFERENCES listings(id),
  old_price      DECIMAL(10,2),
  new_price      DECIMAL(10,2),
  trigger_reason TEXT CHECK (trigger_reason IN ('below_offer','low_engagement','over_market')),
  adjustment_n   INT DEFAULT 1,       -- max 3
  notified_at    TIMESTAMPTZ,         -- quand la notif a été envoyée
  adjusted_at    TIMESTAMPTZ,         -- quand le vendeur a ajusté (NULL si refusé)
  seller_choice  TEXT CHECK (seller_choice IN ('adjusted','kept','pending'))
);

-- Index pour le cron (performance)
CREATE INDEX idx_price_adj_listing ON price_adjustments(listing_id, adjustment_n);
```

---

## AI Core Brain — Orchestrateur

### Rôle
Coordonner les 4 agents. Gérer les erreurs et les timeouts. Aucune logique métier propre.

### Flux principal (création d'une annonce)
```
1. Vendeur upload photo
      ↓
2. Core Brain → Seller Engine (analyse photo)
      ↓
3. Core Brain → Trust Engine (score contrefaçon)
      ↓  [parallèle]
4a. Core Brain → Gorse (enregistrement nouvel item)
4b. Core Brain → save listing en DB
      ↓
5. Core Brain → réponse mobile (listing créé avec métadonnées IA)
```

### Circuit-breaker (NestJS)
```typescript
// ai-core.service.ts
import { CircuitBreaker } from 'opossum';

const sellerEngineBreaker = new CircuitBreaker(callSellerEngine, {
  timeout: 8000,        // 8 secondes max
  errorThresholdPercentage: 50,
  resetTimeout: 30000   // retry après 30s
});

sellerEngineBreaker.fallback(() => ({
  category: 'vetement',
  brand: 'Unknown',
  confidence: 0,
  ai_price_min: 20,
  ai_price_max: 150,
  is_fallback: true
}));
```

---

## Performances & Monitoring

### Seuils SLA
| Endpoint | Temps cible | Action si dépassé |
|----------|-------------|-------------------|
| `/ai/analyze-photo` | < 6s | Skeleton loader mobile |
| `/ai/feed/{user_id}` | < 200ms | Cache Redis obligatoire |
| `/ai/trust-score` | < 3s | Async (ne bloque pas création) |
| `/ai/price-check` | < 500ms | Cron silencieux |

### Métriques à logger
```python
# Prometheus metrics
ai_request_duration = Histogram('ai_request_duration_seconds', 
                                 'Durée des appels IA', ['engine', 'endpoint'])
ai_fallback_total   = Counter('ai_fallback_total', 'Fallbacks déclenchés', ['engine'])
ai_alert_triggered  = Counter('ai_price_alert_total', 'Alertes prix déclenchées', ['reason'])
```

---

## Résumé des APIs externes

| Engine | Service | Endpoint | Auth |
|--------|---------|----------|------|
| Seller | API4AI | `https://fashion.api4ai.cloud/v1/results` | Header `Api-Key` |
| Trust | Nyckel | `https://www.nyckel.com/v0.9/functions/{id}/invoke` | Bearer OAuth2 |
| Stylist | Gorse | `http://gorse-server:8087/api/recommend/{user_id}` | Internal |
| Matching | Mistral | `https://api.mistral.ai/v1/chat/completions` | Bearer API key |

---

## Variables d'environnement requises

```bash
# .env
API4AI_KEY=xxx
NYCKEL_CLIENT_ID=xxx
NYCKEL_CLIENT_SECRET=xxx
NYCKEL_FUNCTION_ID=xxx
MISTRAL_API_KEY=xxx
GORSE_SERVER_URL=http://gorse-server:8087
REDIS_URL=redis://redis:6379
DATABASE_URL=postgres://lokko:password@postgres:5432/lokko
FCM_PROJECT_ID=lokko-firebase-xxx
```

---

*Lokko AI Agents Spec v1.0 — 26 Oct 2026*
