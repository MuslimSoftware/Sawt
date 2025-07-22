from features.agent.types.signatures import ConversationSig
from dspy import History
import dspy

class AgentRepository:

    def __init__(self):
        self.history = History(messages=[])

    def get_response(self, prompt: str) -> tuple[str, bool]:
        """Calls the DSPy module to get a response."""
        result = dspy.Predict(ConversationSig)(user_utterance=prompt, conversation_history=self.history)
        ai_response = result.assistant_utterance
        is_directed_at_agent = result.is_directed_at_agent

        self.history.messages.append({"user_utterance": prompt, "assistant_utterance": ai_response})

        return ai_response, is_directed_at_agent