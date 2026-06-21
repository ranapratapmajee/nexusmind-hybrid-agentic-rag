# app/control/router.py

from typing import Dict, Any
from config.settings import get_settings

class ControlRouter:
    def __init__(self):
        self.settings = get_settings()

    def deterministic_route_check(self, query: str) -> str:
        """
        Runs a zero-token keyword check on the raw query text.
        Allows the system to fast-path specific intents before semantic evaluation.
        """
        query_lower = query.lower().strip().strip("?!.,")
        
        # 1. High-Priority Conversational / Greeting Intercept
        greetings = {
            "hi", "hello", "hey", "hola", "greetings", "yo", "sup",
            "good morning", "good afternoon", "good evening"
        }
        if query_lower in greetings:
            return "CASUAL_CHITCHAT"
        
        # 2. Immediate structural deterministic routing checks
        if any(w in query_lower for w in ["connect", "relationship", "map", "network", "ecosystem", "topology"]):
            return "GRAPH_SEARCH"
            
        if any(w in query_lower for w in ["latest", "recent", "current", "news", "update"]):
            return "WEB_SEARCH"
            
        return "DYNAMIC"

    def determine_compute_target(self, payload: Dict[str, Any]) -> str:
        """
        Evaluates the runtime context footprint to choose between local compute and cloud fallback.
        Keeps computation local on Apple Silicon unless high structural complexity triggers cloud reasoning.
        """
        complexity_tier = payload.get("complexity", "LOW")
        
        if complexity_tier == "HIGH":
            return "GEMINI_CLOUD"
            
        return "OLLAMA_LOCAL"
