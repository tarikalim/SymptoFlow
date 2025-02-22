from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "backend"
DATA_PATH = PROJECT_ROOT / "chatbot" / "data"
CONTENT_PATH = DATA_PATH / "content"
MAPPINGS_FILE = DATA_PATH / "mappings.json"


class PathConfig(BaseModel):
    data: Path
    content: Path
    mappings: Path

    def __init__(self):
        super().__init__(
            data=DATA_PATH,
            content=CONTENT_PATH,
            mappings=MAPPINGS_FILE,
        )

        if not self.content.exists():
            raise FileNotFoundError(f"Content directory does not exist at {self.content}")

        if not self.mappings.exists():
            print(f"Warning: Mappings file does not exist at {self.mappings}. It will be created later.")