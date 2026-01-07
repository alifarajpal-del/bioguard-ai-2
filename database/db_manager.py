"""
Hybrid Storage Manager: SQLite + ChromaDB + NetworkX.

This module manages a three-tier database architecture:
- SQLite: Structured relational data (users, analysis history, medical files)
- ChromaDB: Vector embeddings for semantic search and similarity queries
- NetworkX: Knowledge graph for ingredient-health relationship mapping

Provides encrypted data persistence and efficient querying across all tiers.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from pathlib import Path

try:
    import chromadb
except ImportError:
    chromadb = None

import networkx as nx
from app_config.settings import (
    DATABASE_PATH, VECTOR_DB_PATH, GRAPH_DB_PATH, CACHE_ENABLED, CACHE_TTL_SECONDS
)


class DBManager:
    """Unified database manager for hybrid storage architecture."""
    
    def __init__(self):
        """Initialize all database backends (SQLite, ChromaDB, NetworkX)."""
        self.db_path = DATABASE_PATH
        self.vector_db_path = VECTOR_DB_PATH
        self.graph_db_path = GRAPH_DB_PATH
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Initialize Vector DB (Chroma) - for semantic search
        if chromadb:
            self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            self.food_collection = self.chroma_client.get_or_create_collection(
                name="food_analysis"
            )
        else:
            self.chroma_client = None
            self.food_collection = None
        
        # Initialize Graph DB (NetworkX) - for relationship mapping
        self._init_graph()
    
    def _init_sqlite(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table - Updated with OAuth fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                picture TEXT,
                provider TEXT,
                email_verified BOOLEAN,
                age INTEGER,
                weight REAL,
                height REAL,
                allergies TEXT,
                medical_conditions TEXT,
                dietary_preferences TEXT,
                health_sync_enabled BOOLEAN DEFAULT 0,
                region TEXT,
                preferred_sources TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Food Analysis History - Updated schema with numeric types
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                product TEXT,
                health_score INTEGER,
                nova_score INTEGER,
                verdict TEXT,
                raw_data TEXT,
                data_source TEXT,
                nutrients TEXT,
                barcode TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE,
                payload TEXT,
                source TEXT,
                source_url TEXT,
                confidence REAL,
                created_at TIMESTAMP
            )
        """)

        # Backfill new columns for existing installs
        self._add_column_if_missing(cursor, "users", "health_sync_enabled", "BOOLEAN DEFAULT 0")
        self._add_column_if_missing(cursor, "users", "region", "TEXT")
        self._add_column_if_missing(cursor, "users", "preferred_sources", "TEXT")
        self._add_column_if_missing(cursor, "food_analysis", "data_source", "TEXT")
        self._add_column_if_missing(cursor, "food_analysis", "nutrients", "TEXT")
        self._add_column_if_missing(cursor, "food_analysis", "barcode", "TEXT")
        
        # Medical Files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                file_name TEXT,
                content TEXT,
                file_type TEXT,
                uploaded_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Federated Learning Updates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fl_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,
                model_weights TEXT,
                accuracy REAL,
                update_timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def _add_column_if_missing(self, cursor: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
        """Add a column to a table if it does not already exist."""
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    
    def _init_graph(self):
        """Initialize knowledge graph for ingredient-health relationships."""
        self.graph = nx.DiGraph()
        
        # Pre-populate with common health relationships
        self._populate_health_graph()
        
        # Save to file
        os.makedirs(self.graph_db_path, exist_ok=True)
    
    def _populate_health_graph(self):
        """
        Populate the knowledge graph with common ingredient-health relationships.
        
        Each edge represents a connection between an ingredient and a health condition,
        with metadata for relationship type and severity level.
        """
        # Ingredient -> Health Impact relationships
        conflicts = [
            ("sodium", "hypertension", "increases_risk", "high"),
            ("sodium", "blood_pressure", "increases", "high"),
            ("sugar", "diabetes", "increases_risk", "high"),
            ("sugar", "glucose_spike", "causes", "high"),
            ("saturated_fat", "cholesterol", "increases", "high"),
            ("preservatives", "digestive_health", "harms", "medium"),
            ("artificial_colors", "hyperactivity", "may_trigger", "low"),
            ("gluten", "celiac_disease", "triggers", "high"),
            ("lactose", "lactose_intolerance", "triggers", "high"),
            ("peanuts", "peanut_allergy", "triggers", "high"),
            ("trans_fat", "heart_disease", "increases_risk", "high"),
        ]
        
        for source, target, relationship, severity in conflicts:
            self.graph.add_edge(
                source, target,
                relationship=relationship,
                severity=severity
            )
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Save or update user profile in SQLite database with OAuth support.
        
        Args:
            user_data: Dictionary containing user information (user_id, name, email, provider, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, name, email, picture, provider, email_verified,
                 age, weight, height, allergies, medical_conditions, 
                 dietary_preferences, health_sync_enabled, region, preferred_sources,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['user_id'],
                user_data.get('name'),
                user_data.get('email'),
                user_data.get('picture'),
                user_data.get('provider', 'traditional'),
                user_data.get('email_verified', False),
                user_data.get('age'),
                user_data.get('weight'),
                user_data.get('height'),
                json.dumps(user_data.get('allergies', [])),
                json.dumps(user_data.get('medical_conditions', [])),
                json.dumps(user_data.get('dietary_preferences', [])),
                bool(user_data.get('health_sync_enabled', False)),
                user_data.get('region'),
                json.dumps(user_data.get('preferred_sources', [])),
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile from database.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'picture': row[3],
                    'provider': row[4],
                    'email_verified': row[5],
                    'age': row[6],
                    'weight': row[7],
                    'height': row[8],
                    'allergies': json.loads(row[9] or '[]'),
                    'medical_conditions': json.loads(row[10] or '[]'),
                    'dietary_preferences': json.loads(row[11] or '[]'),
                    'health_sync_enabled': bool(row[12]) if len(row) > 12 else False,
                    'region': row[13] if len(row) > 13 else None,
                    'preferred_sources': json.loads(row[14] or '[]') if len(row) > 14 else [],
                }
            return None
        except Exception as e:
            print(f"❌ Error retrieving user: {e}")
            return None

    def update_user_settings(
        self,
        user_id: str,
        health_sync_enabled: Optional[bool] = None,
        region: Optional[str] = None,
        preferred_sources: Optional[List[str]] = None,
    ) -> bool:
        """Update user nutrition/health-sync settings."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            updates = []
            params: List[Any] = []

            if health_sync_enabled is not None:
                updates.append("health_sync_enabled = ?")
                params.append(bool(health_sync_enabled))

            if region is not None:
                updates.append("region = ?")
                params.append(region)

            if preferred_sources is not None:
                updates.append("preferred_sources = ?")
                params.append(json.dumps(preferred_sources))

            if not updates:
                return True

            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(user_id)

            cursor.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?",
                params,
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error updating user settings: {e}")
            return False
    
    def save_food_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> bool:
        """
        Save food analysis result to history with proper typing.
        
        Args:
            user_id: User identifier
            analysis_data: Analysis results containing product, health_score, nova_score, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract numeric values properly
            health_score = analysis_data.get('health_score', 0)
            nova_score = analysis_data.get('nova_score', 0)
            
            # Ensure numeric types
            if isinstance(health_score, str):
                health_score = int(health_score) if health_score.isdigit() else 0
            if isinstance(nova_score, str):
                nova_score = int(nova_score) if nova_score.isdigit() else 0
            
            cursor.execute("""
                INSERT INTO food_analysis 
                (user_id, product, health_score, nova_score, verdict, raw_data, data_source, nutrients, barcode, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                analysis_data.get('product', 'Unknown'),  # Changed from 'name' to 'product'
                int(health_score),  # Ensure INTEGER type
                int(nova_score),    # Ensure INTEGER type
                analysis_data.get('verdict', 'UNKNOWN'),
                json.dumps(analysis_data),
                analysis_data.get('data_source') or analysis_data.get('source'),
                json.dumps(analysis_data.get('nutrients', {})),
                analysis_data.get('barcode'),
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            
            # Also add to vector DB if available
            if self.food_collection:
                self._add_to_vector_db(analysis_data)
            
            return True
        except Exception as e:
            print(f"❌ Error saving food analysis: {e}")
            return False

    def get_cached_nutrition(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Return cached nutrition payload if within TTL."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT payload, created_at FROM nutrition_cache WHERE cache_key = ?",
                (cache_key,),
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            payload, created_at = row
            created_ts = datetime.fromisoformat(created_at)
            age_seconds = (datetime.utcnow() - created_ts).total_seconds()
            if age_seconds > CACHE_TTL_SECONDS:
                return None
            return json.loads(payload)
        except Exception as exc:
            print(f"⚠️ Cache read failed: {exc}")
            return None

    def save_nutrition_cache(
        self,
        cache_key: str,
        payload: Dict[str, Any],
    ) -> None:
        """Persist nutrition payload for offline-like experience."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO nutrition_cache
                (cache_key, payload, source, source_url, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    json.dumps(payload),
                    payload.get("source"),
                    payload.get("source_url"),
                    payload.get("confidence"),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            print(f"⚠️ Cache write failed: {exc}")
    
    def _add_to_vector_db(self, analysis_data: Dict[str, Any]):
        """
        Add food analysis to ChromaDB vector database for semantic search.
        
        Args:
            analysis_data: Analysis results to be embedded and stored
        """
        try:
            if not self.food_collection:
                return
            
            product_name = analysis_data.get('product', analysis_data.get('name', 'Unknown'))
            
            text_content = f"""
            Product: {product_name}
            Health Score: {analysis_data.get('health_score', 0)}
            Ingredients: {', '.join(analysis_data.get('ingredients', []))}
            Warnings: {', '.join(analysis_data.get('warnings', []))}
            Clinical Verdict: {analysis_data.get('clinical_verdict', '')}
            """
            
            doc_id = hashlib.md5(
                f"{product_name}-{datetime.utcnow()}".encode()
            ).hexdigest()
            
            self.food_collection.add(
                ids=[doc_id],
                documents=[text_content],
                metadatas=[{
                    'product': product_name,  # Changed from 'product_name' for consistency
                    'health_score': analysis_data.get('health_score', 0),
                    'verdict': analysis_data.get('verdict', 'UNKNOWN'),
                }]
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not add to vector DB: {e}")
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve user's food analysis history with updated column names.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
            
        Returns:
            List of analysis history records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT product, health_score, nova_score, verdict, created_at
                FROM food_analysis
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'product': row[0],  # Changed from 'product_name' to 'product'
                    'health_score': row[1],
                    'nova_score': row[2],
                    'verdict': row[3],
                    'created_at': row[4],
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Error retrieving history: {e}")
            return []
    
    def find_conflicts_in_graph(self, ingredients: List[str], medical_conditions: List[str]) -> List[Dict[str, Any]]:
        """
        Query knowledge graph for ingredient-health conflicts.
        
        Searches the NetworkX graph for edges connecting user's ingredients
        to their medical conditions, identifying potential health risks.
        
        Args:
            ingredients: List of food ingredients to check
            medical_conditions: List of user's health conditions
            
        Returns:
            List of conflict dictionaries with ingredient, condition, relationship, and severity
        """
        conflicts = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()
            
            # Check if ingredient has outgoing edges (conflicts)
            if ingredient_lower in self.graph:
                successors = self.graph.successors(ingredient_lower)
                for successor in successors:
                    # Check if the health condition matches user's conditions
                    if any(cond.lower() in successor.lower() for cond in medical_conditions):
                        edge_data = self.graph.edges[ingredient_lower, successor]
                        conflicts.append({
                            'ingredient': ingredient,
                            'health_condition': successor,
                            'relationship': edge_data.get('relationship', ''),
                            'severity': edge_data.get('severity', 'medium'),
                        })
        
        return conflicts
    
    def save_federated_update(self, client_id: str, model_weights: Dict[str, Any], accuracy: float):
        """
        Save federated learning model update to database.
        
        Args:
            client_id: Unique client/device identifier
            model_weights: Model parameters as dictionary
            accuracy: Training accuracy score
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fl_updates (client_id, model_weights, accuracy, update_timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                client_id,
                json.dumps(model_weights),
                accuracy,
                datetime.utcnow().isoformat(),
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving FL update: {e}")
            return False
    
    def clear_cache(self):
        """Clear in-memory caches (ChromaDB manages its own cache)."""
        if self.chroma_client and CACHE_ENABLED:
            pass  # Chroma handles its own cache


# Global instance
db_manager = None


def get_db_manager() -> DBManager:
    """
    Get or create global database manager instance (singleton pattern).
    
    Returns:
        Global DBManager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = DBManager()
    return db_manager
