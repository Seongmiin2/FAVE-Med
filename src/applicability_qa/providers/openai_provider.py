from __future__ import annotations

import json
import os
import time

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, temperature: float = 0, max_retries: int = 3):
        from openai import OpenAI

        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model, self.temperature, self.max_retries = model, temperature, max_retries

    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict | None = None) -> dict:
        started, last_error = time.perf_counter(), None
        for attempt in range(self.max_retries):
            try:
                response_format = {"type": "json_object"}
                if schema is not None:
                    response_format = {"type": "json_schema", "json_schema": {"name": "structured_response", "strict": True, "schema": schema}}
                response = self.client.chat.completions.create(model=self.model, temperature=self.temperature, response_format=response_format, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
                parsed = json.loads(response.choices[0].message.content or "{}")
                usage = response.usage
                parsed["usage"] = {"input_tokens": getattr(usage, "prompt_tokens", 0), "output_tokens": getattr(usage, "completion_tokens", 0), "latency_seconds": time.perf_counter() - started}
                return parsed
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self.max_retries:
                    time.sleep(2**attempt)
        raise RuntimeError(f"OpenAI generation failed after {self.max_retries} attempts") from last_error
