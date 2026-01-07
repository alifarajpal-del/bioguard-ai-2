"""
OAuth Authentication Providers (Google & Apple Sign-In).
Handles OAuth 2.0 flows for social authentication.
"""

import jwt
import time
import json
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app_config.settings import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    APPLE_CLIENT_ID, APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY, APPLE_REDIRECT_URI
)


class OAuthProvider:
    """Base OAuth provider class."""
    
    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL."""
        raise NotImplementedError
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        raise NotImplementedError
    
    def get_user_info(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get user information from provider."""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider."""
    
    AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"
    SCOPES = ["openid", "email", "profile"]
    
    def __init__(self):
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.redirect_uri = GOOGLE_REDIRECT_URI
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL string
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        
        if state:
            params["state"] = state
        
        return f"{self.AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Token response dict with access_token, id_token, etc.
        """
        try:
            payload = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            }
            
            response = requests.post(self.TOKEN_ENDPOINT, data=payload, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Google token exchange error: {e}")
            return None
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode Google ID token (JWT).
        
        Args:
            id_token: JWT ID token from Google
            
        Returns:
            Decoded token payload
        """
        try:
            # Get Google's public keys
            keys_response = requests.get(
                "https://www.googleapis.com/oauth2/v3/certs",
                timeout=5
            )
            keys_response.raise_for_status()
            jwks = keys_response.json()
            
            # Decode without verification first to get header
            unverified_header = jwt.get_unverified_header(id_token)
            
            # Find matching key
            key = None
            for jwk in jwks.get("keys", []):
                if jwk["kid"] == unverified_header["kid"]:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                print("❌ No matching key found for ID token")
                return None
            
            # Verify and decode
            payload = jwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://accounts.google.com"
            )
            
            return payload
            
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid Google ID token: {e}")
            return None
        except Exception as e:
            print(f"❌ ID token verification error: {e}")
            return None
    
    def get_user_info(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get user information from Google.
        
        Args:
            token_data: Token response containing id_token
            
        Returns:
            User info dict with email, name, picture, etc.
        """
        try:
            # First try to decode ID token (faster)
            if "id_token" in token_data:
                user_info = self.verify_id_token(token_data["id_token"])
                if user_info:
                    return {
                        "user_id": user_info.get("sub"),
                        "email": user_info.get("email"),
                        "name": user_info.get("name"),
                        "picture": user_info.get("picture"),
                        "email_verified": user_info.get("email_verified", False),
                        "provider": "google",
                    }
            
            # Fallback: use access token to fetch user info
            if "access_token" in token_data:
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                response = requests.get(self.USERINFO_ENDPOINT, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                return {
                    "user_id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "picture": data.get("picture"),
                    "email_verified": data.get("verified_email", False),
                    "provider": "google",
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get Google user info: {e}")
            return None


class AppleOAuthProvider(OAuthProvider):
    """Apple Sign In provider."""
    
    AUTHORIZATION_ENDPOINT = "https://appleid.apple.com/auth/authorize"
    TOKEN_ENDPOINT = "https://appleid.apple.com/auth/token"
    SCOPES = ["name", "email"]
    
    def __init__(self):
        self.client_id = APPLE_CLIENT_ID
        self.team_id = APPLE_TEAM_ID
        self.key_id = APPLE_KEY_ID
        self.private_key = APPLE_PRIVATE_KEY
        self.redirect_uri = APPLE_REDIRECT_URI
    
    def _generate_client_secret(self) -> str:
        """
        Generate client_secret JWT for Apple.
        Apple requires a JWT signed with your private key.
        """
        now = int(time.time())
        
        headers = {
            "alg": "ES256",
            "kid": self.key_id,
        }
        
        payload = {
            "iss": self.team_id,
            "iat": now,
            "exp": now + 86400 * 180,  # 6 months
            "aud": "https://appleid.apple.com",
            "sub": self.client_id,
        }
        
        # Sign with ES256 (ECDSA with SHA-256)
        client_secret = jwt.encode(
            payload,
            self.private_key,
            algorithm="ES256",
            headers=headers
        )
        
        return client_secret
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Apple Sign In authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL string
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "response_mode": "form_post",  # Apple recommends form_post
            "scope": " ".join(self.SCOPES),
        }
        
        if state:
            params["state"] = state
        
        return f"{self.AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Token response dict with access_token, id_token, etc.
        """
        try:
            client_secret = self._generate_client_secret()
            
            payload = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            }
            
            response = requests.post(self.TOKEN_ENDPOINT, data=payload, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Apple token exchange error: {e}")
            return None
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode Apple ID token (JWT).
        
        Args:
            id_token: JWT ID token from Apple
            
        Returns:
            Decoded token payload
        """
        try:
            # Get Apple's public keys
            keys_response = requests.get(
                "https://appleid.apple.com/auth/keys",
                timeout=5
            )
            keys_response.raise_for_status()
            jwks = keys_response.json()
            
            # Decode without verification first to get header
            unverified_header = jwt.get_unverified_header(id_token)
            
            # Find matching key
            key = None
            for jwk in jwks.get("keys", []):
                if jwk["kid"] == unverified_header["kid"]:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                    break
            
            if not key:
                print("❌ No matching key found for Apple ID token")
                return None
            
            # Verify and decode
            payload = jwt.decode(
                id_token,
                key=key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer="https://appleid.apple.com"
            )
            
            return payload
            
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid Apple ID token: {e}")
            return None
        except Exception as e:
            print(f"❌ Apple ID token verification error: {e}")
            return None
    
    def get_user_info(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get user information from Apple ID token.
        
        Note: Apple doesn't provide a userinfo endpoint.
        All user data is in the ID token.
        
        Args:
            token_data: Token response containing id_token
            
        Returns:
            User info dict with email, name (if provided), etc.
        """
        try:
            if "id_token" not in token_data:
                print("❌ No ID token in Apple response")
                return None
            
            user_info = self.verify_id_token(token_data["id_token"])
            if not user_info:
                return None
            
            # Apple's ID token contains minimal info
            result = {
                "user_id": user_info.get("sub"),
                "email": user_info.get("email"),
                "email_verified": user_info.get("email_verified", "false") == "true",
                "provider": "apple",
            }
            
            # Name is only provided on first authorization
            # and comes in the POST body, not the token
            # You need to handle it in the callback handler
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to get Apple user info: {e}")
            return None


# ============== Factory ==============

def get_oauth_provider(provider_name: str) -> Optional[OAuthProvider]:
    """
    Get OAuth provider instance by name.
    
    Args:
        provider_name: "google" or "apple"
        
    Returns:
        OAuth provider instance
    """
    providers = {
        "google": GoogleOAuthProvider,
        "apple": AppleOAuthProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        print(f"❌ Unknown OAuth provider: {provider_name}")
        return None
    
    try:
        return provider_class()
    except Exception as e:
        print(f"❌ Failed to initialize {provider_name} provider: {e}")
        return None
