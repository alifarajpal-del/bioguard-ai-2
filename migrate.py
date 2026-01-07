#!/usr/bin/env python3
"""
Database migration script for BioGuard AI.
Handles schema updates and data migrations.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from app_config.settings import DATABASE_PATH


def migrate_add_roles():
    """Add role column to users table."""
    print("📊 Migration: Adding roles to users table...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if role column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            conn.commit()
            print("✅ Added 'role' column to users table")
        else:
            print("ℹ️  'role' column already exists")
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def migrate_add_encryption_fields():
    """Add fields for encrypted data."""
    print("📊 Migration: Adding encryption fields...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'encrypted_email' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN encrypted_email TEXT")
            print("✅ Added 'encrypted_email' column")
        
        if 'phone_number' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
            print("✅ Added 'phone_number' column")
        
        conn.commit()
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def migrate_add_dri_fields():
    """Add DRI (Daily Recommended Intake) fields."""
    print("📊 Migration: Adding DRI tracking fields...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_fields = {
            'daily_calories_target': 'INTEGER DEFAULT 2000',
            'daily_protein_target': 'INTEGER DEFAULT 50',
            'daily_carbs_target': 'INTEGER DEFAULT 250',
            'daily_fat_target': 'INTEGER DEFAULT 70',
            'daily_fiber_target': 'INTEGER DEFAULT 25',
        }
        
        for field, definition in new_fields.items():
            if field not in columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {field} {definition}")
                print(f"✅ Added '{field}' column")
        
        conn.commit()
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def migrate_add_federated_learning_table():
    """Create federated learning updates table."""
    print("📊 Migration: Creating federated learning table...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fl_updates (
                update_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                model_version TEXT NOT NULL,
                update_data BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        conn.commit()
        print("✅ Created 'fl_updates' table")
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def run_all_migrations():
    """Run all pending migrations."""
    print("="*60)
    print("🚀 Starting BioGuard AI Database Migrations")
    print("="*60)
    
    # Ensure database exists
    db = DatabaseManager()
    print(f"📁 Database: {DATABASE_PATH}")
    
    # Run migrations
    migrate_add_roles()
    migrate_add_encryption_fields()
    migrate_add_dri_fields()
    migrate_add_federated_learning_table()
    
    print("="*60)
    print("✅ All migrations completed successfully!")
    print("="*60)


if __name__ == "__main__":
    run_all_migrations()
