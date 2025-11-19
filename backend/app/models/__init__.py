"""
SQLAlchemy ORM Models for Database
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    """User roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UserStatus(str, enum.Enum):
    """User status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class ProjectStatus(str, enum.Enum):
    """Project status"""
    PLANNING = "planning"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class LogStatus(str, enum.Enum):
    """Well log processing status"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelStatus(str, enum.Enum):
    """AI Model status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class PredictionStatus(str, enum.Enum):
    """Prediction result status"""
    SUCCESS = "success"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(100))
    avatar_url = Column(String(255))
    phone = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    logs = relationship("WellLog", back_populates="upload_user")
    models = relationship("AIModel", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_status', 'status'),
        Index('idx_user_role', 'role'),
    )


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(255))
    depth_from = Column(Float)
    depth_to = Column(Float)
    well_diameter = Column(Float)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    logs = relationship("WellLog", back_populates="project")
    
    __table_args__ = (
        Index('idx_project_owner', 'owner_id'),
        Index('idx_project_status', 'status'),
    )


class WellLog(Base):
    """Well log data model"""
    __tablename__ = "well_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512))
    file_size = Column(Integer)
    depth_from = Column(Float)
    depth_to = Column(Float)
    sample_count = Column(Integer)
    curves_json = Column(JSON)  # Store available curves as JSON
    upload_user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(LogStatus), default=LogStatus.PROCESSING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="logs")
    upload_user = relationship("User", back_populates="logs")
    curves = relationship("CurveData", back_populates="log")
    predictions = relationship("Prediction", back_populates="log")
    
    __table_args__ = (
        Index('idx_log_project', 'project_id'),
        Index('idx_log_status', 'status'),
    )


class CurveData(Base):
    """Individual curve data points"""
    __tablename__ = "curve_data"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("well_logs.id"), nullable=False)
    curve_name = Column(String(50))
    depth = Column(Float)
    value = Column(Float)
    quality_flag = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    log = relationship("WellLog", back_populates="curves")
    
    __table_args__ = (
        Index('idx_curve_log_depth', 'log_id', 'depth'),
    )


class AIModel(Base):
    """AI Model information"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50))
    description = Column(Text)
    model_type = Column(String(50))  # 'predictor', 'classifier', 'analyzer'
    accuracy = Column(Float)
    model_path = Column(String(512))
    parameters_json = Column(JSON)
    creator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(ModelStatus), default=ModelStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="models")
    predictions = relationship("Prediction", back_populates="model")
    
    __table_args__ = (
        Index('idx_model_status', 'status'),
    )


class Prediction(Base):
    """Model prediction results"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("well_logs.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    depth_from = Column(Float)
    depth_to = Column(Float)
    results_json = Column(JSON)
    confidence = Column(Float)
    execution_time = Column(Integer)  # milliseconds
    status = Column(Enum(PredictionStatus), default=PredictionStatus.SUCCESS)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    log = relationship("WellLog", back_populates="predictions")
    model = relationship("AIModel", back_populates="predictions")
    
    __table_args__ = (
        Index('idx_prediction_log', 'log_id'),
        Index('idx_prediction_model', 'model_id'),
        Index('idx_prediction_status', 'status'),
    )


class AuditLog(Base):
    """Operation audit log"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    changes_json = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
