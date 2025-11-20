#!/usr/bin/env python
"""Create a demo project for testing"""
import sys
import os
from pathlib import Path

# Load .env first
backend_dir = Path("d:/GeologAI/backend").absolute()
env_file = backend_dir / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Add backend to path
sys.path.insert(0, str(backend_dir))

# Import database and models
from app.models import User, Project
from app.db.session import SessionLocal

def create_demo_project():
    """Create a demo project for test user"""
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Find or create test user
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            print("❌ Test user not found. Creating one...")
            from app.core.security import SecurityUtility
            user = User(
                username="testuser",
                email="testuser@example.com",
                real_name="Test User",
                password_hash=SecurityUtility.hash_password("TestPass123"),
                role="user",
                status="active"
            )
            db.add(user)
            db.commit()
            print(f"✅ Test user created: {user.username} (ID: {user.id})")
        else:
            print(f"✅ Test user found: {user.username} (ID: {user.id})")
        
        # Check if demo project already exists
        existing_project = db.query(Project).filter(
            Project.owner_id == user.id,
            Project.name == "Demo Project"
        ).first()
        
        if existing_project:
            print(f"✅ Demo project already exists: {existing_project.name} (ID: {existing_project.id})")
        else:
            # Create demo project
            demo_project = Project(
                name="Demo Project",
                description="演示项目用于测试各项功能",
                location="Eastern Basin, China",
                depth_from=0.0,
                depth_to=3000.0,
                well_diameter=0.2159,  # 8.5 inches
                owner_id=user.id,
                status="ONGOING"  # Use enum value
            )
            db.add(demo_project)
            db.commit()
            db.refresh(demo_project)
            print(f"✅ Demo project created: {demo_project.name} (ID: {demo_project.id})")
            print(f"   - Owner: {user.username}")
            print(f"   - Location: {demo_project.location}")
            print(f"   - Depth range: {demo_project.depth_from}m - {demo_project.depth_to}m")
        
        print("\n✅ Demo project setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_project()
