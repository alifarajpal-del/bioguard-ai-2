"""
Pydantic models and schemas for type safety and validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VerdictType(str, Enum):
    """Health verdict classification."""
    SAFE = "SAFE"
    WARNING = "WARNING"
    DANGER = "DANGER"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NutritionData(BaseModel):
    """Nutritional information model."""
    protein: str = Field(default="0g")
    carbs: str = Field(default="0g")
    fats: str = Field(default="0g")
    sodium: str = Field(default="0mg")
    sugar: Optional[str] = None
    fiber: Optional[str] = None
    calories: Optional[int] = None


class HealthScore(BaseModel):
    """Health scoring model."""
    score: int = Field(ge=0, le=100)
    reasoning: str
    confidence: ConfidenceLevel


class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    allergies: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    dietary_preferences: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NutritionConflict(BaseModel):
    """Nutrition conflict model."""
    factor: str
    conflicts_with: str
    severity: str = Field(description="low/medium/high")
    explanation: str
    recommendation: Optional[str] = None


class FoodAnalysisResult(BaseModel):
    """Complete food analysis result model."""
    name: str
    health_score: int
    nova_score: int
    verdict: VerdictType
    macros: NutritionData
    ingredients: List[str] = Field(default_factory=list)
    clinical_verdict: str
    warnings: List[str] = Field(default_factory=list)
    bio_alternative: Optional[str] = None
    confidence_level: ConfidenceLevel
    decision_trace: List[str] = Field(default_factory=list)
    long_term_projection: Optional[Dict[str, Any]] = None
    nutrition_conflicts: List[NutritionConflict] = Field(default_factory=list)
    medical_file_correlation: Optional[str] = None
    freshness_assessment: Optional[str] = None
    spectral_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DetectionResult(BaseModel):
    """Real-time detection result from vision module."""
    object_type: str
    confidence: float
    bounding_box: Dict[str, int]  # {x1, y1, x2, y2}
    micro_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BiologicalTwinPrediction(BaseModel):
    """Biological Digital Twin prediction."""
    food_name: str
    predicted_impact: str
    confidence: float
    metrics: Dict[str, Any]
    time_horizon: str
    recommendation: str


class GraphConflict(BaseModel):
    """Knowledge graph conflict representation."""
    node_a: str
    node_b: str
    relationship: str
    severity: str
    evidence: List[str] = Field(default_factory=list)


class FederatedLearningUpdate(BaseModel):
    """Local model update for federated learning."""
    client_id: str
    update_timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_weights: Dict[str, Any]
    accuracy: float
    data_points_count: int
