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
        
        # Check if demo user already exists
        demo_user = db.query(User).filter(User.username == "demo_user").first()
        if demo_user:
            logger.info("Demo user already exists")
            db.close()
            return
        
        logger.info("Creating demo user...")
        
        # Create demo user
        from app.core.security import SecurityUtility
        
        demo = User(
            username="demo_user",
            email="demo@geologai.com",
            password_hash=SecurityUtility.hash_password("DemoUser123"),
            real_name="演示用户",
            role="user",
            status="active"
        )
        db.add(demo)
        
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin = User(
                username="admin",
                email="admin@geologai.com",
                password_hash=SecurityUtility.hash_password("Admin@123456"),
                real_name="Administrator",
                role="admin",
                status="active"
            )
            db.add(admin)
        
        db.commit()
        logger.info("✅ Demo user created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create demo user: {e}")
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
