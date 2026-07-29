from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, get_db
from app.routes import users, products, bids
from app.models import User
from datetime import datetime

app = FastAPI(
    title="Lokko API",
    description="MVP Prototype - Marketplace de mode de luxe avec IA",
    version="1.0.0"
)

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Root
@app.get("/")
def root():
    return {
        "name": "Lokko",
        "version": "v1.0 MVP",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check
@app.get("/health")
def health(db=Depends(get_db)):
    return {"status": "ok", "database": "sqlite"}

# --- Register Routes ---
# Note: user_id will be injected via query param for MVP
app.include_router(users.router)
app.include_router(products.router)
app.include_router(bids.router)

# --- Demo endpoints ---
@app.post("/demo/init")
def init_demo(db=Depends(get_db)):
    """Initialize with sample data for the MVP demo."""
    from app.models import Product
    
    # Check if already seeded
    if db.query(User).count() > 0:
        return {"message": "Demo data already seeded"}
    
    # Create demo users
    users_data = [
        {"email": "amina@lokko.tn", "username": "amina_style", "full_name": "Amina Ben Ali"},
        {"email": "yassine@lokko.tn", "username": "yassine_lux", "full_name": "Yassine Khelifi"},
        {"email": "sara@lokko.tn", "username": "sara_chic", "full_name": "Sara Mansour"},
        {"email": "karim@lokko.tn", "username": "karim_vintage", "full_name": "Karim Trabelsi"},
    ]
    
    created_users = []
    for u in users_data:
        user = User(**u, trust_score=88.0)
        db.add(user)
        created_users.append(user)
    db.commit()
    
    # Create demo products
    products_data = [
        {"title": "Chanel Classic Flap Bag", "brand": "Chanel", "description": "Authentique, taille petite", "price": 3200, "estimated_value": 3500, "size": "S", "condition": "Like New", "images": ["https://picsum.photos/400/500?random=1"], "owner_id": created_users[0].id},
        {"title": "Nike Air Max 90", "brand": "Nike", "description": "Nouvelles, taille 42", "price": 145, "estimated_value": 180, "size": "M", "condition": "New", "images": ["https://picsum.photos/400/500?random=2"], "owner_id": created_users[1].id},
        {"title": "Lemarié Paris - Robe Soirée", "brand": "Lemarié", "description": "Pièce unique, parfait état", "price": 850, "estimated_value": 1000, "size": "M", "condition": "Like New", "images": ["https://picsum.photos/400/500?random=3"], "owner_id": created_users[2].id},
        {"title": "Vintage Levi's 501", "brand": "Levi's", "description": "Années 70, authentique", "price": 120, "estimated_value": 150, "size": "L", "condition": "Good", "images": ["https://picsum.photos/400/500?random=4"], "owner_id": created_users[3].id},
        {"title": "Rolex Submariner", "brand": "Rolex", "description": "Année 2018, boîte et papiers", "price": 6500, "estimated_value": 7200, "size": "S", "condition": "Like New", "images": ["https://picsum.photos/400/500?random=5"], "owner_id": created_users[0].id},
        {"title": "Adidas Yeezy Boost 350", "brand": "Adidas", "description": "Taille 43, portées 3 fois", "price": 220, "estimated_value": 280, "size": "M", "condition": "Good", "images": ["https://picsum.photos/400/500?random=6"], "owner_id": created_users[1].id},
    ]
    
    from datetime import timedelta
    for p in products_data:
        product = Product(
            **{k: v for k, v in p.items() if k not in ['owner_id']},
            status="active",
            listing_type="selling",
            listing_ends=datetime.utcnow() + timedelta(hours=48),
            ai_trust_score=90.0
        )
        db.add(product)
    
    db.commit()
    
    return {"message": "Demo data seeded", "users": len(created_users), "products": len(products_data)}
