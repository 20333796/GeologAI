"""
Database initialization script
"""
import logging
from app.db.session import Base, engine, init_db, SessionLocal
from app.models import (
    User, Project, WellLog, CurveData, AIModel, Prediction, AuditLog
)

logger = logging.getLogger(__name__)


def init_database():
    """
    Initialize database tables
    """
    try:
        logger.info("Creating database tables...")
        init_db()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


def create_sample_data():
    """
    Create sample data for testing (optional)
    """
    try:
        db = SessionLocal()
        
        # Check if sample data already exists
        user_count = db.query(User).count()
        if user_count > 0:
            logger.info("Sample data already exists")
            return
        
        logger.info("Creating sample data...")
        
        # Create sample admin user
        from app.core.security import SecurityUtility
        
        admin_user = User(
            username="admin",
            email="admin@geologai.com",
            password_hash=SecurityUtility.hash_password("Admin@123456"),
            real_name="Administrator",
            role="admin",
            status="active"
        )
        db.add(admin_user)
        db.commit()
        
        logger.info("✅ Sample data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    init_database()
    create_sample_data()
