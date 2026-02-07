import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.profile import OperatorProfile


def seed_database():
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@port.dz").first()
        
        if not existing_admin:
            # Create admin user
            admin_user = User(
                email="admin@port.dz",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"Admin user created successfully with ID: {admin_user.id}")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()