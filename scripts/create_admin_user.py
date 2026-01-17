import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.book import Book
from app.models.api_log import APILog
from app.utils.security import get_password_hash
from app.config import settings


def create_admin_user():
    """Create admin user if it doesn't exist"""
    
    print("🔧 Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar se o admin já existe
        existing_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        
        if existing_admin:
            print(f"ℹ️  Admin user '{settings.ADMIN_USERNAME}' already exists")
            return
        
        # Criar novo usuário admin
        print(f"👤 Creating admin user '{settings.ADMIN_USERNAME}'...")
        admin_user = User(
            username=settings.ADMIN_USERNAME,
            email=f"{settings.ADMIN_USERNAME}@example.com",
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Username: {settings.ADMIN_USERNAME}")
        print(f"Password: {settings.ADMIN_PASSWORD}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()