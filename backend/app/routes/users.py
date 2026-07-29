from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.models import User
from app.auth import create_access_token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (founder invitation in V1)."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        trust_score=85.0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: int, db: Session = Depends(get_db)):
    """Get current user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user dashboard stats."""
    from app.models import Product, Bid
    
    total_listings = db.query(Product).filter(Product.owner_id == user_id).count()
    active_listings = db.query(Product).filter(
        Product.owner_id == user_id, Product.status == "active"
    ).count()
    total_sold = db.query(Product).filter(
        Product.owner_id == user_id, Product.status == "sold"
    ).count()
    
    return {
        "user_id": user_id,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_sold": total_sold,
        "trust_score": db.query(User).filter(User.id == user_id).first().trust_score
    }
