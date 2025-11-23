from features.agent.types.signatures import ConversationSig
from dspy import History
import dspy
from litellm import RateLimitError
import logging
from features.common.types.exceptions import ProviderException, RateLimitException

logger = logging.getLogger(__name__)

class AgentRepository:

    def __init__(self):
        self.history = History(messages=[])

    def get_response(self, prompt: str) -> tuple[str, bool]:
        """Calls the DSPy module to get a response."""
        try:
            logger.info(f"Getting response for prompt: {prompt}")
            result = dspy.Predict(ConversationSig)(user_utterance=prompt, conversation_history=self.history)
            ai_response = result.assistant_utterance
            is_directed_at_agent = result.is_directed_at_agent

            self.history.messages.append({"user_utterance": prompt, "assistant_utterance": ai_response})

            return ai_response, is_directed_at_agent
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                logger.error(f"Error getting response: {e}")
                raise RateLimitException(message=str(e))
            
            raise ProviderException(message=str(e))