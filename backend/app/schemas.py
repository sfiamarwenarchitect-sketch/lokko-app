from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

# --- Enums ---
class ProductStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    PAUSED = "paused"
    HIDDEN = "hidden"

class ListingType(str, Enum):
    SELLING = "selling"
    BARTER = "barter"

class BidStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CASCADING = "cascading"

# --- User ---
class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_professional: bool
    trust_score: float
    created_at: datetime
    last_active: datetime
    kyc_verified: bool
    
    class Config:
        from_attributes = True

# --- Product ---
class ProductCreate(BaseModel):
    title: str
    brand: str
    description: str
    price: float
    estimated_value: float
    size: str
    condition: str
    listing_type: ListingType = ListingType.SELLING
    min_bid_percentage: float = 0.7
    duration_hours: int = 48
    images: List[str]

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    estimated_value: Optional[float] = None
    status: Optional[ProductStatus] = None

class ProductResponse(BaseModel):
    id: int
    title: str
    brand: str
    description: str
    price: float
    estimated_value: Optional[float]
    size: str
    condition: str
    listing_type: str
    status: str
    min_bid_percentage: float
    duration_hours: int
    listing_created: datetime
    listing_ends: Optional[datetime]
    ai_trust_score: float
    is_safe_haven: bool
    images: List[str]
    owner_id: int
    owner: Optional[dict] = None  # Nested user
    
    class Config:
        from_attributes = True

class ProductWithBidCount(ProductResponse):
    active_bid_count: int = 0
    highest_bid: Optional[float] = None
    time_remaining: Optional[str] = None

# --- Bid ---
class BidCreate(BaseModel):
    product_id: int
    amount: float

class BidResponse(BaseModel):
    id: int
    amount: float
    status: str
    bid_rank: int
    bid_time: datetime
    deadline: Optional[datetime]
    is_cascading_to_next: bool
    
    class Config:
        from_attributes = True

class BidWithUser(BidResponse):
    bidder: Optional[dict] = None

# --- Exchange ---
class ExchangeCreate(BaseModel):
    product_id: int
    offered_product_id: int

class ExchangeResponse(BaseModel):
    id: int
    status: str
    preference_rank: int
    deadline: Optional[datetime]
    product_id: int
    offered_product_id: Optional[int]
    
    class Config:
        from_attributes = True

# --- Swipe ---
class SwipeCreate(BaseModel):
    product_id: int
    swipe_direction: str  # "right" or "left"

class SwipeResponse(BaseModel):
    id: int
    product_id: int
    swipe_direction: str
    swipe_time: datetime

# --- AI Look Card ---
class AILookCardResponse(BaseModel):
    id: int
    title: str
    description: str
    matching_score: float
    inserted_at: datetime
    swipe_count: int

# --- Auth ---
class LoginRequest(BaseModel):
    email: str
    password: str  # Simplified for prototype

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
