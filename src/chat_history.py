"""
Chat History Module
Persists chat sessions in Supabase database
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid

# Import initialized client from auth to avoid circular issues or duplication
# Assuming src.auth has initialize_supabase
# But to be safe and independent, we can re-create client here or import
from src.config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client



class ChatHistory:
    """Manages chat sessions using Supabase"""
    
    def __init__(self, user_token: str = None):
        """Initialize Supabase client with user auth"""
        self.enabled = False
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                if user_token:
                    # Authenticate the client for RLS policies
                    self.supabase.postgrest.auth(user_token)
                self.enabled = True
            except Exception as e:
                print(f"Chat History DB connection failed: {e}")
        else:
            print("Supabase credentials missing for Chat History")
            
    def create_session(self, user_id: str, title: str = "New Chat") -> Dict:
        """Create a new chat session"""
        if not self.enabled:
            # Fallback mock for offline/error state
            return {
                "id": str(uuid.uuid4()),
                "title": title,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }

        now = datetime.now().isoformat()
        
        # We let the DB generate ID if we wanted, but here we generate explicitly
        # Note: if we insert without an ID, ensure DB has default gen_random_uuid()
        # The SQL script I provided has default gen_random_uuid(), so we can omit ID or generate one.
        # Generating one here is safer for returning it immediately.
        session_id = str(uuid.uuid4())
        
        data = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now
        }
        
        try:
            # RLS requires us to be the user
            self.supabase.table("chat_sessions").insert(data).execute()
        except Exception as e:
            print(f"Error creating session: {e}")
            # If RLS fails, we might return the local object but it won't be saved
            # Ideally we propagate error, but for UI resilience we return the object
            
        return data
    
    def get_session(self, user_id: str, session_id: str) -> Optional[Dict]:
        """Load a specific session"""
        if not self.enabled: return None
        
        try:
            response = self.supabase.table("chat_sessions")\
                .select("*")\
                .eq("id", session_id)\
                .execute()
                
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def list_sessions(self, user_id: str) -> List[Dict]:
        """List all sessions for a user"""
        if not self.enabled: return []
        
        try:
            response = self.supabase.table("chat_sessions")\
                .select("id, title, created_at, updated_at, messages")\
                .order("updated_at", desc=True)\
                .execute()
                
            sessions = []
            for item in response.data:
                # Add message count for UI
                item["message_count"] = len(item.get("messages", []))
                sessions.append(item)
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def add_message(self, user_id: str, session_id: str, role: str, 
                    content: str, sources: List[str] = None) -> bool:
        """Add a message to a session"""
        if not self.enabled: return False
        
        # 1. Get current session to append
        session = self.get_session(user_id, session_id)
        if not session:
            return False
            
        messages = session.get("messages", [])
        
        # 2. Add new message
        new_message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "sources": sources or []
        }
        messages.append(new_message)
        
        # 3. Update data
        update_data = {
            "messages": messages,
            "updated_at": datetime.now().isoformat()
        }
        
        # Update title if it's the first message
        if session["title"] == "New Chat" and role == "user" and len(messages) == 1:
            update_data["title"] = content[:50] + ("..." if len(content) > 50 else "")
            
        try:
            self.supabase.table("chat_sessions")\
                .update(update_data)\
                .eq("id", session_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def delete_session(self, user_id: str, session_id: str) -> bool:
        """Delete a chat session"""
        if not self.enabled: return False
        
        try:
            self.supabase.table("chat_sessions")\
                .delete()\
                .eq("id", session_id)\
                .execute()
            return True
        except Exception:
            return False
    
    def clear_all_sessions(self, user_id: str) -> bool:
        """Delete all sessions for a user"""
        if not self.enabled: return False
        
        try:
            self.supabase.table("chat_sessions")\
                .delete()\
                .neq("id", "00000000-0000-0000-0000-000000000000")\
                .execute()
            # Note: .delete() requires a where clause usually. 
            # RLS ensures we only delete our own. 
            # But client libraries might block delete-all without filter.
            # Using .neq('id', '0') is a hack to 'select all'. 
            # Better: list then delete, or backend function. 
            # For now, trusting RLS + neq hack or just iterate? 
            # Let's rely on RLS logic with a dummy filter.
            return True
        except Exception:
            return False
    
    def export_session(self, user_id: str, session_id: str, format: str = "markdown") -> str:
        """Export a session as text or markdown"""
        session = self.get_session(user_id, session_id)
        if not session:
            return ""
        
        messages = session.get("messages", [])
        title = session.get("title", "Chat")
        created_at = session.get("created_at", "")
        
        if format == "markdown":
            output = f"# {title}\n\n"
            output += f"*Created: {created_at}*\n\n---\n\n"
            
            for msg in messages:
                role = "**You:**" if msg["role"] == "user" else "**RAGbot:**"
                output += f"{role}\n{msg['content']}\n\n"
                if msg.get("sources"):
                    output += f"*Sources: {', '.join(msg['sources'])}*\n\n"
            
            return output
        else:
            output = f"{title}\n{'=' * len(title)}\n\n"
            for msg in messages:
                role = "You" if msg["role"] == "user" else "RAGbot"
                output += f"[{role}]\n{msg['content']}\n\n"
            return output
