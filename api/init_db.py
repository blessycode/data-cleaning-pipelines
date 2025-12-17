"""
Initialize Database
Create tables and default admin user
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api.database import init_db, engine, AsyncSessionLocal
    from api.db_models import Base, User
    from api.db_service import UserService
    from api.config import settings
    from api.auth import get_password_hash
except ImportError:
    from database import init_db, engine, AsyncSessionLocal
    from db_models import Base, User
    from db_service import UserService
    from config import settings
    from auth import get_password_hash


async def create_default_admin():
    """Create default admin user"""
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        admin = await UserService.get_user_by_username(db, settings.ADMIN_USERNAME)
        if not admin:
            try:
                # Ensure password is not too long for bcrypt (72 bytes)
                admin_password = settings.ADMIN_PASSWORD
                password_bytes = admin_password.encode('utf-8')
                if len(password_bytes) > 72:
                    admin_password = password_bytes[:72].decode('utf-8', errors='ignore')
                    print(f"⚠️  Admin password truncated to 72 bytes for bcrypt compatibility")
                
                admin = await UserService.create_user(
                    db=db,
                    username=settings.ADMIN_USERNAME,
                    password=admin_password,
                    email=f"{settings.ADMIN_USERNAME}@example.com",
                    role="admin"
                )
                print(f"✅ Created default admin user: {admin.username}")
            except Exception as e:
                print(f"⚠️  Could not create admin user: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"✅ Admin user already exists: {admin.username}")


async def main():
    """Initialize database"""
    print("🔄 Initializing database...")
    
    try:
        # Create tables
        await init_db()
        print("✅ Database tables created")
        
        # Create default admin
        await create_default_admin()
        
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

