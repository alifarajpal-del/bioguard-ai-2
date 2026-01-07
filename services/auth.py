"""
Authentication and user management with SQLite backend.
Provides login, register, and admin functions.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List

from services.auth_privacy import get_auth_manager
from database.db_manager import get_db_manager


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app_data.db")


def ensure_db():
    """Create database and tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = password_hash.split('$')
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == pwd_hash
    except Exception:
        return False


def register_user(email: str, password: str, is_admin: bool = False) -> Dict[str, Any]:
    """
    Register a new user.
    
    Returns:
        {"success": bool, "message": str, "user_id": int or None}
    """
    ensure_db()
    
    email = email.strip().lower()
    if not email or "@" not in email:
        return {"success": False, "message": "Invalid email format"}
    
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        pwd_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)",
            (email, pwd_hash, 1 if is_admin else 0, datetime.utcnow().isoformat())
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {"success": True, "message": "User registered successfully", "user_id": user_id}
    
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Email already registered"}
    except Exception as e:
        return {"success": False, "message": f"Registration error: {str(e)}"}


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user.
    
    Returns:
        {"success": bool, "message": str, "user_id": int or None, "is_admin": bool}
    """
    ensure_db()
    
    email = email.strip().lower()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"success": False, "message": "Invalid email or password"}
        
        user_id, pwd_hash, is_admin = result
        
        if not verify_password(password, pwd_hash):
            return {"success": False, "message": "Invalid email or password"}
        
        return {
            "success": True,
            "message": "Login successful",
            "user_id": user_id,
            "is_admin": bool(is_admin)
        }
    
    except Exception as e:
        return {"success": False, "message": f"Login error: {str(e)}"}


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    ensure_db()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, is_admin, created_at FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "is_admin": bool(result[2]),
                "created_at": result[3]
            }
        return None
    
    except Exception:
        return None


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (admin only)."""
    ensure_db()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, is_admin, created_at FROM users ORDER BY created_at DESC")
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "email": r[1],
                "is_admin": bool(r[2]),
                "created_at": r[3]
            }
            for r in results
        ]
    
    except Exception:
        return []


def init_admin_user():
    """Initialize admin user if it doesn't exist."""
    ensure_db()
    
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bioguard.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "BioGuard2024!")
    
    # Check if admin exists
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE is_admin = 1")
        if cursor.fetchone():
            conn.close()
            return
        conn.close()
    except Exception:
        pass
    
    # Create admin
    register_user(admin_email, admin_password, is_admin=True)


def create_or_login_user(user_profile: Dict[str, Any]) -> str:
    """
    Create or authenticate user and generate JWT token (legacy).
    
    Args:
        user_profile: User profile dictionary containing user_id and other details
        
    Returns:
        JWT token string for authenticated session
    """
    # Save user to database
    db = get_db_manager()
    db.save_user(user_profile)
    
    # Generate JWT token
    auth = get_auth_manager()
    token = auth.generate_jwt_token(user_profile["user_id"], user_profile)
    return token


def logout(user_id: str) -> None:
    """
    Revoke user's authentication token (legacy).
    
    Args:
        user_id: Unique user identifier
    """
    auth = get_auth_manager()
    auth.revoke_token(user_id)


# Initialize on import
ensure_db()
init_admin_user()
