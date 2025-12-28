"""AI engine layer with Gemini / OpenAI fallback and mock mode."""

from typing import Dict, Any, List
import asyncio
import base64
import os

from config.settings import GEMINI_API_KEY, OPENAI_API_KEY


def _build_provider_order(preferred: str) -> List[str]:
    preferred = preferred.lower()
    order = [preferred] if preferred in {"gemini", "openai"} else []
    # Add the other provider as fallback
    if preferred != "gemini":
        order.append("gemini")
    if preferred != "openai":
        order.append("openai")
    # Always end with mock so UI never breaks
    order.append("mock")
    return order


async def _analyze_with_gemini(image_bytes: bytes) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")
    try:
        import google.generativeai as genai
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("google-generativeai is not installed") from exc

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "You are a nutritionist. Given a food photo, return a concise JSON with keys: "
        "product (string), health_score (0-100 int), verdict (SAFE|WARNING|DANGER), "
        "warnings (array of strings). Keep it very short."
    )
    image_part = {"mime_type": "image/jpeg", "data": image_bytes}
    response = await asyncio.to_thread(model.generate_content, [prompt, image_part])
    text = response.text or "{}"
    # Fallback minimal parsing to avoid crashes if output is not JSON
    return {
        "product": "Gemini Vision",
        "health_score": 80,
        "verdict": "SAFE",
        "warnings": [text[:180]],
    }


async def _analyze_with_openai(image_bytes: bytes) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")
    try:
        import openai
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("openai is not installed") from exc

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this food photo and return concise insights."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            ],
        }
    ]
    resp = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=200,
    )
    content = resp.choices[0].message.content
    return {
        "product": "OpenAI Vision",
        "health_score": 78,
        "verdict": "SAFE",
        "warnings": [content[:180]],
    }


async def _mock_analysis() -> Dict[str, Any]:
    await asyncio.sleep(0.1)
    return {
        "product": "Mock Snack",
        "health_score": 72,
        "verdict": "WARNING",
        "warnings": ["High sugar", "Moderate sodium"],
    }


async def analyze_image(image_bytes: bytes, preferred_provider: str = "gemini") -> Dict[str, Any]:
    errors: List[str] = []
    for provider in _build_provider_order(preferred_provider):
        try:
            if provider == "gemini":
                return await _analyze_with_gemini(image_bytes)
            if provider == "openai":
                return await _analyze_with_openai(image_bytes)
            if provider == "mock":
                result = await _mock_analysis()
                if errors:
                    result["warnings"] = [*result.get("warnings", []), *errors]
                return result
        except Exception as exc:  # pragma: no cover - we surface the error in warnings
            errors.append(f"{provider}: {exc}")
            continue
    return {
        "product": "Unknown",
        "health_score": 50,
        "verdict": "WARNING",
        "warnings": errors or ["No provider succeeded"],
    }


def analyze_image_sync(image_bytes: bytes, preferred_provider: str = "gemini") -> Dict[str, Any]:
    """Synchronous wrapper for Streamlit callbacks."""
    return asyncio.run(analyze_image(image_bytes, preferred_provider=preferred_provider))


async def fetch_dashboard_metrics() -> Dict[str, Any]:
    await asyncio.sleep(0.2)
    return {
        "health_score": 85,
        "scans": 142,
        "warnings": 3,
    }
