from typing import Dict, Optional, List

from openai.types.chat import ChatCompletionMessageParam
from openai import OpenAI


class TextGenerator:
    def __init__(self, model: str, key: str) -> None:
        self.client = None
        self.model = model
        self.key = key
        self._initialize_model()

    def _initialize_model(self) -> None:
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.key
        )

    def generate(self, history: List[ChatCompletionMessageParam]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=history,
            max_tokens=2048,
            temperature=0.7,
        )
        content = completion.choices[0].message.content
        return content