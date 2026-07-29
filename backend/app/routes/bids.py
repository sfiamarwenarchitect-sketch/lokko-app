from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import BidCreate, BidResponse, BidWithUser, SwipeCreate, SwipeResponse
from app.models import Product, Bid, User, SwipeHistory, BidStatus
from datetime import datetime, timedelta

router = APIRouter(prefix="/bids", tags=["bids"])

@router.post("/", response_model=BidResponse, status_code=201)
def place_bid(bid: BidCreate, bidder_id: int, db: Session = Depends(get_db)):
    """
    Place a private bid on a product.
    Rule: Bid must be ≥ 70% of seller's estimated value.
    """
    product = db.query(Product).filter(Product.id == bid.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate minimum bid (70% rule)
    min_bid = product.estimated_value * product.min_bid_percentage
    if bid.amount < min_bid:
        raise HTTPException(
            status_code=400,
            detail=f"Bid must be at least {min_bid:.2f}€ (70% of estimated value {product.estimated_value}€)"
        )
    
    # Check if user already bid on this product
    existing_bid = db.query(Bid).filter(
        Bid.product_id == product.id,
        Bid.bidder_id == bidder_id,
        Bid.status.in_(["pending", "cascading"])
    ).first()
    if existing_bid:
        raise HTTPException(status_code=400, detail="User already has an active bid on this product")
    
    # Get current bid ranking
    active_bids = db.query(Bid).filter(
        Bid.product_id == product.id,
        Bid.status.in_(["pending", "cascading"])
    ).all()
    new_rank = len(active_bids) + 1
    
    # Create the bid
    new_bid = Bid(
        product_id=product.id,
        bidder_id=bidder_id,
        amount=bid.amount,
        status="pending",
        bid_rank=new_rank,
        bid_time=datetime.utcnow(),
        deadline=None,  # Set when accepted
        is_cascading_to_next=False
    )
    db.add(new_bid)
    
    # Update rankings
    for b in active_bids:
        if b.amount < bid.amount:
            b.bid_rank += 1
    
    db.commit()
    db.refresh(new_bid)
    return new_bid

@router.get("/product/{product_id}")
def get_product_bids(product_id: int, db: Session = Depends(get_db)):
    """Get all bids for a product (sorted by amount)."""
    bids = db.query(Bid).filter(
        Bid.product_id == product_id,
        Bid.status.in_(["pending", "cascading"])
    ).order_by(Bid.amount.desc()).all()
    
    result = []
    for bid in bids:
        bidder = db.query(User).filter(User.id == bid.bidder_id).first()
        result.append(BidWithUser(
            **bid.__dict__,
            bidder={"id": bidder.id, "username": bidder.username, "trust_score": bidder.trust_score}
        ))
    
    return result

@router.post("/accept/{bid_id}", status_code=200)
def accept_bid(bid_id: int, db: Session = Depends(get_db)):
    """
    Seller accepts a bid.
    Triggers 12h countdown timer.
    If timer expires → cascades to next bidder.
    """
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Set 12h deadline
    bid.status = "cascading"
    bid.deadline = datetime.utcnow() + timedelta(hours=12)
    bid.is_cascading_to_next = True
    
    # Find next bidder
    next_bid = db.query(Bid).filter(
        Bid.product_id == bid.product_id,
        Bid.status == "pending"
    ).order_by(Bid.amount.desc()).first()
    
    if next_bid:
        # Mark next bid as waiting in cascade
        next_bid.status = "pending"
        next_bid.deadline = bid.deadline + timedelta(minutes=15)  # 15 min after current expires
    
    db.commit()
    return {
        "message": "Bid accepted, 12h countdown started",
        "bidder_id": bid.bidder_id,
        "deadline": bid.deadline
    }

@router.post("/swipe", response_model=SwipeResponse, status_code=201)
def swipe_product(swipe: SwipeCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Record a swipe action (for AI learning).
    Direction: "right" = like/offer, "left" = pass.
    """
    # Don't swipe your own product
    product = db.query(Product).filter(Product.id == swipe.product_id).first()
    if not product or product.owner_id == user_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_swipe = SwipeHistory(
        user_id=user_id,
        product_id=swipe.product_id,
        swipe_direction=swipe.swipe_direction,
        swipe_time=datetime.utcnow()
    )
    db.add(new_swipe)
    db.commit()
    db.refresh(new_swipe)
    return new_swipe
