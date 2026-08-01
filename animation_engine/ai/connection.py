from pathlib import Path
import json
from .providers import AIProvider, GoogleAIProvider, LocalAIProvider

# ==============================
# MODEL CONFIGURATION
# ==============================

MODELS = {
    "google": {
        "director": "gemini-3.1-flash-lite",
        "engineer": "gemini-3.1-flash-lite"
    },
    "local": {
        "director": "Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M",
        "engineer": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"
    }
}

# Default provider configuration (maintained for compatibility)
DEFAULT_PROVIDER = "google"
GOOGLE_API_KEY = "AQ.Ab8RN6KGPYWSLWh2R-vR3x36l67SE7CPiNMqDkKQnd5fQayOHA"

class AIConnection:
    def __init__(self, provider: AIProvider | None = None):
        prompt_dir = Path(__file__).parent
        self.director_prompt = (prompt_dir / "DIRECTOR_PROMPT.md").read_text(encoding="utf-8")
        self.engineer_prompt = (prompt_dir / "ENGINEER_PROMPT.md").read_text(encoding="utf-8")
        
        self.provider = provider or GoogleAIProvider(GOOGLE_API_KEY)
        self.provider_type = "google" # Assuming google for default compatibility

    def _request(self, model: str, system_prompt: str, user_message: str) -> str:
        return self.provider.generate_content(model, system_prompt, user_message)

    def _clean_output(self, output: str) -> str:
        clean_output = output.strip()
        if clean_output.startswith("```"):
            clean_output = clean_output.split("\n", 1)[1] if "\n" in clean_output else clean_output.replace("```", "")
        if clean_output.endswith("```"):
            clean_output = clean_output[:-3]
        return clean_output.strip()

    def generate_plan(self, prompt: str) -> dict:
        model = MODELS[self.provider_type]["director"]
        output = self._request(model, self.director_prompt, prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def repair_plan(self, invalid_plan: dict, error: str) -> dict:
        request = f"Invalid AIPlan:\n{json.dumps(invalid_plan, indent=2)}\n\nEngine error:\n{error}\n\nReturn a corrected AIPlan JSON object only."
        model = MODELS[self.provider_type]["engineer"]
        output = self._request(model, self.engineer_prompt, request)
        return json.loads(self._clean_output(output))

    def generate_simple_scene_plan(self) -> dict:
        return self.generate_plan("Create a minute-ish scene plan, unleash your creativity.")