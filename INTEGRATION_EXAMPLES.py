"""
BioGuard AI - Integration Examples & Usage Patterns
Complete examples of how to use all services together
"""

import asyncio
from typing import Dict, Any
import json

# ============================================================================
# EXAMPLE 1: Complete Food Analysis Workflow
# ============================================================================

async def complete_food_analysis_example():
    """
    Complete workflow: User uploads food image, system performs full analysis
    """
    from services.live_vision import get_live_vision_service
    from services.graph_engine import get_graph_engine
    from services.digital_twin import get_digital_twin
    from database.db_manager import get_db_manager
    from models.schemas import FoodAnalysisResult, VerdictType
    import cv2
    
    print("="*70)
    print("EXAMPLE 1: Complete Food Analysis Workflow")
    print("="*70)
    
    # Step 1: Load image and perform detection
    print("\n[1/5] Loading image and performing detection...")
    vision = get_live_vision_service()
    image = cv2.imread("test_food.jpg")
    annotated_frame, detections = vision.process_frame(image)
    print(f"    ✅ Detected {len(detections)} objects")
    
    # Step 2: Simulate deep analysis (would call OpenAI Vision API)
    print("\n[2/5] Performing deep analysis...")
    food_analysis = {
        'name': 'Apple with Almonds',
        'health_score': 82,
        'nova_score': 1,
        'verdict': 'SAFE',
        'macros': {
            'protein': '5g',
            'carbs': '28g',
            'fats': '8g',
            'sodium': '2mg',
            'sugar': '19g',
            'fiber': '4g',
            'calories': 195,
        },
        'ingredients': ['apple', 'almonds', 'natural honey'],
        'clinical_verdict': 'Excellent nutritional profile',
        'warnings': [],
    }
    print(f"    ✅ Health Score: {food_analysis['health_score']}/100")
    
    # Step 3: Check for health conflicts
    print("\n[3/5] Querying knowledge graph for conflicts...")
    graph = get_graph_engine()
    user_medical_conditions = ['diabetes', 'nut_allergy']
    user_allergies = ['tree_nuts']
    
    conflicts = graph.find_hidden_conflicts(
        ingredients=food_analysis['ingredients'],
        medical_conditions=user_medical_conditions,
        allergies=user_allergies
    )
    print(f"    ⚠️  Found {len(conflicts)} potential conflicts")
    for conflict in conflicts:
        print(f"       • {conflict['ingredient'].upper()} → {conflict['health_condition']}")
        print(f"         Severity: {conflict['severity']}")
    
    # Step 4: Generate digital twin predictions
    print("\n[4/5] Generating digital twin predictions...")
    twin = get_digital_twin()
    user_biometrics = {
        'glucose_baseline': 105,  # User is diabetic
        'bp_systolic': 128,
        'bp_diastolic': 82,
        'cholesterol_baseline': 210,
        'medical_conditions': user_medical_conditions,
    }
    
    prediction = twin.predict_impact(user_biometrics, food_analysis)
    print(f"    🔮 Impact Prediction:")
    print(f"       {prediction.predicted_impact[:200]}...")
    print(f"    Confidence: {prediction.confidence:.0%}")
    
    # Step 5: Save to database
    print("\n[5/5] Saving analysis to database...")
    db = get_db_manager()
    user_id = 'user_test_001'
    
    analysis_result = {
        **food_analysis,
        'conflicts': [c for c in conflicts],
        'prediction': prediction.dict(),
    }
    
    if db.save_food_analysis(user_id, analysis_result):
        print(f"    ✅ Analysis saved for user {user_id}")
    
    # Retrieve history
    history = db.get_user_history(user_id)
    print(f"    📊 User analysis history: {len(history)} items")
    
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE")
    print("="*70)


# ============================================================================
# EXAMPLE 2: Real-Time AR Processing Loop
# ============================================================================

def realtime_ar_processing_example():
    """
    Continuous AR processing with cached detections for smooth UX
    """
    from services.live_vision import get_live_vision_service
    import cv2
    import time
    
    print("="*70)
    print("EXAMPLE 2: Real-Time AR Processing Loop")
    print("="*70)
    
    vision = get_live_vision_service()
    
    # Simulate 30 frames
    print("\nSimulating 30 FPS video stream with 1 FPS detection...\n")
    
    for frame_num in range(30):
        # Mock frame (would come from camera)
        frame = cv2.imread("test_food.jpg")
        if frame is None:
            print(f"[Frame {frame_num}] Mock frame")
            continue
        
        start_time = time.time()
        annotated, detections = vision.process_frame(frame)
        elapsed = time.time() - start_time
        
        if frame_num % 10 == 0:  # Print every 10 frames
            print(f"[Frame {frame_num}] Detections: {len(detections)} | "
                  f"Processing: {elapsed*1000:.1f}ms")
    
    # Print stats
    stats = vision.get_service_stats()
    print(f"\n📊 Service Stats:")
    print(f"   Total Frames Processed: {stats['frames_processed']}")
    print(f"   Cached Detections: {stats['cached_detections']}")
    print(f"   Detection FPS: {stats['detection_fps']}")
    
    print("\n" + "="*70)
    print("✅ AR LOOP COMPLETE")
    print("="*70)


# ============================================================================
# EXAMPLE 3: Multi-User Scenario with Federated Learning
# ============================================================================

async def federated_learning_scenario():
    """
    Simulate multiple users training models locally
    """
    from services.auth_privacy import get_auth_manager
    from database.db_manager import get_db_manager
    
    print("="*70)
    print("EXAMPLE 3: Federated Learning Multi-User Scenario")
    print("="*70)
    
    auth = get_auth_manager()
    db = get_db_manager()
    
    # Simulate 3 users
    users = [
        {'user_id': 'alice', 'name': 'Alice', 'age': 28},
        {'user_id': 'bob', 'name': 'Bob', 'age': 45},
        {'user_id': 'charlie', 'name': 'Charlie', 'age': 62},
    ]
    
    print(f"\nTraining models locally for {len(users)} users...\n")
    
    initial_weights = {
        'layer_1': 0.5,
        'layer_2': 0.3,
        'layer_3': 0.2,
    }
    
    for user in users:
        print(f"[{user['name']}] Starting local training...")
        
        # Simulate local data
        user_data_batch = [{'food': 'apple'}, {'food': 'bread'}, {'food': 'salad'}]
        
        # Perform local update
        updated_weights, accuracy = await auth.local_model_update(
            client_id=user['user_id'],
            user_data_batch=user_data_batch,
            current_weights=initial_weights
        )
        
        print(f"[{user['name']}] Local training complete!")
        print(f"    Accuracy: {accuracy:.3f}")
        print(f"    Updated weights saved to database")
        print()
    
    print("="*70)
    print("✅ FEDERATED LEARNING SCENARIO COMPLETE")
    print("   Next step: Server aggregates all client updates with FedAvg")
    print("="*70)


# ============================================================================
# EXAMPLE 4: Knowledge Graph Conflict Detection
# ============================================================================

def knowledge_graph_example():
    """
    Advanced conflict detection using graph relationships
    """
    from services.graph_engine import get_graph_engine
    
    print("="*70)
    print("EXAMPLE 4: Knowledge Graph Conflict Detection")
    print("="*70)
    
    graph = get_graph_engine()
    
    # Test user with hypertension and diabetes
    print("\nUser Profile:")
    print("  Medical Conditions: Hypertension, Diabetes")
    print("  Allergies: Peanuts, Shellfish")
    print()
    
    # Analyze a processed food
    print("Analyzing: 'Instant Ramen Noodles'")
    print("Ingredients: [wheat flour, salt, MSG, trans fat, egg powder]")
    print()
    
    conflicts = graph.find_hidden_conflicts(
        ingredients=['wheat flour', 'salt', 'MSG', 'trans fat', 'egg powder'],
        medical_conditions=['hypertension', 'diabetes'],
        allergies=['peanuts', 'shellfish']
    )
    
    print(f"Found {len(conflicts)} conflicts:\n")
    
    # Group by severity
    by_severity = {}
    for conflict in conflicts:
        severity = conflict['severity']
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(conflict)
    
    for severity in ['high', 'medium', 'low']:
        if severity in by_severity:
            print(f"{severity.upper()} Severity ({len(by_severity[severity])}):")
            for conflict in by_severity[severity]:
                print(f"  • {conflict['ingredient'].upper()}")
                print(f"    → {conflict['health_condition']}")
                print(f"    Relationship: {conflict['relationship']}")
                if 'path' in conflict:
                    print(f"    Path: {' → '.join(conflict['path'])}")
            print()
    
    # Show graph metrics
    metrics = graph.get_graph_metrics()
    print("\nGraph Statistics:")
    print(f"  Total Nodes: {metrics['total_nodes']}")
    print(f"  Total Edges: {metrics['total_edges']}")
    print(f"  Graph Density: {metrics['density']:.3f}")
    print(f"  Average Node Degree: {metrics['avg_degree']:.1f}")
    
    print("\n" + "="*70)
    print("✅ GRAPH ANALYSIS COMPLETE")
    print("="*70)


# ============================================================================
# EXAMPLE 5: Digital Twin Impact Simulation
# ============================================================================

def digital_twin_example():
    """
    Detailed biological impact prediction
    """
    from services.digital_twin import get_digital_twin
    
    print("="*70)
    print("EXAMPLE 5: Digital Twin Impact Simulation")
    print("="*70)
    
    twin = get_digital_twin()
    
    # User profile
    user = {
        'name': 'John',
        'age': 45,
        'medical_conditions': ['diabetes', 'hypertension'],
        'glucose_baseline': 115,
        'bp_systolic': 140,
        'bp_diastolic': 90,
        'cholesterol_baseline': 245,
    }
    
    # Food: Sugary cereal
    food = {
        'name': 'Fruit Loops Cereal with Whole Milk',
        'health_score': 35,
        'nova_score': 4,
        'macros': {
            'calories': 380,
            'protein': '8g',
            'carbs': '48g',
            'fats': '15g',
            'sodium': '280mg',
            'sugar': '16g',
            'fiber': '1g',
        },
        'ingredients': ['corn flour', 'sugar', 'vegetable oil', 'salt', 'colors'],
    }
    
    print(f"\nUser: {user['name']}")
    print(f"  Glucose Baseline: {user['glucose_baseline']} mg/dL")
    print(f"  BP: {user['bp_systolic']}/{user['bp_diastolic']}")
    print(f"  Medical: {', '.join(user['medical_conditions'])}")
    
    print(f"\nFood: {food['name']}")
    print(f"  Calories: {food['macros'].get('calories', 0)}")
    print(f"  Carbs: {food['macros'].get('carbs', '0g')}")
    print(f"  Sugar: {food['macros'].get('sugar', '0g')}")
    print()
    
    # Get prediction
    prediction = twin.predict_impact(user, food)
    
    print("="*70)
    print("BIOLOGICAL TWIN PREDICTION")
    print("="*70)
    print(prediction.predicted_impact)
    
    print("\n" + "="*70)
    print("DETAILED METRICS")
    print("="*70)
    
    for metric_name, metric_data in prediction.metrics.items():
        print(f"\n{metric_name.upper()}:")
        for key, value in metric_data.items():
            print(f"  • {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ DIGITAL TWIN PREDICTION COMPLETE")
    print("="*70)


# ============================================================================
# EXAMPLE 6: Privacy & Authentication Workflow
# ============================================================================

def privacy_workflow_example():
    """
    Complete privacy and security demonstration
    """
    from services.auth_privacy import get_auth_manager
    
    print("="*70)
    print("EXAMPLE 6: Privacy & Authentication Workflow")
    print("="*70)
    
    auth = get_auth_manager()
    
    user_id = 'user_privacy_001'
    user_data = {
        'user_id': user_id,
        'name': 'Private User',
        'age': 35,
        'medical_conditions': ['high cholesterol'],
    }
    
    print("\n[1] Generate JWT Token")
    token = auth.generate_jwt_token(user_id, user_data)
    print(f"    Token: {token[:50]}...")
    
    print("\n[2] Verify Token")
    verified = auth.verify_jwt_token(token)
    if verified:
        print(f"    ✅ Token valid for user: {verified['user_name']}")
    
    print("\n[3] Setup Two-Factor Authentication")
    secret = auth.generate_2fa_secret(user_id)
    print(f"    Secret generated (length: {len(secret)})")
    
    print("\n[4] Get 2FA QR Code")
    qr_uri = auth.get_2fa_qr_code(user_id, 'user@example.com')
    print(f"    QR URI: {qr_uri[:60]}...")
    
    print("\n[5] Encrypt Sensitive Data")
    medical_info = "Patient has Type 2 Diabetes, on Metformin"
    encrypted = auth.encrypt_data(medical_info)
    print(f"    Original: {medical_info}")
    print(f"    Encrypted: {encrypted[:40]}...")
    
    print("\n[6] Decrypt Data")
    decrypted = auth.decrypt_data(encrypted)
    print(f"    Decrypted: {decrypted}")
    
    print("\n[7] Privacy Report")
    report = auth.get_privacy_report(user_id)
    print("    Privacy Report:")
    for key, value in report.items():
        if key != 'user_id':
            print(f"      {key}: {value}")
    
    print("\n[8] Revoke Token (Logout)")
    auth.revoke_token(user_id)
    print(f"    ✅ Token revoked for user: {user_id}")
    
    print("\n" + "="*70)
    print("✅ PRIVACY WORKFLOW COMPLETE")
    print("="*70)


# ============================================================================
# MAIN: Run all examples
# ============================================================================

async def main():
    """Run all examples"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "BIOGUARD AI - INTEGRATION EXAMPLES" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    # Run examples
    await complete_food_analysis_example()
    print("\n\n")
    
    realtime_ar_processing_example()
    print("\n\n")
    
    await federated_learning_scenario()
    print("\n\n")
    
    knowledge_graph_example()
    print("\n\n")
    
    digital_twin_example()
    print("\n\n")
    
    privacy_workflow_example()
    
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "✅ ALL INTEGRATION EXAMPLES COMPLETED SUCCESSFULLY" + " "*8 + "║")
    print("╚" + "="*68 + "╝")
    print()


if __name__ == "__main__":
    asyncio.run(main())
