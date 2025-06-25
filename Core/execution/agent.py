#!/usr/bin/env python3

import os
import dspy
import warnings
from dspy import History
import litellm

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class ConversationSig(dspy.Signature):
    """Signature guiding the LM to produce natural spoken replies (no markdown)."""

    user_utterance: str = dspy.InputField(desc="What the user just said, as plain text from speech.")
    conversation_history: History = dspy.InputField(desc="Previous turns of the voice conversation.")
    assistant_utterance: str = dspy.OutputField(desc="How the assistant should speak back – plain conversational text, no markdown or code.")


class AIAgent:
    def __init__(self):
        print("Initializing DSPy with memory support...")
        dspy.configure(
            lm=dspy.LM(
                model="gemini/gemini-2.0-flash-exp",
                api_key=os.getenv("GEMINI_API_KEY"),
                max_tokens=4000,
                temperature=0.1,
            )
        )
        print("✅ DSPy ready!")

        # Initialize Predict module once
        self.predict_fn = dspy.Predict(ConversationSig)

        # In-memory conversation history (dspy.History)
        self.history = History(messages=[])
        self.max_history = 20  # keep last 20 turns

    def generate_response(self, user_input: str) -> str:
        """Generate AI response using DSPy.History for context."""
        try:
            # Call model with current history
            result = self.predict_fn(user_utterance=user_input, conversation_history=self.history)
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