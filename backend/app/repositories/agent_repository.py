#!/usr/bin/env python3

import dspy
import warnings
from typing import Dict
from dspy import History
from configs.ai_config import AIConfig

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class ConversationSig(dspy.Signature):
    """
    You are a helpful voice assistant that can answer general questions conversationally.
    You respond with plain conversational text, no markdown or code or any special characters.
    Your responses should be in clear conversational style, so that it can be converted to speech without problems.
    Also you should determine if the user is speaking to you or whether the transciption is non-sensical or doesnt make any sense. in those cases you should respond with [Not directed at agent]
    """
    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    conversation_history: History = dspy.InputField(desc="Previous turns of the voice conversation.")
    assistant_utterance: str = dspy.OutputField(desc="How the assistant should speak back – plain conversational text, no markdown or code or special characters. Respond in short sentences and paragraphs. Maximum 3-4 sentences.")
    is_directed_at_agent: bool = dspy.OutputField(desc="Whether the user's utterance is directed at the agent. If the user is clearly speaking to you and the transcription is not non-sensical or doesnt make any sense, then this should be True. If the user is speaking to you and the transcription is non-sensical or doesnt make any sense, then this should be False.")

class AgentRepository:
    """Low-level AI agent management with per-connection conversation history"""
    
    _instance = None
    _dspy_configured = False
    
    def __new__(cls, config: AIConfig):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
            cls._instance.conversations: Dict[str, History] = {}
        return cls._instance
    
    def _configure_dspy(self):
        """Configure DSPy once"""
        if not self._dspy_configured:
            self._configure_dspy_internal()
    
    def _configure_dspy_internal(self):
        """Internal DSPy configuration"""
        print("Initializing DSPy with memory support...")
        dspy.configure(
            lm=dspy.LM(
                model=self.config.model,
                api_key=self.config.api_key,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
        )
        print("✅ DSPy ready!")
        self._dspy_configured = True
    
    @classmethod
    def configure_dspy_globally(cls, config: AIConfig):
        """Configure DSPy globally at server startup"""
        if cls._instance is None:
            cls._instance = cls(config)
        cls._instance._configure_dspy_internal()
    
    def get_conversation_history(self, connection_id: str) -> History:
        """Get or create conversation history for a connection"""
        if connection_id not in self.conversations:
            self.conversations[connection_id] = History(messages=[])
        return self.conversations[connection_id]
    
    def generate_response(self, connection_id: str, user_input: str) -> str:
        """Generate AI response using conversation history"""
        self._configure_dspy()
        
        history = self.get_conversation_history(connection_id)
        
        try:
            result = dspy.Predict(ConversationSig)(user_utterance=user_input, conversation_history=history)
            ai_response = result.assistant_utterance
            is_directed_at_agent = result.is_directed_at_agent

            # Update conversation history
            new_messages = history.messages + [{"user_utterance": user_input, "assistant_utterance": ai_response}]
            if len(new_messages) > self.config.max_history:
                new_messages = new_messages[-self.config.max_history:]
            self.conversations[connection_id] = History(messages=new_messages)

            return ai_response, is_directed_at_agent
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error occurred: {str(e)[:50]}"
    
    def cleanup_connection(self, connection_id: str) -> None:
        """Clean up conversation history for a connection"""
        if connection_id in self.conversations:
            del self.conversations[connection_id] 