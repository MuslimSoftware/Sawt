#!/usr/bin/env python3

import os
import dspy
import warnings

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class AIAgent:
    def __init__(self):
        print("Initializing DSPy...")
        dspy.configure(
            lm=dspy.LM(
                model="gemini/gemini-2.0-flash-exp", 
                api_key=os.getenv("GEMINI_API_KEY"),
                max_tokens=4000,
                temperature=0.1
            )
        )
        print("✅ DSPy ready!")
    
    def generate_response(self, user_input: str) -> str:
        """Generate AI response for given input"""
        try:
            agent = dspy.Predict('speech_to_text -> text_to_speech')
            result = agent(speech_to_text=user_input)
            return result.text_to_speech
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Sorry, I couldn't process that request." 