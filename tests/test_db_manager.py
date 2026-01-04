"""
Tests for Database Manager (database/db_manager.py)
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime

from database.db_manager import DatabaseManager


class TestDatabaseInitialization:
    """Test database initialization and table creation."""
    
    def test_create_tables(self, temp_db_path):
        """Test that all required tables are created."""
        db = DatabaseManager(db_path=temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        
        # Check food_analysis table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='food_analysis'")
        assert cursor.fetchone() is not None
        
        # Check medical_files table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='medical_files'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_column_types(self, temp_db_path):
        """Test that column types are correct."""
        db = DatabaseManager(db_path=temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check food_analysis columns
        cursor.execute("PRAGMA table_info(food_analysis)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert columns.get('health_score') == 'INTEGER'
        assert columns.get('nova_score') == 'INTEGER'
        assert columns.get('product') == 'TEXT'
        
        conn.close()


class TestUserManagement:
    """Test user creation and authentication."""
    
    def test_create_user(self, temp_db_path, sample_user_data):
        """Test user creation."""
        db = DatabaseManager(db_path=temp_db_path)
        
        result = db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        assert result is True
    
    def test_create_duplicate_user(self, temp_db_path, sample_user_data):
        """Test that duplicate usernames are rejected."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        # Try to create again
        result = db.create_user(
            sample_user_data['username'],
            'different_password',
            'different@email.com'
        )
        
        assert result is False
    
    def test_verify_credentials(self, temp_db_path, sample_user_data):
        """Test password verification."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        # Correct password
        assert db.verify_credentials(
            sample_user_data['username'],
            sample_user_data['password']
        ) is True
        
        # Wrong password
        assert db.verify_credentials(
            sample_user_data['username'],
            'wrong_password'
        ) is False
    
    def test_get_user_profile(self, temp_db_path, sample_user_data):
        """Test retrieving user profile."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        profile = db.get_user_profile(sample_user_data['username'])
        
        assert profile is not None
        assert profile['username'] == sample_user_data['username']
        assert profile['email'] == sample_user_data['email']


class TestFoodAnalysis:
    """Test food analysis storage and retrieval."""
    
    def test_save_food_analysis(self, temp_db_path, sample_user_data, sample_analysis_result):
        """Test saving food analysis results."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        analysis_id = db.save_food_analysis(
            sample_user_data['username'],
            sample_analysis_result
        )
        
        assert analysis_id is not None
        assert isinstance(analysis_id, int)
    
    def test_get_user_history(self, temp_db_path, sample_user_data, sample_analysis_result):
        """Test retrieving user analysis history."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        # Save multiple analyses
        for i in range(3):
            result = sample_analysis_result.copy()
            result['product'] = f"Test Product {i}"
            db.save_food_analysis(sample_user_data['username'], result)
        
        history = db.get_user_history(sample_user_data['username'], limit=10)
        
        assert len(history) == 3
        assert all('product' in item for item in history)
    
    def test_health_score_type_conversion(self, temp_db_path, sample_user_data):
        """Test that health_score is properly converted to INTEGER."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        # Save with string health_score
        analysis = {
            'product': 'Test Product',
            'health_score': '85',  # String
            'verdict': 'SAFE',
            'warnings': [],
            'nova_score': '2'  # String
        }
        
        analysis_id = db.save_food_analysis(sample_user_data['username'], analysis)
        
        # Retrieve and verify
        history = db.get_user_history(sample_user_data['username'], limit=1)
        assert len(history) == 1
        assert isinstance(history[0]['health_score'], int)
        assert history[0]['health_score'] == 85


class TestMedicalFiles:
    """Test medical file storage."""
    
    def test_save_medical_file(self, temp_db_path, sample_user_data):
        """Test saving medical file metadata."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        file_id = db.save_medical_file(
            username=sample_user_data['username'],
            file_path='/path/to/file.pdf',
            file_type='Lab',
            summary='Blood test results'
        )
        
        assert file_id is not None
    
    def test_get_medical_files(self, temp_db_path, sample_user_data):
        """Test retrieving medical files."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        # Save multiple files
        for i in range(2):
            db.save_medical_file(
                username=sample_user_data['username'],
                file_path=f'/path/to/file{i}.pdf',
                file_type='Lab',
                summary=f'Test {i}'
            )
        
        files = db.get_medical_files(sample_user_data['username'])
        
        assert len(files) >= 2
        assert all('file_path' in f for f in files)


class TestVectorDatabase:
    """Test ChromaDB vector operations."""
    
    def test_add_to_vector_db(self, temp_db_path, sample_user_data, sample_analysis_result):
        """Test adding documents to vector database."""
        db = DatabaseManager(db_path=temp_db_path)
        
        try:
            db._add_to_vector_db(
                analysis_id=1,
                username=sample_user_data['username'],
                analysis_data=sample_analysis_result
            )
            # If no error, test passes
            assert True
        except Exception as e:
            # ChromaDB might not be available in test environment
            pytest.skip(f"ChromaDB not available: {e}")
    
    def test_semantic_search(self, temp_db_path):
        """Test semantic search functionality."""
        db = DatabaseManager(db_path=temp_db_path)
        
        try:
            results = db.semantic_search("healthy snacks", limit=5)
            assert isinstance(results, list)
        except Exception as e:
            pytest.skip(f"ChromaDB not available: {e}")


class TestDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_foreign_key_constraint(self, temp_db_path, sample_analysis_result):
        """Test that foreign key constraints work."""
        db = DatabaseManager(db_path=temp_db_path)
        
        # Try to save analysis for non-existent user
        with pytest.raises(Exception):
            db.save_food_analysis('nonexistent_user', sample_analysis_result)
    
    def test_timestamp_auto_creation(self, temp_db_path, sample_user_data, sample_analysis_result):
        """Test that timestamps are automatically created."""
        db = DatabaseManager(db_path=temp_db_path)
        
        db.create_user(
            sample_user_data['username'],
            sample_user_data['password'],
            sample_user_data['email']
        )
        
        db.save_food_analysis(sample_user_data['username'], sample_analysis_result)
        
        history = db.get_user_history(sample_user_data['username'], limit=1)
        assert 'timestamp' in history[0]
        assert history[0]['timestamp'] is not None
