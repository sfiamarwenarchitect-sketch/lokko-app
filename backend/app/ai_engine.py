"""
AI Stylist Engine - Lokko
Moteur de recommandation hybride basé sur les données utilisateur.

Fonctionnalités:
- Recommandation de produits basée sur l'historique de swipe
- Score de matching (0-100%) pour chaque produit
- Détection des patterns d'utilisateur (marques, tailles, prix)
- Carte "Look du Jour" insérée tous les 10 swipes
"""

from sqlalchemy.orm import Session
from app.models import User, Product, Bid, SwipeHistory, AILookCard
from datetime import datetime

def calculate_matching_score(user_id: int, product: Product, db: Session) -> float:
    """
    Calculate how well a product matches a user's taste.
    
    Factors:
    1. Brand affinity (based on swiped products)
    2. Price range compatibility
    3. Size match
    4. Condition preference
    5. Trust score alignment
    """
    if product.owner_id == user_id:
        return 0.0  # Don't show own products
    
    score = 50.0  # Base score
    
    # Get user's swipe history
    swiped = db.query(SwipeHistory).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.swipe_direction == "right"
    ).limit(50).all()
    
    if not swiped:
        return score  # New user, base score
    
    # 1. Brand affinity (+20 points max)
    swiped_brands = [
        db.query(Product.brand).filter(Product.id == s.product_id).scalar()
        for s in swiped
    ]
    brand_matches = swiped_brands.count(product.brand) if product.brand else 0
    brand_score = min(20, brand_matches * 5)
    score += brand_score
    
    # 2. Price range (+20 points max)
    avg_price = sum(
        [p.price for p in [
            db.query(Product).filter(Product.id == s.product_id).first()
            for s in swiped if s.product_id
        ]]
    ) / max(len(swiped), 1)
    
    if avg_price > 0:
        price_diff = abs(product.price - avg_price) / avg_price
        price_score = max(0, 20 - (price_diff * 10))
        score += price_score
    
    # 3. Size match (+15 points)
    if product.size:
        swiped_sizes = [
            db.query(Product.size).filter(Product.id == s.product_id).scalar()
            for s in swiped
        ]
        if product.size in swiped_sizes:
            score += 15
        # Similar sizes (S/M, M/L)
        similar = ["S", "M", "L", "XL"]
        if product.size in similar:
            idx = similar.index(product.size)
            nearby = similar[max(0, idx-1):min(len(similar), idx+2)]
            if product.size not in swiped_sizes:
                for s in nearby:
                    if s in swiped_sizes:
                        score += 8
                        break
    
    # 4. Condition preference (+10 points)
    if product.condition:
        swiped_conditions = [
            db.query(Product.condition).filter(Product.id == s.product_id).scalar()
            for s in swiped
        ]
        if product.condition in swiped_conditions:
            score += 10
    
    # 5. Trust score alignment (+5 points)
    user_trust = db.query(User.trust_score).filter(User.id == user_id).scalar()
    if user_trust and product.ai_trust_score:
        trust_diff = abs(user_trust - product.ai_trust_score) / 100
        score += max(0, 5 - (trust_diff * 5))
    
    return min(100, max(0, score))

def get_personalized_feed(user_id: int, db: Session, limit: int = 20) -> list:
    """
    Get a personalized feed of products for the user.
    
    Algorithm:
    1. Get all active products
    2. Score each based on user's taste
    3. Sort by matching score
    4. Insert "Look du Jour" card every 10 products
    """
    # Get active selling products
    products = db.query(Product).filter(
        Product.status == "active",
        Product.listing_type == "selling",
        Product.is_safe_haven == False
    ).limit(limit * 2).all()  # Get more to filter
    
    # Score each product
    scored_products = []
    for p in products:
        score = calculate_matching_score(user_id, p, db)
        if score > 0:
            scored_products.append((p, score))
    
    # Sort by score
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # Limit results
    result = scored_products[:limit]
    
    # Insert AI Look Card every 10 swipes (if enough products)
    insert_look_card = False  # V1: disabled, enable for beta
    
    return [p for p, s in result]

def generate_look_card(user_id: int, db: Session) -> dict:
    """
    Generate an AI-generated "Look du Jour" card.
    
    Composed of products marked for exchange from other members.
    """
    # Find exchange products with high AI trust score
    products = db.query(Product).filter(
        Product.listing_type == "barter",
        Product.status == "active"
    ).limit(5).all()
    
    if not products:
        return None
    
    # Pick highest trust score product
    best = max(products, key=lambda p: p.ai_trust_score)
    
    matching_score = calculate_matching_score(user_id, best, db)
    
    if matching_score > 90:
        return {
            "product": best,
            "matching_score": matching_score,
            "title": "Look du Jour",
            "description": f"Pièce IA recommandée pour vous ({matching_score:.0f}% match)"
        }
    
    return None
