#!/usr/bin/env python3

import os
import dspy
import warnings
from dspy import History
import litellm
from typing import Optional, Tuple

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class ConversationSig(dspy.Signature):
    """
    You are a helpful voice assistant that can answer general questions conversationally.
    You respond with plain conversational text, no markdown or code or any special characters.
    Your responses should be in clear conversational style, so that it can be converted to speech without problems.
    """

    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    conversation_history: History = dspy.InputField(desc="Previous turns of the voice conversation.")
    assistant_utterance: str = dspy.OutputField(desc="How the assistant should speak back – plain conversational text, no markdown or code or special characters. Respond in short sentences and paragraphs. Maximum 3-4 sentences.")

class ClassificationSig(dspy.Signature):
    """
    Determine whether the user's utterance is directed at the agent or not.
    It is directed at the agent if it's a question or a non-ambigious request to the agent.
    If unsure return False.
    Only return True if the user's utterance is referencing something in the conversation history or a clear question that is non-ambiguous.
    """

    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    is_directed_at_agent: bool = dspy.OutputField(desc="Whether the user's utterance is directed at the agent.")
    is_directed_at_agent_reasoning: str = dspy.OutputField(desc="Reasoning about why the user's utterance is directed at the agent.")

class AIAgent:
    """AI Agent using DSPy framework for conversation and intent classification"""
    
    def __init__(self, 
                 model: Optional[str] = None, 
                 api_key: Optional[str] = None, 
                 max_history: int = 20,
                 temperature: float = 0.1,
                 max_tokens: int = 4000):
        """
        Initialize AI Agent with DSPy configuration
        
        Args:
            model: AI model identifier (from environment if not provided)
            api_key: API key for the model (from environment if not provided)
            max_history: Maximum number of conversation turns to remember
            temperature: Model temperature for response generation
            max_tokens: Maximum tokens for response generation
        """
        self.model = model or os.getenv("AI_MODEL")
        self.api_key = api_key or os.getenv("AI_API_KEY")
        self.max_history = max_history
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.model:
            raise ValueError("AI model must be specified via parameter or AI_MODEL environment variable")
        if not self.api_key:
            raise ValueError("API key must be specified via parameter or AI_API_KEY environment variable")
            
        print("Initializing DSPy with memory support...")
        dspy.configure(
            lm=dspy.LM(
                model=self.model,
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        )
        print("✅ DSPy ready!")

        # In-memory conversation history (dspy.History)
        self.history = History(messages=[])

    def classify_intent(self, user_input: str) -> Tuple[bool, str]:
        """
        Classify whether user input is directed at the agent
        
        Args:
            user_input: The user's utterance
            
        Returns:
            Tuple of (is_directed_at_agent, reasoning)
        """
        try:
            # Call model with current history
            result = dspy.Predict(ClassificationSig)(user_utterance=user_input)
            is_directed_at_agent = result.is_directed_at_agent

            return is_directed_at_agent, result.is_directed_at_agent_reasoning
        except Exception as e:
            print(f"❌ Error in intent classification: {e}")
            return False, f"Error occurred: {str(e)[:50]}"
        except litellm.exceptions.RateLimitError as e:
            print(f"❌ Rate limit error in classification: {e}")
            return False, "Error occurred: Rate Limit Exceeded"

    def generate_response(self, user_input: str) -> str:
        """
        Generate AI response using conversation history
        
        Args:
            user_input: The user's utterance
            
        Returns:
            AI response text
        """
        try:
            # Call model with current history
            result = dspy.Predict(ConversationSig)(user_utterance=user_input, conversation_history=self.history)
            ai_response = result.assistant_utterance

            # Build new history list respecting max turns (History is frozen)
            new_msgs = self.history.messages + [{"user_utterance": user_input, "assistant_utterance": ai_response}]
            if len(new_msgs) > self.max_history:
                new_msgs = new_msgs[-self.max_history:]
            self.history = History(messages=new_msgs)

            return ai_response
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error occurred: {str(e)[:50]}"
        except litellm.exceptions.RateLimitError as e:
            print(f"❌ Rate limit error in response generation: {e}")
            return "Error occurred: Rate Limit Exceeded"
            
    def get_conversation_history(self) -> History:
        """Get the current conversation history"""
        return self.history
        
    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.history = History(messages=[])
        
    def get_history_length(self) -> int:
        """Get the current length of conversation history"""
        return len(self.history.messages)
        
    def get_config(self) -> dict:
        """Get current agent configuration"""
        return {
            "model": self.model,
            "max_history": self.max_history,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "history_length": self.get_history_length()
        } 