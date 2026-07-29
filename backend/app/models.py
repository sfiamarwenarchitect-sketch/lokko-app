from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta
import enum

Base = declarative_base()

# --- Enums ---
class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    SOLD = "sold"
    PAUSED = "paused"
    HIDDEN = "hidden"

class ListingType(str, enum.Enum):
    SELLING = "selling"
    BARTER = "barter"

class BidStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CASCADING = "cascading"

# --- User ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    is_professional = Column(Boolean, default=False)
    trust_score = Column(Float, default=85.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_vacation_mode = Column(Boolean, default=False)
    vacation_starts = Column(DateTime)
    vacation_ends = Column(DateTime)
    kyc_verified = Column(Boolean, default=False)
    kyc_docs = Column(JSON)
    
    # Relationships
    products = relationship("Product", back_populates="owner")
    bids_made = relationship("Bid", back_populates="bidder")
    bids_received = relationship("Bid", back_populates="product")

# --- Product ---
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    brand = Column(String(100))
    description = Column(Text)
    price = Column(Float, nullable=False)  # Starting price
    estimated_value = Column(Float)  # Private estimation by seller
    size = Column(String(20))
    condition = Column(String(50))  # New, Like New, Good, Vintage
    listing_type = Column(String(20), default=ListingType.SELLING.value)
    status = Column(String(20), default=ProductStatus.ACTIVE.value)
    min_bid_percentage = Column(Float, default=0.7)  # 70% rule
    duration_hours = Column(Integer, default=48)
    listing_created = Column(DateTime, default=datetime.utcnow)
    listing_ends = Column(DateTime)
    ai_trust_score = Column(Float, default=85.0)  # AI confidence
    is_safe_haven = Column(Boolean, default=False)  # Relégué en échange uniquement
    images = Column(JSON)  # [url1, url2, ...]
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")
    bids = relationship("Bid", back_populates="product", order_by="Bid.amount.desc()")
    exchanges = relationship("Exchange", back_populates="product")
    ai_look_cards = relationship("AILookCard", back_populates="product")

# --- Bid (Private Offer) ---
class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default=BidStatus.PENDING.value)
    bid_rank = Column(Integer, default=1)  # 1 = best price, 2 = second, etc.
    bid_time = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime)  # 12h countdown from acceptance
    
    # Relationships
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="bids")
    bidder_id = Column(Integer, ForeignKey("users.id"))
    bidder = relationship("User", back_populates="bids_made")
    
    # Cascade chain
    is_cascading_to_next = Column(Boolean, default=False)
    next_bidder_id = Column(Integer, ForeignKey("users.id"), nullable=True)

# --- Exchange (Loop Bartering) ---
class Exchange(Base):
    __tablename__ = "exchanges"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), default="pending")
    preference_rank = Column(Integer, default=1)
    deadline = Column(DateTime)
    
    # Relationships
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="exchanges")
    proposer_id = Column(Integer, ForeignKey("users.id"))
    proposer = relationship("User", foreign_keys=[proposer_id])
    offered_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    offered_product = relationship("Product", foreign_keys=[offered_product_id])

# --- AI Look Card (Stylist Engine) ---
class AILookCard(Base):
    __tablename__ = "ai_look_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="Look du Jour")
    description = Column(Text)
    matching_score = Column(Float, default=92.0)
    inserted_at = Column(DateTime, default=datetime.utcnow)
    swipe_count = Column(Integer, default=10)  # Inserted every N swipes
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="ai_look_cards")

# --- Swipe History (for AI learning) ---
class SwipeHistory(Base):
    __tablename__ = "swipe_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    swipe_direction = Column(String(10))  # "right" = like/offer, "left" = pass
    swipe_time = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    product = relationship("Product")

# --- Trust Log ---
class TrustLog(Base):
    __tablename__ = "trust_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50))  # "shipped_on_time", "dispute_won", "photo_verified"
    score_change = Column(Float, default=2.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    user = relationship("User")
