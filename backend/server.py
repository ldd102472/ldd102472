from fastapi import FastAPI, APIRouter
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

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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
