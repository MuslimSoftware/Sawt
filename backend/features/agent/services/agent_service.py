from features.agent.repositories.agent_repository import AgentRepository

class AgentService:
    
    def __init__(self):
        self.repository = AgentRepository()

    def get_response(self, prompt: str) -> tuple[str, bool]:
        """Gets a response from the agent."""
        return self.repository.get_response(prompt)