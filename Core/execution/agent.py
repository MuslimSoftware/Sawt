#!/usr/bin/env python3

import os
import dspy
import warnings
from dspy import History
import litellm

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class ConversationSig(dspy.Signature):
    """
    You are a helpful assistant that can answer questions and help with tasks.
    You are not a human, and do not have a personality.
    You do not respond with any special characters, only the alphabet.
    """

    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    conversation_history: History = dspy.InputField(desc="Previous turns of the voice conversation.")
    assistant_utterance: str = dspy.OutputField(desc="How the assistant should speak back – plain conversational text, no markdown or code.")

class ClassificationSig(dspy.Signature):
    """
    You are a helpful assistant that can classify whether the user's utterance is directed at the agent.
    The user's utterance is directed at the agent if it is making a request to the agent, either not referring to who the request is directed at or clearly referring to the agent.
    The user's utterance is not directed at the agent if it is not making a request to the agent, or if it is referring to someone else.
    The agent is a helpful assistant that can answer questions and help with tasks.
    """

    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    is_directed_at_agent: bool = dspy.OutputField(desc="Whether the user's utterance is directed at the agent.")
    is_directed_at_agent_reasoning: str = dspy.OutputField(desc="Reasoning about why the user's utterance is directed at the agent.")

class AIAgent:
    def __init__(self):
        print("Initializing DSPy with memory support...")
        dspy.configure(
            lm=dspy.LM(
                model=os.getenv("AI_MODEL"),
                api_key=os.getenv("AI_API_KEY"),
                max_tokens=4000,
                temperature=0.1,
            )
        )
        print("✅ DSPy ready!")

        # In-memory conversation history (dspy.History)
        self.history = History(messages=[])
        self.max_history = 20  # keep last 20 turns

    def get_classification_response(self, user_input: str) -> tuple[bool, str]:
        """Generate AI response using DSPy.History for context."""
        try:
            # Call model with current history
            result = dspy.Predict(ClassificationSig)(user_utterance=user_input)
            is_directed_at_agent = result.is_directed_at_agent

            return is_directed_at_agent, result.is_directed_at_agent_reasoning
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error Occured: {e.args[0][:10]}" 
        except litellm.exceptions.RateLimitError as e:
            print(f"❌ Rate limit error: {e}")
            return "Error Occured: Rate Limit Exceeded"

    def get_conversation_response(self, user_input: str) -> str:
        """Generate AI response using DSPy.History for context."""
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
            return f"Error Occured: {e.args[0][:10]}" 
        except litellm.exceptions.RateLimitError as e:
            print(f"❌ Rate limit error: {e}")
            return "Error Occured: Rate Limit Exceeded"