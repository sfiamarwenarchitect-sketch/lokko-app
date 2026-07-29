from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductCreate, ProductResponse, ProductWithBidCount
from app.models import Product, Bid, User
from datetime import datetime, timedelta

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, owner_id: int, db: Session = Depends(get_db)):
    """Create a new product listing with 48h duration."""
    listing_ends = datetime.utcnow() + timedelta(hours=product.duration_hours)
    
    db_product = Product(
        title=product.title,
        brand=product.brand,
        description=product.description,
        price=product.price,
        estimated_value=product.estimated_value,
        size=product.size,
        condition=product.condition,
        listing_type=product.listing_type,
        status="active",
        min_bid_percentage=product.min_bid_percentage,
        duration_hours=product.duration_hours,
        listing_created=datetime.utcnow(),
        listing_ends=listing_ends,
        ai_trust_score=85.0,
        is_safe_haven=False,
        images=product.images,
        owner_id=owner_id
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/feed", response_model=list[ProductWithBidCount])
def get_feed(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get swipeable product feed (one product per screen)."""
    from app.models import SwipeHistory
    
    # Get products the user hasn't swiped yet
    swiped_product_ids = db.query(SwipeHistory.product_id).filter(
        SwipeHistory.user_id == user_id,
        SwipeHistory.swipe_direction == "right"
    ).subquery().scalar_subquery()
    
    products = db.query(Product).filter(
        Product.status == "active",
        Product.owner_id != user_id,
        Product.listing_type == "selling",
        Product.is_safe_haven == False
    ).offset(skip).limit(limit).all()
    
    result = []
    for p in products:
        bid_count = db.query(Bid).filter(
            Bid.product_id == p.id, Bid.status.in_(["pending", "cascading"])
        ).count()
        highest_bid = db.query(Bid.amount).filter(
            Bid.product_id == p.id, Bid.status.in_(["pending", "cascading"])
        ).order_by(Bid.amount.desc()).first()
        
        time_remaining = ""
        if p.listing_ends:
            delta = p.listing_ends - datetime.utcnow()
            if delta.total_seconds() > 0:
                hours = int(delta.total_seconds() // 3600)
                time_remaining = f"{hours}h"
        
        result.append(ProductWithBidCount(
            **p.__dict__,
            active_bid_count=bid_count,
            highest_bid=highest_bid[0] if highest_bid else None,
            time_remaining=time_remaining
        ))
    
    return result

@router.get("/product/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/my-listings", response_model=list[ProductResponse])
def get_my_listings(owner_id: int, db: Session = Depends(get_db)):
    """Get all user's product listings (their dressing)."""
    products = db.query(Product).filter(Product.owner_id == owner_id).all()
    return products

@router.patch("/product/{product_id}/pause", status_code=200)
def pause_product(product_id: int, owner_id: int, db: Session = Depends(get_db)):
    """Pause a product listing (goes to dressing)."""
    product = db.query(Product).filter(Product.id == product_id, Product.owner_id == owner_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = "paused"
    db.commit()
    return {"message": "Product paused", "product_id": product_id}
