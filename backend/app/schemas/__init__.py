"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
import json
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    real_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password_hash: str


# Authentication Schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional['UserResponse'] = None
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    depth_from: Optional[float] = None
    depth_to: Optional[float] = None
    well_diameter: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    logs: List['WellLogResponse'] = []


class ProjectListResponse(BaseModel):
    data: List[ProjectResponse]
    total: int
    skip: int
    limit: int


# Well Log Schemas
class WellLogBase(BaseModel):
    filename: str
    file_size: int
    depth_from: Optional[float] = None
    depth_to: Optional[float] = None
    sample_count: Optional[int] = None
    file_path: Optional[str] = None
    curves_json: Optional[dict] = None


class WellLogCreate(WellLogBase):
    pass


class WellLogUpdate(BaseModel):
    status: Optional[str] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None


class WellLogResponse(WellLogBase):
    id: int
    project_id: int
    upload_user_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WellLogListResponse(BaseModel):
    data: List[WellLogResponse]
    total: int
    skip: int
    limit: int


# Curve Data Schemas
class CurveDataBase(BaseModel):
    curve_name: str
    depth: float
    value: float
    quality_flag: int = 0


class CurveDataResponse(CurveDataBase):
    id: int
    log_id: int
    
    class Config:
        from_attributes = True


# AI Model Schemas
class AIModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: Optional[str] = None
    description: Optional[str] = None
    model_type: str
    accuracy: Optional[float] = None


class AIModelCreate(AIModelBase):
    model_path: str
    parameters_json: Optional[dict] = None


class AIModelUpdate(BaseModel):
    accuracy: Optional[float] = None
    status: Optional[str] = None


class AIModelResponse(AIModelBase):
    id: int
    creator_id: Optional[int]
    model_path: Optional[str]
    parameters_json: Optional[dict]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Prediction Schemas
class PredictionCreate(BaseModel):
    log_id: int
    model_id: int
    results_json: Optional[Union[dict, str]] = None
    # Allow creation with arbitrary float so service layer can validate range and return controlled errors
    confidence: float
    execution_time: Optional[float] = None

    @validator('results_json', pre=True)
    def parse_results_json(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v


class PredictionUpdate(BaseModel):
    results_json: Optional[dict] = None
    confidence: Optional[float] = None
    status: Optional[str] = None


class PredictionResponse(BaseModel):
    id: int
    log_id: int
    model_id: int
    results_json: Optional[dict]
    confidence: float
    execution_time: Optional[float]
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    data: List[PredictionResponse]
    total: int
    skip: int
    limit: int


# Pagination Schemas
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List


class UserListResponse(BaseModel):
    data: List[UserResponse]
    total: int
    skip: int
    limit: int


# Generic Response Schema
class ResponseSchema(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Error Response Schema
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    code: int
    message: str
    errors: Optional[List[ErrorDetail]] = None


# Update all forward references
ProjectDetailResponse.update_forward_refs()
