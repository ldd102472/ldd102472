from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Enums for Categories and Status
class FeedbackCategory(str, Enum):
    USER_INTERFACE = "user_interface"
    SOCIAL_FEATURES = "social_features"
    CONTENT = "content"
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    OTHER = "other"

class FeedbackStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class FeedbackType(str, Enum):
    FEEDBACK = "feedback"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Enhanced Models for Feedback System
class FeedbackBase(BaseModel):
    title: str
    description: str
    category: FeedbackCategory
    type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 star rating
    is_anonymous: bool = False
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: FeedbackStatus = FeedbackStatus.PENDING
    priority: Priority = Priority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    admin_notes: Optional[str] = None
    admin_response: Optional[str] = None

class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    priority: Optional[Priority] = None
    admin_notes: Optional[str] = None
    admin_response: Optional[str] = None

class SuggestionBase(BaseModel):
    title: str
    description: str
    category: FeedbackCategory
    rating: Optional[int] = Field(None, ge=1, le=5)  # Interest rating
    is_anonymous: bool = False
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    expected_benefit: Optional[str] = None

class SuggestionCreate(SuggestionBase):
    pass

class Suggestion(SuggestionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: FeedbackStatus = FeedbackStatus.PENDING
    priority: Priority = Priority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    admin_notes: Optional[str] = None
    admin_response: Optional[str] = None
    votes: int = 0  # Community voting for suggestions

class UserAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    page_path: str
    action: str  # 'view', 'click', 'submit', etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

class CategoryStats(BaseModel):
    category: FeedbackCategory
    feedback_count: int
    suggestion_count: int
    average_rating: Optional[float] = None
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

# Feedback and Suggestions API Endpoints

@api_router.post("/feedback", response_model=Feedback)
async def create_feedback(feedback: FeedbackCreate):
    """Submit new feedback"""
    feedback_dict = feedback.dict()
    feedback_obj = Feedback(**feedback_dict)
    await db.feedback.insert_one(feedback_obj.dict())
    return feedback_obj

@api_router.get("/feedback", response_model=List[Feedback])
async def get_feedback(
    status: Optional[FeedbackStatus] = None,
    category: Optional[FeedbackCategory] = None,
    priority: Optional[Priority] = None,
    feedback_type: Optional[FeedbackType] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get feedback with optional filtering"""
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    if category:
        filter_dict["category"] = category
    if priority:
        filter_dict["priority"] = priority
    if feedback_type:
        filter_dict["type"] = feedback_type
    
    feedback_list = await db.feedback.find(filter_dict).skip(skip).limit(limit).to_list(limit)
    return [Feedback(**feedback) for feedback in feedback_list]

@api_router.get("/feedback/{feedback_id}", response_model=Feedback)
async def get_feedback_by_id(feedback_id: str):
    """Get specific feedback by ID"""
    feedback = await db.feedback.find_one({"id": feedback_id})
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return Feedback(**feedback)

@api_router.patch("/feedback/{feedback_id}", response_model=Feedback)
async def update_feedback(feedback_id: str, update_data: FeedbackUpdate):
    """Update feedback (admin function)"""
    feedback = await db.feedback.find_one({"id": feedback_id})
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.feedback.update_one({"id": feedback_id}, {"$set": update_dict})
    updated_feedback = await db.feedback.find_one({"id": feedback_id})
    return Feedback(**updated_feedback)

@api_router.post("/suggestions", response_model=Suggestion)
async def create_suggestion(suggestion: SuggestionCreate):
    """Submit new suggestion"""
    suggestion_dict = suggestion.dict()
    suggestion_obj = Suggestion(**suggestion_dict)
    await db.suggestions.insert_one(suggestion_obj.dict())
    return suggestion_obj

@api_router.get("/suggestions", response_model=List[Suggestion])
async def get_suggestions(
    status: Optional[FeedbackStatus] = None,
    category: Optional[FeedbackCategory] = None,
    priority: Optional[Priority] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get suggestions with optional filtering"""
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    if category:
        filter_dict["category"] = category
    if priority:
        filter_dict["priority"] = priority
    
    suggestions_list = await db.suggestions.find(filter_dict).skip(skip).limit(limit).to_list(limit)
    return [Suggestion(**suggestion) for suggestion in suggestions_list]

@api_router.patch("/suggestions/{suggestion_id}", response_model=Suggestion)
async def update_suggestion(suggestion_id: str, update_data: FeedbackUpdate):
    """Update suggestion (admin function)"""
    suggestion = await db.suggestions.find_one({"id": suggestion_id})
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.suggestions.update_one({"id": suggestion_id}, {"$set": update_dict})
    updated_suggestion = await db.suggestions.find_one({"id": suggestion_id})
    return Suggestion(**updated_suggestion)

@api_router.post("/suggestions/{suggestion_id}/vote")
async def vote_suggestion(suggestion_id: str):
    """Vote for a suggestion (community feature)"""
    suggestion = await db.suggestions.find_one({"id": suggestion_id})
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    await db.suggestions.update_one({"id": suggestion_id}, {"$inc": {"votes": 1}})
    return {"message": "Vote recorded successfully"}

@api_router.post("/analytics", response_model=UserAnalytics)
async def track_user_analytics(analytics: UserAnalytics):
    """Track user interactions for analytics"""
    await db.analytics.insert_one(analytics.dict())
    return analytics

@api_router.get("/categories/stats", response_model=List[CategoryStats])
async def get_category_stats():
    """Get statistics for each category"""
    stats = []
    for category in FeedbackCategory:
        # Count feedback in this category
        feedback_count = await db.feedback.count_documents({"category": category})
        suggestion_count = await db.suggestions.count_documents({"category": category})
        
        # Calculate average rating
        feedback_ratings = await db.feedback.find(
            {"category": category, "rating": {"$exists": True}}
        ).to_list(None)
        suggestion_ratings = await db.suggestions.find(
            {"category": category, "rating": {"$exists": True}}
        ).to_list(None)
        
        all_ratings = [f["rating"] for f in feedback_ratings if f.get("rating")] + \
                     [s["rating"] for s in suggestion_ratings if s.get("rating")]
        
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else None
        
        stats.append(CategoryStats(
            category=category,
            feedback_count=feedback_count,
            suggestion_count=suggestion_count,
            average_rating=avg_rating
        ))
    
    return stats

@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard data"""
    # Get counts by status
    total_feedback = await db.feedback.count_documents({})
    total_suggestions = await db.suggestions.count_documents({})
    pending_feedback = await db.feedback.count_documents({"status": FeedbackStatus.PENDING})
    pending_suggestions = await db.suggestions.count_documents({"status": FeedbackStatus.PENDING})
    high_priority = await db.feedback.count_documents({"priority": Priority.HIGH}) + \
                   await db.suggestions.count_documents({"priority": Priority.HIGH})
    
    # Get recent feedback
    recent_feedback = await db.feedback.find({}).sort("created_at", -1).limit(5).to_list(5)
    recent_suggestions = await db.suggestions.find({}).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "overview": {
            "total_feedback": total_feedback,
            "total_suggestions": total_suggestions,
            "pending_feedback": pending_feedback,
            "pending_suggestions": pending_suggestions,
            "high_priority_items": high_priority
        },
        "recent_feedback": [Feedback(**f) for f in recent_feedback],
        "recent_suggestions": [Suggestion(**s) for s in recent_suggestions]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
