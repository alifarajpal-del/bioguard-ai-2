"""Helper functions for camera view to reduce complexity."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import streamlit as st

from utils.i18n import t


def init_camera_session_state() -> None:
    """Initialize all camera-related session state variables."""
    if "scan_status" not in st.session_state:
        st.session_state.scan_status = "searching"
    if "last_barcode" not in st.session_state:
        st.session_state.last_barcode = None
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "last_nutrition_snapshot" not in st.session_state:
        st.session_state.last_nutrition_snapshot = None


def get_status_message(status: str, messages: Dict[str, str]) -> str:
    """Get status message based on scan status."""
    return {
        "searching": messages["searching"],
        "detected": messages["detected"],
        "analyzing": messages["analyzing"],
        "complete": messages["complete"],
    }.get(status, messages["searching"])


def extract_confidence_info(confidence: float) -> tuple[str, str]:
    """Extract confidence label and color."""
    if confidence >= 0.8:
        return "High", "green"
    elif confidence >= 0.6:
        return "Medium", "orange"
    else:
        return "Low", "red"


def get_score_color(score: int) -> str:
    """Get color based on health score."""
    if score > 70:
        return "#10b981"
    elif score > 40:
        return "#f59e0b"
    else:
        return "#ef4444"


def normalize_nutrition_data(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize nutrition snapshot to flat dict structure."""
    raw = snapshot.get("raw") or snapshot
    if isinstance(raw, dict) and "nutrients" in raw:
        return raw["nutrients"]
    return raw


def prepare_nutrition_result(
    snapshot: Dict[str, Any], result: Dict[str, Any]
) -> Dict[str, Any]:
    """Prepare nutrition data for result display."""
    result["data_source"] = snapshot.get("source")
    result["nutrients"] = normalize_nutrition_data(snapshot)

    raw = snapshot.get("raw") or snapshot
    if not result.get("product") and isinstance(raw, dict):
        label = raw.get("product_name")
        if label:
            result["product"] = label

    return result


def save_analysis_to_history(result: Dict[str, Any], user_id: str) -> None:
    """Save analysis result to session history and database."""
    from database.db_manager import get_db_manager
    from utils.logging_setup import get_logger, log_user_action

    logger = get_logger(__name__)

    st.session_state.analysis_history.append(result)
    log_user_action(
        logger,
        "analysis_complete",
        {
            "score": result.get("health_score", 0),
            "product": result.get("product", "unknown"),
        },
    )

    db = get_db_manager()
    db.save_food_analysis(user_id, result)


def sync_health_data(result: Dict[str, Any], user_id: str) -> None:
    """Sync nutrition data to health services if enabled."""
    if not st.session_state.get("health_sync_enabled"):
        return

    if not result.get("nutrients"):
        return

    from services.health_sync import get_health_sync_service

    health_sync = get_health_sync_service()
    health_sync.sync_nutrition_entry(
        user_id=user_id,
        product=result.get("product", "Unknown"),
        nutrients=result.get("nutrients", {}),
        source=result.get("data_source"),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def render_metadata_badges(result: Dict[str, Any], confidence: float) -> None:
    """Render confidence and source badges."""
    from ui_components.ui_kit import confidence_badge, source_badge

    badges_html = confidence_badge(confidence, t("confidence"))
    if result.get("data_source"):
        badges_html += " " + source_badge(result["data_source"])
    st.markdown(
        f'<div style="margin: 8px 0;">{badges_html}</div>', unsafe_allow_html=True
    )


def render_ingredients_section(result: Dict[str, Any]) -> None:
    """Render ingredients section if available."""
    if result.get("ingredients"):
        with st.expander("📝 Ingredients"):
            st.write(", ".join(result.get("ingredients", [])))


def render_alternatives_section(
    score: int, result: Dict[str, Any], messages: Dict[str, str]
) -> None:
    """Render healthier alternatives section for low scores."""
    if score >= 70:
        return

    with st.expander(messages["alternatives"]):
        try:
            from database.db_manager import get_db_manager
            from services.recommendations import get_recommendations_service

            recommendations_service = get_recommendations_service()
            product_name = result.get("product", "Unknown")
            category = result.get("category")

            # Get user profile for personalized recommendations
            username = st.session_state.get("username")
            user_profile = {}
            if username:
                db = get_db_manager()
                user_data = db.get_user_profile(username)
                if user_data:
                    user_profile = {
                        "allergies": user_data.get("allergies", []),
                        "health_conditions": user_data.get("health_conditions", []),
                    }

            # Get alternatives
            if user_profile:
                alternatives = recommendations_service.get_healthier_alternatives(
                    product_name=product_name,
                    current_score=score,
                    category=category,
                    user_profile=user_profile,
                )
            else:
                alternatives = recommendations_service.get_healthier_alternatives(
                    product_name=product_name, current_score=score, category=category
                )

            if alternatives and len(alternatives) > 0:
                st.markdown("### 🌟 Healthier Options:")
                for alt in alternatives[:3]:
                    st.markdown(
                        f"**{alt.get('name', 'Alternative')}** - "
                        f"Score: {alt.get('score', 'N/A')}/100"
                    )
                    if alt.get("reason"):
                        st.caption(alt["reason"])
            else:
                st.info(messages.get("no_alternatives", "No alternatives found."))

        except Exception as e:
            st.warning(f"Could not fetch alternatives: {str(e)}")
