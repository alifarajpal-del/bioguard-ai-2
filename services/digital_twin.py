"""
Biological Digital Twin Engine.
Predicts the future impact of food consumption based on user biometrics
and real-time health data.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import math
import json
from models.schemas import BiologicalTwinPrediction


class DigitalTwinEngine:
    """Predictive engine for food impact simulation."""
    
    def __init__(self):
        """Initialize digital twin with health heuristics."""
        self.health_models = self._init_health_models()
    
    def _init_health_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize biometric models for prediction."""
        return {
            'glucose': {
                'baseline': 100,  # mg/dL
                'spike_duration_min': 45,
                'recovery_duration_min': 120,
            },
            'blood_pressure': {
                'baseline_systolic': 120,
                'baseline_diastolic': 80,
                'salt_sensitivity': 0.5,  # mg increase per 100mg sodium
            },
            'cholesterol': {
                'baseline': 200,  # mg/dL
                'sat_fat_impact': 0.1,  # mg increase per 1g sat fat
            },
            'energy': {
                'baseline': 0,
                'crash_threshold': -50,  # Fatigue indicator
            },
        }
    
    def predict_impact(
        self,
        user_biometrics: Dict[str, Any],
        food_data: Dict[str, Any]
    ) -> BiologicalTwinPrediction:
        """
        Predict the impact of consuming a food product.
        Returns detailed predictions with confidence levels.
        """
        food_name = food_data.get('name', 'Unknown')
        
        # Extract nutrition data
        nutrition = self._extract_nutrition(food_data)
        
        # Generate predictions for each metric
        predictions = {
            'glucose': self._predict_glucose(user_biometrics, nutrition),
            'blood_pressure': self._predict_blood_pressure(user_biometrics, nutrition),
            'cholesterol': self._predict_cholesterol(user_biometrics, nutrition),
            'energy': self._predict_energy(user_biometrics, nutrition),
            'digestion': self._predict_digestion(food_data),
        }
        
        # Synthesize into narrative
        impact_narrative = self._synthesize_prediction(
            food_name,
            user_biometrics,
            nutrition,
            predictions
        )
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(user_biometrics, predictions)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            predictions,
            user_biometrics,
            food_data
        )
        
        return BiologicalTwinPrediction(
            food_name=food_name,
            predicted_impact=impact_narrative,
            confidence=confidence,
            metrics=predictions,
            time_horizon='45-120 minutes post-consumption',
            recommendation=recommendation,
        )
    
    def _extract_nutrition(self, food_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract nutritional values from food data."""
        macros = food_data.get('macros', {})
        
        def parse_value(val_str: str) -> float:
            """Parse nutritional value string (e.g., '15g' -> 15)."""
            if isinstance(val_str, (int, float)):
                return float(val_str)
            if isinstance(val_str, str):
                import re
                match = re.search(r'([\d.]+)', val_str)
                return float(match.group(1)) if match else 0.0
            return 0.0
        
        return {
            'calories': food_data.get('macros', {}).get('calories', 0),
            'protein': parse_value(macros.get('protein', '0g')),
            'carbs': parse_value(macros.get('carbs', '0g')),
            'fats': parse_value(macros.get('fats', '0g')),
            'sodium': parse_value(macros.get('sodium', '0mg')),
            'sugar': parse_value(macros.get('sugar', '0g')) if 'sugar' in macros else 0,
            'fiber': parse_value(macros.get('fiber', '0g')) if 'fiber' in macros else 0,
        }
    
    def _predict_glucose(
        self,
        user_biometrics: Dict[str, Any],
        nutrition: Dict[str, float]
    ) -> Dict[str, Any]:
        """Predict glucose spike and recovery."""
        baseline = user_biometrics.get('glucose_baseline', 100)
        
        # Simple model: carbs and sugar drive glucose spikes
        carbs = nutrition.get('carbs', 0)
        sugar = nutrition.get('sugar', 0)
        
        # Spike magnitude (simplified)
        spike_magnitude = (carbs * 0.5 + sugar * 1.2) / 20
        
        # Fiber helps mitigate spike
        fiber = nutrition.get('fiber', 0)
        spike_magnitude = max(0, spike_magnitude - fiber * 0.1)
        
        peak_glucose = baseline + spike_magnitude
        
        return {
            'baseline': baseline,
            'peak_glucose': round(peak_glucose, 1),
            'spike_magnitude': round(spike_magnitude, 1),
            'peak_time_min': 30,
            'recovery_time_min': 90,
            'risk_level': 'high' if peak_glucose > 180 else 'medium' if peak_glucose > 140 else 'low',
        }
    
    def _predict_blood_pressure(
        self,
        user_biometrics: Dict[str, Any],
        nutrition: Dict[str, float]
    ) -> Dict[str, Any]:
        """Predict blood pressure impact from sodium."""
        baseline_sys = user_biometrics.get('bp_systolic', 120)
        baseline_dia = user_biometrics.get('bp_diastolic', 80)
        
        sodium_mg = nutrition.get('sodium', 0)
        
        # Sodium sensitivity model
        has_hypertension = 'hypertension' in [
            c.lower() for c in user_biometrics.get('medical_conditions', [])
        ]
        sensitivity = 0.8 if has_hypertension else 0.3
        
        # Effect per 100mg sodium
        sys_increase = (sodium_mg / 100) * sensitivity * 0.5
        dia_increase = (sodium_mg / 100) * sensitivity * 0.3
        
        return {
            'baseline_systolic': baseline_sys,
            'baseline_diastolic': baseline_dia,
            'predicted_systolic': round(baseline_sys + sys_increase, 1),
            'predicted_diastolic': round(baseline_dia + dia_increase, 1),
            'sodium_content': round(sodium_mg, 0),
            'risk_level': 'high' if sys_increase > 10 else 'medium' if sys_increase > 5 else 'low',
        }
    
    def _predict_cholesterol(
        self,
        user_biometrics: Dict[str, Any],
        nutrition: Dict[str, float]
    ) -> Dict[str, Any]:
        """Predict cholesterol impact from saturated fat."""
        baseline = user_biometrics.get('cholesterol_baseline', 200)
        
        fats = nutrition.get('fats', 0)
        
        # Assumption: ~30% of fats are saturated (conservative)
        sat_fat = fats * 0.3
        
        # Saturated fat impact
        impact = sat_fat * 2.5  # mg increase per g of sat fat
        
        return {
            'baseline': baseline,
            'predicted_level': round(baseline + impact, 1),
            'impact': round(impact, 1),
            'saturated_fat_estimate': round(sat_fat, 1),
            'risk_level': 'high' if impact > 20 else 'medium' if impact > 10 else 'low',
        }
    
    def _predict_energy(
        self,
        user_biometrics: Dict[str, Any],
        nutrition: Dict[str, float]
    ) -> Dict[str, Any]:
        """Predict energy levels and crash risk."""
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        carbs = nutrition.get('carbs', 0)
        sugar = nutrition.get('sugar', 0)
        
        # Balanced ratio = good sustained energy
        if calories == 0:
            energy_score = 0
        else:
            protein_ratio = (protein * 4) / calories
            
            # Good if ~20-30% protein
            protein_balance = abs(protein_ratio - 0.25)
            energy_score = max(0, 100 - (protein_balance * 200))
        
        # High sugar = crash risk
        crash_risk = min(100, sugar * 5) if sugar > 10 else 0
        
        return {
            'energy_score': round(energy_score, 0),
            'sustained_energy_min': 120 if energy_score > 70 else 60,
            'crash_risk_percent': round(crash_risk, 0),
            'sustained_level': 'high' if energy_score > 70 else 'medium' if energy_score > 40 else 'low',
        }
    
    def _predict_digestion(self, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict digestive impact."""
        ingredients = food_data.get('ingredients', [])
        nova_score = food_data.get('nova_score', 2)
        
        # Ultra-processed foods are harder to digest
        digestion_difficulty = nova_score * 20  # 20-80 scale
        
        # Check for known digestive irritants
        irritants = [ing for ing in ingredients if any(
            trigger in ing.lower()
            for trigger in ['spicy', 'caffeine', 'dairy', 'artificial', 'fiber']
        )]
        
        return {
            'digestion_difficulty': digestion_difficulty,
            'estimated_time_min': 90 + digestion_difficulty,
            'potential_irritants': irritants,
            'recommendation': 'Take with water' if digestion_difficulty > 60 else 'No special care needed',
        }
    
    def _synthesize_prediction(
        self,
        food_name: str,
        user_biometrics: Dict[str, Any],
        nutrition: Dict[str, float],
        predictions: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate human-readable impact prediction."""
        glucose_pred = predictions['glucose']
        bp_pred = predictions['blood_pressure']
        energy_pred = predictions['energy']
        
        narrative = f"""
🔮 **Biological Digital Twin Prediction for {food_name}**

**Immediate Impact (30 minutes):**
- Your glucose is predicted to spike by {glucose_pred['spike_magnitude']}mg/dL, reaching {glucose_pred['peak_glucose']}mg/dL.
  Risk Level: {glucose_pred['risk_level'].upper()}
  
- Blood pressure impact: +{bp_pred['predicted_systolic'] - bp_pred['baseline_systolic']}mmHg systolic
  Your predicted BP: {bp_pred['predicted_systolic']}/{bp_pred['predicted_diastolic']} (baseline: {bp_pred['baseline_systolic']}/{bp_pred['baseline_diastolic']})
  Risk Level: {bp_pred['risk_level'].upper()}

**Energy Profile:**
- Sustained energy score: {energy_pred['energy_score']}/100
- Sustained energy duration: ~{energy_pred['sustained_energy_min']} minutes
- Energy crash risk: {energy_pred['crash_risk_percent']}%

**Recovery Timeline:**
- Glucose returns to baseline: ~{glucose_pred['recovery_time_min']} minutes
- Peak energy level: ~{glucose_pred['peak_time_min']} minutes after consumption

**Overall Assessment:**
This product will provide {energy_pred['sustained_level']} sustained energy with a {glucose_pred['risk_level']} glucose spike risk.
"""
        return narrative.strip()
    
    def _calculate_confidence(
        self,
        user_biometrics: Dict[str, Any],
        predictions: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate confidence in predictions."""
        # Check data completeness
        required_fields = ['glucose_baseline', 'bp_systolic', 'bp_diastolic']
        provided_fields = sum(
            1 for field in required_fields
            if field in user_biometrics and user_biometrics[field]
        )
        
        completeness = provided_fields / len(required_fields)
        
        # Confidence is 0.6-0.95 based on data completeness
        confidence = 0.6 + (completeness * 0.35)
        return round(confidence, 2)
    
    def _generate_recommendation(
        self,
        predictions: Dict[str, Dict[str, Any]],
        user_biometrics: Dict[str, Any],
        food_data: Dict[str, Any]
    ) -> str:
        """Generate personalized recommendation."""
        glucose = predictions['glucose']
        energy = predictions['energy']
        
        recommendations = []
        
        if glucose['risk_level'] == 'high':
            recommendations.append("❌ High glucose spike risk. Consider eating with protein/fiber or in smaller portions.")
        elif glucose['risk_level'] == 'medium':
            recommendations.append("⚠️ Moderate glucose impact. Pair with protein to reduce spike.")
        
        if energy['crash_risk_percent'] > 50:
            recommendations.append("💡 High sugar content may cause energy crash. Plan lighter activity afterwards.")
        
        if energy['sustained_level'] == 'low':
            recommendations.append("🍎 Consider adding protein/healthy fats for sustained energy.")
        
        if not recommendations:
            recommendations.append("✅ This appears to be a well-balanced choice for your profile.")
        
        return " ".join(recommendations)


# Global instance
digital_twin = None


def get_digital_twin() -> DigitalTwinEngine:
    """Get or create global digital twin instance."""
    global digital_twin
    if digital_twin is None:
        digital_twin = DigitalTwinEngine()
    return digital_twin
