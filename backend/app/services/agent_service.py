#!/usr/bin/env python3

from typing import Optional, Tuple
from app.repositories.agent_repository import AgentRepository

class AgentService:
    """High-level AI agent orchestration"""
    
    def __init__(self, repo: AgentRepository):
        self.repo = repo
    
    def process_user_input(self, connection_id: str, text: str) -> tuple[Optional[str], Optional[bool]]:
        """Process user input and generate response if directed at agent"""
        try:
            # Generate response
            response, is_directed_at_agent = self.repo.generate_response(connection_id, text)

            print(f"🤖 Agent response: {response} is_directed_at_agent: {is_directed_at_agent}")
            return response, is_directed_at_agent
        except Exception as e:
            print(f"❌ Agent processing error: {e}")
            return None, None
    
    def cleanup_connection(self, connection_id: str) -> None:
        """Clean up agent state for a connection"""
        self.repo.cleanup_connection(connection_id) 