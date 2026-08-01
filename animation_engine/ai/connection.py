from pathlib import Path
import json
from .providers import AIProvider, GoogleAIProvider, LocalAIProvider

# ==============================
# MODEL CONFIGURATION
# ==============================

import os
import json
from pathlib import Path
from .providers import AIProvider, GoogleAIProvider, LocalAIProvider

# Default provider configuration
DEFAULT_PROVIDER = "google"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or "AQ.Ab8RN6KGPYWSLWh2R-vR3x36l67SE7CPiNMqDkKQnd5fQayOHA"

def load_model_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "config" / "models.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

class AIConnection:
    def __init__(self, provider: AIProvider | None = None, provider_type: str = "google"):
        self.prompt_dir = Path(__file__).parent
        
        # Load prompts
        self.prompts = {
            "director": self._load_prompt("DIRECTOR_PROMPT.md"),
            "concept_director": self._load_prompt("CONCEPT_DIRECTOR_PROMPT.md"),
            "story_architect": self._load_prompt("STORY_ARCHITECT_PROMPT.md"),
            "visual_metaphor": self._load_prompt("VISUAL_METAPHOR_PROMPT.md"),
            "storyboard_artist": self._load_prompt("STORYBOARD_ARTIST_PROMPT.md"),
            "animation_planner": self._load_prompt("ANIMATION_PLANNER_PROMPT.md"),
            "schema_translator": self._load_prompt("SCHEMA_TRANSLATOR_PROMPT.md"),
            "engineer": self._load_prompt("ENGINEER_PROMPT.md"),
            "reviewer": self._load_prompt("REVIEWER_PROMPT.md"),
        }

        self.provider = provider or GoogleAIProvider(GOOGLE_API_KEY)
        self.provider_type = provider_type
        self.model_map = load_model_config()

    def _load_prompt(self, filename: str) -> str:
        prompt_path = self.prompt_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing required system prompt file: {prompt_path}")
        
        prompt_text = prompt_path.read_text(encoding="utf-8")
        
        if "{{ENGINE_CAPABILITIES}}" in prompt_text:
            capabilities_path = self.prompt_dir.parent / "engine" / "CAPABILITIES.md"
            if capabilities_path.exists():
                capabilities = capabilities_path.read_text(encoding="utf-8")
                prompt_text = prompt_text.replace("{{ENGINE_CAPABILITIES}}", capabilities)
            else:
                raise FileNotFoundError(f"Missing required engine capabilities file: {capabilities_path}")
        
        return prompt_text

    def _get_model(self, role: str) -> str:
        """Helper to get model based on role and provider type."""
        provider_config = self.model_map.get(self.provider_type, {})
        return provider_config.get(role, "default-model")

    def _request(self, model: str, system_prompt: str, user_message: str, retries: int = 3) -> str:
        import time
        for i in range(retries):
            try:
                output = self.provider.generate_content(model, system_prompt, user_message)
                print(f"\n--- AI OUTPUT START ---\n{output}\n--- AI OUTPUT END ---\n")
                return output
            except Exception as e:
                if i == retries - 1:
                    raise
                print(f"Request failed, retrying... ({i+1}/{retries})")
                time.sleep(2)
        return ""

    def _clean_output(self, output: str) -> str:
        """Robustly extract the first JSON object from the output."""
        output = output.strip()
        # Find the first '{' and the last '}'
        start = output.find('{')
        end = output.rfind('}')
        if start != -1 and end != -1:
            return output[start:end+1]
        return output

    def generate_narrative_structure(self, creative_brief: dict) -> dict:
        model = self._get_model("director")
        prompt = f"Transform this creative brief into a narrative structure:\n{json.dumps(creative_brief)}"
        output = self._request(model, self.prompts["story_architect"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def generate_visual_concept(self, narrative_structure: dict) -> dict:
        model = self._get_model("director")
        prompt = f"Transform this narrative structure into a visual concept:\n{json.dumps(narrative_structure)}"
        output = self._request(model, self.prompts["visual_metaphor"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def generate_storyboard(self, visual_concept: dict) -> dict:
        model = self._get_model("director")
        prompt = f"Transform this visual concept into a storyboard sequence:\n{json.dumps(visual_concept)}"
        output = self._request(model, self.prompts["storyboard_artist"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def generate_animation_plan(self, storyboard_sequence: dict) -> dict:
        model = self._get_model("director")
        prompt = f"Transform this storyboard sequence into an animation plan:\n{json.dumps(storyboard_sequence)}"
        output = self._request(model, self.prompts["animation_planner"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def translate_to_engine_schema(self, animation_plan: dict) -> dict:
        model = self._get_model("engineer")
        prompt = f"Translate this intermediate animation plan to engine Plan schema:\n{json.dumps(animation_plan)}"
        output = self._request(model, self.prompts["schema_translator"], prompt)
        clean_output = self._clean_output(output)

        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def repair_plan(self, invalid_plan: dict, error: str) -> dict:
        request = (
            f"Invalid AIPlan:\n{json.dumps(invalid_plan, indent=2)}\n\n"
            f"Engine error: {error}\n\n"
            "CRITICAL REPAIR RULES:\n"
            "1. Every `target_id` used in an action MUST exist in the `objects` list of that same scene.\n"
            "2. If an object is used in multiple scenes, you MUST re-define the object in each scene's `objects` list.\n"
            "3. DO NOT use 'scene' or 'canvas' as a `target_id`. If you need to perform an action on the whole scene (e.g., fade_out), define a Group or Rectangle object that covers the scene and target that object instead.\n"
            "Return a corrected Plan JSON object only."
        )
        model = self._get_model("engineer")
        output = self._request(model, self.prompts["engineer"], request)
        return json.loads(self._clean_output(output))

    def improve_plan(self, plan: dict, feedback: dict) -> dict:
        request = f"Improve this animation plan based on the provided feedback:\nPlan:\n{json.dumps(plan, indent=2)}\n\nFeedback:\n{json.dumps(feedback, indent=2)}\n\nReturn the improved AIPlan JSON object only."
        model = self._get_model("director")
        output = self._request(model, self.prompts["animation_planner"], request)
        return json.loads(self._clean_output(output))

    def review_plan(self, animation_plan: dict) -> dict:
        model = self._get_model("director")
        prompt = f"Review this animation plan:\n{json.dumps(animation_plan)}"
        output = self._request(model, self.prompts["reviewer"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}

    def generate_creative_brief(self, idea: str) -> dict:
        model = self._get_model("director")
        prompt = f"Transform this idea into a creative brief:\n{idea}"
        output = self._request(model, self.prompts["director"], prompt)
        clean_output = self._clean_output(output)
        
        try:
            return json.loads(clean_output)
        except json.JSONDecodeError:
            start, end = clean_output.find('{'), clean_output.rfind('}')
            return json.loads(clean_output[start:end+1]) if start != -1 and end != -1 else {}
