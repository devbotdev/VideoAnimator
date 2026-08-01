from __future__ import annotations
from typing import Protocol
from abc import ABC, abstractmethod
from pathlib import Path
import json

# ==============================
# PROVIDER INTERFACE
# ==============================

class AIProvider(Protocol):
    """Protocol for interacting with different AI providers."""
    def generate_content(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2
    ) -> str:
        ...

# ==============================
# CONCRETE PROVIDERS
# ==============================

class GoogleAIProvider:
    def __init__(self, api_key: str):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def generate_content(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2
    ) -> str:
        prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER REQUEST:\n{user_message}\n\nReturn only valid JSON."
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": temperature,
                "response_mime_type": "application/json"
            }
        )
        return response.text

class LocalAIProvider:
    def __init__(self, base_url: str = "http://localhost:8080/", api_key: str = "local"):
        from openai import OpenAI
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def generate_content(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

# ==============================
# MOCK PROVIDER
# ==============================

class MockAIProvider:
    def __init__(self, responses: dict[str, str] = None):
        self.responses = responses or {}
        self.last_prompt = None

    def generate_content(self, model: str, system_prompt: str, user_message: str, temperature: float = 0.2) -> str:
        self.last_prompt = user_message
        return self.responses.get(user_message, "{}")
