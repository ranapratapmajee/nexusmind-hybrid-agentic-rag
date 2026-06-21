# app/services/llm_service.py

import json
import requests
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from config.settings import get_settings


# 1. Define a Pydantic schema for strict entity-relationship extraction output
class KnowledgeTriplet(BaseModel):
    source: str = Field(description="CONCEPT OR ENTITY, clear and short (1-4 words max)")
    relation: str = Field(description="VERB_OR_ACTION in UPPERCASE_WITH_UNDERSCORES")
    target: str = Field(description="CONCEPT OR ENTITY, clear and short (1-4 words max)")


class TripletExtractionContainer(BaseModel):
    triplets: list[KnowledgeTriplet]


class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        self.gemini_model = self.settings.gemini.model
        
        # Point to Ollama's local OpenAI-compatible routing path
        self.local_url = f"{self.settings.local_llm.base_url}/chat/completions"
        self.local_model = self.settings.local_llm.model
        
        # Cleaned Headers: Ollama runs locally on your Mac and does not expect any Authorization header
        self.local_headers = {
            "Content-Type": "application/json"
        }

    def extract_triplets_from_text(self, text_content: str) -> list[dict[str, str]]:
        """
        Uses Cloud LLM capabilities to parse raw text windows into clean 
        entity-relationship triplets using strict JSON schema enforcement.
        """
        system_instruction = (
            "You are an expert knowledge graph extraction engine. Analyze the provided text "
            "and extract core semantic relationships matching the requested schema."
        )

        try:
            # Leverage Gemini's strict native response configuration mapping
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=f"Text to analyze:\n{text_content}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=TripletExtractionContainer,
                    temperature=0.1
                )
            )
            
            # The payload response is guaranteed to conform strictly to our Pydantic schema rules
            raw_json_data = json.loads(response.text.strip())
            return raw_json_data.get("triplets", [])
            
        except Exception:
            # High-availability graceful fallback if network errors or api issues trigger
            return []

    def generate_local(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes your local Qwen2.5-Coder-7B-Instruct model via Ollama."""
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.local_model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            response = requests.post(self.local_url, json=payload, headers=self.local_headers, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return self.generate_cloud(
                prompt + f"\n\n[Fallback triggered: Local Ollama engine unreachable: {e}]", 
                system_instruction
            )

    def generate_cloud(self, prompt: str, system_instruction: str = None) -> str:
        """Invokes the cloud fallback Gemini-2.5-Flash system endpoint."""
        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction

        response = self.client.models.generate_content(
            model=self.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_args) if config_args else None
        )
        return response.text
