"""
Authentication Module
Supabase integration for user authentication
"""
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Tuple

from src.config import SUPABASE_URL, SUPABASE_KEY


def initialize_supabase() -> Optional[Client]:
    """
    Initialize Supabase client
    
    Returns:
        Supabase client or None if credentials missing
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None


def sign_up(email: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Tuple of (success, message)
    """
    client = initialize_supabase()
    if not client:
        return False, "Authentication service not configured"
    
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return True, "Account created! Please check your email to confirm your account."
        else:
            return False, "Sign up failed. Please try again."
            
    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower():
            return False, "This email is already registered. Please sign in."
        return False, f"Sign up error: {error_message}"


def sign_in(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Sign in existing user
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Tuple of (success, message, user_data)
    """
    client = initialize_supabase()
    if not client:
        return False, "Authentication service not configured", None
    
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            user_data = {
                "id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token
            }
            return True, "Signed in successfully!", user_data
        else:
            return False, "Invalid credentials", None
            
    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower():
            return False, "Invalid email or password", None
        return False, f"Sign in error: {error_message}", None


def sign_out() -> Tuple[bool, str]:
    """
    Sign out current user
    
    Returns:
        Tuple of (success, message)
    """
    client = initialize_supabase()
    if not client:
        return False, "Authentication service not configured"
    
    try:
        client.auth.sign_out()
        return True, "Signed out successfully"
    except Exception as e:
        return False, f"Sign out error: {e}"


def get_current_user() -> Optional[dict]:
    """
    Get current user from session state
    
    Returns:
        User data dict or None
    """
    return st.session_state.get("user", None)


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return get_current_user() is not None


def require_auth():
    """Decorator-like function to require authentication"""
    if not is_authenticated():
        st.warning("Please sign in to continue")
        st.stop()
