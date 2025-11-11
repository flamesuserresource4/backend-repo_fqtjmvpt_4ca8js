"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Example schemas (kept for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Gold trading SaaS specific schemas
class Subscriber(BaseModel):
    """
    Subscribers to the signal service
    Collection name: "subscriber"
    """
    email: EmailStr = Field(..., description="Subscriber email")
    plan: Literal['monthly', 'yearly'] = Field(..., description="Subscription plan")
    status: Literal['active', 'trial', 'canceled', 'past_due'] = Field('active', description="Billing status")
    started_at: Optional[datetime] = Field(None, description="Start date of subscription")

class Signal(BaseModel):
    """
    AI-generated trading signal for XAUUSD
    Collection name: "signal"
    """
    symbol: Literal['XAUUSD'] = Field('XAUUSD', description="Trading pair")
    action: Literal['BUY', 'SELL'] = Field(..., description="Recommended action")
    entry: Optional[float] = Field(None, description="Suggested entry price")
    stop_loss: Optional[float] = Field(None, description="Suggested stop loss")
    take_profit: Optional[float] = Field(None, description="Suggested take profit")
    confidence: Optional[int] = Field(None, ge=0, le=100, description="AI confidence score")
    timeframe: Optional[str] = Field('M15', description="Chart timeframe, e.g., M15, H1")
    snapshot_url: Optional[str] = Field(None, description="URL to chart snapshot image")
    note: Optional[str] = Field(None, description="Additional commentary")
