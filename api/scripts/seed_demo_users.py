"""
Seed demo users for MediAI authentication.

Creates demo users in the database for testing and development.
Run this after database migrations to populate demo user accounts.

Usage:
    python api/scripts/seed_demo_users.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import SessionLocal
from core.rbac import Role
from models.user import User


def seed_demo_users():
    """Seed demo users into database"""

    # Demo users with bcrypt hash for 'demo123'
    # Generated with: bcrypt.hashpw(b'demo123', bcrypt.gensalt(12))
    DEMO_PASSWORD_HASH = "$2b$12$8Zfhb7536dY3OaHbV5RS6uefmkTUM7I3AsatOzkoHOaTHumcl71c6"

    demo_users = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@mediai.com",
            "full_name": "System Administrator",
            "hashed_password": DEMO_PASSWORD_HASH,
            "role": Role.ADMIN,
            "is_active": True,
            "is_verified": True,
            "specialty": "System Administration",
            "department": "IT",
        },
        {
            "id": 2,
            "username": "demo",
            "email": "demo@mediai.com",
            "full_name": "Demo Doctor",
            "hashed_password": DEMO_PASSWORD_HASH,
            "role": Role.DOCTOR,
            "is_active": True,
            "is_verified": True,
            "specialty": "Critical Care Medicine",
            "department": "ICU",
        },
        {
            "id": 3,
            "username": "nurse",
            "email": "nurse@mediai.com",
            "full_name": "Demo Nurse",
            "hashed_password": DEMO_PASSWORD_HASH,
            "role": Role.NURSE,
            "is_active": True,
            "is_verified": True,
            "specialty": "Critical Care Nursing",
            "department": "ICU",
        },
        {
            "id": 4,
            "username": "researcher",
            "email": "researcher@mediai.com",
            "full_name": "Demo Researcher",
            "hashed_password": DEMO_PASSWORD_HASH,
            "role": Role.RESEARCHER,
            "is_active": True,
            "is_verified": True,
            "specialty": "Clinical Research",
            "department": "Research",
        },
    ]

    db = SessionLocal()

    try:
        print("🌱 Seeding demo users...")
        print("=" * 60)

        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()

            if existing_user:
                print(f"⏭️  User '{user_data['username']}' already exists (id={existing_user.id})")
                continue

            # Create new user
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)

            print(f"✅ Created user '{user.username}' (id={user.id}, role={user.role.value})")

        print("=" * 60)
        print("✅ Demo users seeded successfully!")
        print("\nYou can now login with:")
        print("  Username: demo")
        print("  Password: demo123")

    except Exception as e:
        print(f"❌ Error seeding users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_users()
