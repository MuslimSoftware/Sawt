#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass
class AIConfig:
    """Configuration for AI agent"""
    model: str
    api_key: str
    temperature: float = 0.1
    max_tokens: int = 4000
    max_history: int = 20 