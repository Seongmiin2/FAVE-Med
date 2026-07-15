from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict | None = None) -> dict:
        """Generate and return one parsed JSON object matching the requested schema."""
