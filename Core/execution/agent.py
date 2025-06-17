#!/usr/bin/env python3

import os
import dspy
import warnings

# Suppress Pydantic serializer warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class AIAgent:
    def __init__(self):
        self.lm = None
        self._initialize_dspy()
    
    def _initialize_dspy(self):
        """Initialize DSPy with Gemini model"""
        print("Initializing DSPy...")
        try:
            self.lm = dspy.LM(
                model="gemini/gemini-2.0-flash-exp", 
                api_key=os.getenv("GEMINI_API_KEY"),
                max_tokens=4000,
                temperature=0.1
            )
            dspy.configure(lm=self.lm)
            print("✅ DSPy ready!")
        except Exception as e:
            print(f"❌ Failed to initialize DSPy: {e}")
            raise
    
    def generate_response(self, user_input: str) -> str:
        """Generate AI response for given input"""
        try:
            agent = dspy.Predict('input -> output')
            result = agent(input=user_input)
            return result.output
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Sorry, I couldn't process that request." 